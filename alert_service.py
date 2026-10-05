from datetime import datetime
from services.db import get_db, rows
from models.prediction_engine import PredictionEngine
from models.risk_engine import risk_score

def refresh_alerts(db):
    with get_db() as c:
        for u in c.execute('SELECT id,name FROM units').fetchall():
            for inv in c.execute('SELECT * FROM inventory WHERE unit_id=?',(u['id'],)).fetchall():
                if inv['available'] < inv['safety_stock']:
                    exists=c.execute("SELECT 1 FROM alerts WHERE unit_id=? AND resource=? AND status='ACTIVE' AND reason LIKE 'Current stock%'",(u['id'],inv['resource'])).fetchone()
                    if not exists: c.execute("INSERT INTO alerts(timestamp,severity,unit_id,resource,reason,action,status) VALUES (?,?,?,?,?,?,?)",(datetime.now().isoformat(),'CRITICAL',u['id'],inv['resource'],'Current stock is below safety stock','Initiate synthetic resupply planning','ACTIVE'))
            for r in c.execute('SELECT resource FROM inventory WHERE unit_id=?',(u['id'],)).fetchall():
                p=PredictionEngine(db).predict(u['id'],r['resource']); score,level=risk_score(p)
                if p['shortage_hours'] is not None and p['shortage_hours']<48:
                    exists=c.execute("SELECT 1 FROM alerts WHERE unit_id=? AND resource=? AND status='ACTIVE' AND reason LIKE 'Predictive shortage%'",(u['id'],r['resource'])).fetchone()
                    if not exists: c.execute("INSERT INTO alerts(timestamp,severity,unit_id,resource,reason,action,status) VALUES (?,?,?,?,?,?,?)",(datetime.now().isoformat(),'CRITICAL' if level=='CRITICAL' else 'HIGH',u['id'],r['resource'],f'Predictive shortage within {p["shortage_hours"]:.0f} hours','Review recommendation and simulate resupply','ACTIVE'))
        c.commit()
    return rows("SELECT a.*,u.name unit_name FROM alerts a LEFT JOIN units u ON u.id=a.unit_id ORDER BY a.id DESC")
