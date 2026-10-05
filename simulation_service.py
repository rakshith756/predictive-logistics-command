from datetime import datetime
from services.db import get_db

def set_state(running=None,mode=None,tick=None):
 with get_db() as c:
  s=c.execute('SELECT * FROM simulation_state WHERE id=1').fetchone(); vals=[s['running'],s['mode'],s['tick']]
  if running is not None: vals[0]=int(running)
  if mode is not None: vals[1]=mode
  if tick is not None: vals[2]=tick
  c.execute('UPDATE simulation_state SET running=?,mode=?,tick=?,updated_at=? WHERE id=1',(*vals,datetime.now().isoformat())); c.commit()
  return dict(c.execute('SELECT * FROM simulation_state WHERE id=1').fetchone())

def apply_resupply(unit_id,resource,quantity):
 with get_db() as c:
  c.execute('UPDATE inventory SET available=available+? WHERE unit_id=? AND resource=?',(max(0,float(quantity)),unit_id,resource))
  c.execute("UPDATE alerts SET status='RESOLVED' WHERE unit_id=? AND resource=? AND status='ACTIVE'",(unit_id,resource)); c.commit()
 return set_state(mode='RESUPPLY_APPLIED')

def tick():
 with get_db() as c:
  c.execute('UPDATE inventory SET available=MAX(0,available-daily_consumption/24.0)')
  c.execute('UPDATE simulation_state SET tick=tick+1,updated_at=?',(datetime.now().isoformat(),)); c.commit()
 return set_state()
