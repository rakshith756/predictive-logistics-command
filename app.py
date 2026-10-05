from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from config import SECRET_KEY, DATABASE_PATH
from database.seed import seed
from services.db import rows,row,get_db
from services.inventory_service import inventory
from services.convoy_service import convoys
from services.alert_service import refresh_alerts
from services.weather_service import get_weather
from services.simulation_service import set_state,apply_resupply,tick
from models.prediction_engine import PredictionEngine
from models.risk_engine import risk_score
from models.recommendation_engine import recommend
from models.route_engine import select_route
from datetime import datetime
import sqlite3

app=Flask(__name__); app.secret_key=SECRET_KEY; CORS(app)
try:
    if not row('SELECT id FROM simulation_state WHERE id=1'): seed()
except sqlite3.OperationalError: seed()

def enrich_prediction(unit_id,resource):
 p=PredictionEngine(DATABASE_PATH).predict(unit_id,resource); score,level=risk_score(p); p['risk_score']=score; p['risk_level']=level; p['recommendation']=recommend(p); p['route']=select_route(unit_id,resource); return p

@app.context_processor
def globals(): return {'now':datetime.now}
@app.route('/')
def dashboard(): return render_template('dashboard.html',page='dashboard')
@app.route('/<page>')
def pages(page):
 allowed={'map','inventory','units','convoys','prediction','analytics','alerts','simulator'}
 if page not in allowed: return render_template('dashboard.html',page='dashboard')
 return render_template(f'{page}.html',page=page)
@app.get('/api/dashboard')
def api_dashboard():
 refresh_alerts(DATABASE_PATH)
 inv=inventory(); units=rows('SELECT * FROM units'); cvs=convoys(); alerts=rows("SELECT * FROM alerts WHERE status='ACTIVE'")
 risks=[]
 for u in units:
  p=enrich_prediction(u['id'],'Fuel'); risks.append(p['risk_score'])
 inv_health=sum(min(100,x['availability_pct']) for x in inv)/len(inv)
 convoy_pen=sum(min(10,c['delay_hours']*2) for c in cvs)/max(len(cvs),1)
 risk_pen=sum(risks)/max(len(risks),1)*.45
 health=round(max(0,min(100,inv_health*.45+(100-risk_pen)*.4+(100-convoy_pen)*.15)),1)
 resources=[]
 for r in ['Fuel','Food','Water','Medical','Spare Parts']:
  a=[x for x in inv if x['resource']==r]; resources.append({'resource':r,'availability':round(sum(x['available'] for x in a)/max(sum(x['required'] for x in a),1)*100,1)})
 return jsonify({'kpis':{'units':len(units),'availability':round(inv_health,1),'active_convoys':sum(c['status'] not in ['ARRIVED'] for c in cvs),'low_stock':sum(x['status']!='HEALTHY' for x in inv),'high_risk':sum(r>50 for r in risks),'critical_alerts':sum(a['severity']=='CRITICAL' for a in alerts)},'health_score':health,'health_label':'STABLE' if health>=70 else 'WATCH' if health>=50 else 'CRITICAL','resources':resources,'risk_focus':enrich_prediction(3,'Fuel'),'alerts':alerts[:6],'updated_at':datetime.now().isoformat()})
@app.get('/api/units')
def api_units():
 out=[]
 for u in rows('SELECT * FROM units'):
  invs=inventory(u['id']); p=enrich_prediction(u['id'],'Fuel'); u.update({'inventory_health':round(sum(x['availability_pct'] for x in invs)/len(invs),1),'risk_score':p['risk_score'],'risk_level':p['risk_level'],'prediction':p}); out.append(u)
 return jsonify(out)
@app.get('/api/units/<int:uid>')
def api_unit(uid):
 u=row('SELECT * FROM units WHERE id=?',(uid,));
 if not u:return jsonify({'error':'Unit not found'}),404
 u['inventory']=inventory(uid); u['weather']=get_weather(uid); u['predictions']=[enrich_prediction(uid,r) for r in ['Fuel','Food','Water','Medical','Spare Parts']]; u['convoys']=rows('SELECT c.*,d.name origin FROM convoys c JOIN depots d ON d.id=c.origin_id WHERE destination_unit_id=?',(uid,)); return jsonify(u)
@app.get('/api/inventory')
def api_inventory(): return jsonify(inventory(request.args.get('unit_id',type=int)))
@app.get('/api/convoys')
def api_convoys(): return jsonify(convoys())
@app.get('/api/depots')
def api_depots(): return jsonify(rows('SELECT * FROM depots'))
@app.get('/api/routes')
def api_routes(): return jsonify(rows('SELECT r.*,d.name origin,u.name destination FROM routes r JOIN depots d ON d.id=r.origin_id JOIN units u ON u.id=r.destination_unit_id'))
@app.get('/api/weather')
def api_weather(): return jsonify(rows('SELECT * FROM weather'))
@app.get('/api/alerts')
def api_alerts(): return jsonify(refresh_alerts(DATABASE_PATH))
@app.post('/api/alerts/<int:aid>/acknowledge')
def ack(aid):
 with get_db() as c:
  if not c.execute('SELECT id FROM alerts WHERE id=?',(aid,)).fetchone(): return jsonify({'error':'Alert not found'}),404
  c.execute("UPDATE alerts SET status='ACKNOWLEDGED' WHERE id=?",(aid,)); c.commit()
 return jsonify({'ok':True})
@app.get('/api/prediction/<int:uid>/<resource>')
def api_prediction(uid,resource):
 try:return jsonify(enrich_prediction(uid,resource.replace('_',' ').title()))
 except ValueError as e:return jsonify({'error':str(e)}),404
@app.get('/api/analytics')
def api_analytics():
 history=rows("SELECT resource,day,ROUND(SUM(quantity),1) quantity FROM consumption_history GROUP BY resource,day ORDER BY day")
 risk=[]
 for u in rows('SELECT id,name FROM units'):
  p=enrich_prediction(u['id'],'Fuel'); risk.append({'unit':u['name'],'score':p['risk_score'],'level':p['risk_level']})
 delays=rows('SELECT convoy_id,delay_hours,status FROM convoys ORDER BY id')
 return jsonify({'consumption':history,'risk':risk,'delays':delays,'inventory':inventory(),'health':[{'label':'Current','score':api_dashboard().json['health_score']}],'shortages':[enrich_prediction(u['id'],'Fuel') for u in rows('SELECT id FROM units') if enrich_prediction(u['id'],'Fuel')['shortage_hours'] is not None]})
@app.post('/api/simulator/run')
def sim_run():
 data=request.get_json(silent=True) or {}; mode=data.get('mode','RUNNING'); state=set_state(running=mode=='RUNNING',mode=mode); return jsonify(state)
@app.post('/api/simulator/tick')
def sim_tick(): return jsonify(tick())
@app.post('/api/simulator/reset')
def sim_reset():
 seed(); return jsonify(set_state(running=False,mode='RESET',tick=0))
@app.post('/api/resupply')
def resupply():
 data=request.get_json(silent=True) or {}
 if not all(k in data for k in ('unit_id','resource','quantity')): return jsonify({'error':'unit_id, resource and quantity required'}),400
 return jsonify({'state':apply_resupply(int(data['unit_id']),str(data['resource']),float(data['quantity'])),'prediction':enrich_prediction(int(data['unit_id']),str(data['resource']))})
@app.get('/api/demo/status')
def demo_status(): return jsonify({'state':row('SELECT * FROM simulation_state WHERE id=1')})
@app.post('/api/demo/start')
def demo_start(): return jsonify({'unit_id':3,'resource':'Fuel','prediction':enrich_prediction(3,'Fuel'),'message':'SIH DEMONSTRATION STARTING'})

if __name__=='__main__': app.run(host='0.0.0.0',port=5000,debug=False)
