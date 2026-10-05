import sqlite3, math
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

class PredictionEngine:
    def __init__(self, db): self.db=db
    def predict(self, unit_id, resource):
        con=sqlite3.connect(self.db); con.row_factory=sqlite3.Row
        inv=con.execute('SELECT * FROM inventory WHERE unit_id=? AND resource=?',(unit_id,resource)).fetchone()
        hist=con.execute('SELECT day,quantity FROM consumption_history WHERE unit_id=? AND resource=? ORDER BY day',(unit_id,resource)).fetchall()
        conv=con.execute("SELECT COALESCE(SUM(quantity),0) q, COALESCE(MAX(delay_hours),0) d FROM convoys WHERE destination_unit_id=? AND cargo=? AND status NOT IN ('ARRIVED','RESOLVED')",(unit_id,resource)).fetchone()
        weather=con.execute('SELECT w.* FROM weather w JOIN units u ON u.weather_id=w.id WHERE u.id=?',(unit_id,)).fetchone()
        con.close()
        if not inv or not hist: raise ValueError('Prediction inputs unavailable')
        y=np.array([r['quantity'] for r in hist],dtype=float); X=np.arange(len(y)).reshape(-1,1)
        model=LinearRegression().fit(X,y)
        pred=max(float(model.predict([[len(y)+i]])[0]) for i in [0,1])
        baseline=float(y.mean()); trend=max(0.5,pred/baseline if baseline else 1)
        future=pred*(1+max(0,weather['impact_score']-40)/1000)
        incoming=float(conv['q']); delay=float(conv['d'])
        effective=future
        days=(float(inv['available'])-float(inv['safety_stock']))/effective if effective else 999
        raw_shortage_days=(float(inv['available'])-float(inv['safety_stock']))/effective if effective else 999
        shortage_hours=max(0,raw_shortage_days*24) if raw_shortage_days<30 else None
        mae=float(mean_absolute_error(y[1:], model.predict(X[1:]))) if len(y)>2 else 0
        r2=float(r2_score(y,model.predict(X))) if len(y)>2 else 0
        confidence=float(np.clip(100-(mae/max(baseline,1))*100,45,98))
        reasons=[]
        if trend>1.08: reasons.append(f'Recent consumption trend is {((trend-1)*100):.0f}% above baseline')
        if float(inv['available'])<float(inv['required']): reasons.append('Current stock is below required planning level')
        if float(inv['available'])<=float(inv['safety_stock'])*1.25: reasons.append('Current stock is approaching safety stock')
        if delay>0: reasons.append(f'Incoming supply has an estimated {delay:.1f}h delay')
        if weather['impact']=='HIGH': reasons.append('Synthetic weather impact is elevated')
        if not reasons: reasons.append('Inventory and demand remain within planned buffers')
        return {'unit_id':unit_id,'resource':resource,'current_stock':round(inv['available'],1),'safety_stock':round(inv['safety_stock'],1),'predicted_daily':round(effective,1),'historical_average':round(baseline,1),'trend_factor':round(trend,3),'incoming_supply':round(incoming,1),'convoy_delay_hours':round(delay,1),'days_to_safety':round(max(0,days),2),'shortage_hours':round(shortage_hours,1) if shortage_hours is not None else None,'risk_score_hint':round(np.clip(100-(shortage_hours or 999)/48*50 + max(0,trend-1)*100 + weather['impact_score']*.15,0,100),1),'confidence':round(confidence,1),'mae':round(mae,2),'r2':round(r2,3),'model':'Linear Regression','weather':dict(weather),'explanation':reasons,'prototype_note':'Prototype estimate based on synthetic historical data.'}
