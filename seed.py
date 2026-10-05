from pathlib import Path
import sqlite3, math
from datetime import datetime, timedelta
import numpy as np

BASE=Path(__file__).resolve().parent
DB=BASE/'database'/'logistics.db'
SCHEMA=(BASE/'database'/'schema.sql').read_text()
RES=[('Fuel','Energy','L'),('Food','Rations','kg'),('Water','Water','L'),('Medical','Medical','packs'),('Spare Parts','Maintenance','units')]
UNITS=[
(1,'UNIT ALPHA','Sector North',15.20,76.15,420,1),(2,'UNIT BRAVO','Sector East',15.25,76.28,390,2),(3,'UNIT CHARLIE','Sector Central',15.12,76.30,480,3),(4,'UNIT DELTA','Sector West',15.08,76.05,360,4),(5,'UNIT ECHO','Sector Ridge',15.32,76.08,510,5),(6,'UNIT FOXTROT','Sector South',14.98,76.24,440,6),(7,'UNIT GOLF','Sector Valley',15.40,76.32,310,7),(8,'UNIT HOTEL','Sector Plain',15.00,76.02,280,8)]
WEATHER=[(1,'Sector North','Clear',26,'LOW',10),(2,'Sector East','Cloudy',22,'MEDIUM',35),(3,'Sector Central','Heavy Rain',18,'HIGH',75),(4,'Sector West','Clear',25,'LOW',12),(5,'Sector Ridge','Windy',20,'MEDIUM',45),(6,'Sector South','Light Rain',21,'MEDIUM',40),(7,'Sector Valley','Clear',24,'LOW',8),(8,'Sector Plain','Cloudy',23,'LOW',25)]
DEPOTS=[(1,'DEPOT A',14.92,76.18,18000,16000,22000,2600,4200),(2,'DEPOT B',15.05,76.12,9200,21000,18000,3100,5000),(3,'DEPOT C',15.48,76.38,25000,12000,26000,1800,7000),(4,'DEPOT D',14.88,76.36,14500,19000,15000,4200,3500)]
now=datetime.now()

def seed():
 DB.parent.mkdir(exist_ok=True)
 con=sqlite3.connect(DB); con.execute('PRAGMA foreign_keys=ON'); con.executescript(SCHEMA)
 for t in ['predictions','alerts','convoys','routes','consumption_history','inventory','weather','depots','units','simulation_state']: con.execute(f'DELETE FROM {t}')
 con.executemany('INSERT INTO units VALUES (?,?,?,?,?,?,?)',UNITS)
 con.executemany('INSERT INTO weather VALUES (?,?,?,?,?,?,?)',[(i,l,c,t,imp,s,(now-timedelta(hours=2)).isoformat()) for i,l,c,t,imp,s in WEATHER])
 con.executemany('INSERT INTO depots VALUES (?,?,?,?,?,?,?,?,?)',DEPOTS)
 # inventory designed around a coherent Charlie fuel shortage story
 rows=[]
 base={
 'Fuel':(1200,1800,500,720), 'Food':(5200,6000,1800,520), 'Water':(10500,12000,3500,1050), 'Medical':(850,1200,400,65), 'Spare Parts':(310,450,120,22)}
 for uid,*_ in UNITS:
  for r,c,u in RES:
   av,req,safe,d=base[r]
   factor={1:1.05,2:.95,3:1,4:.82,5:1.12,6:.9,7:.7,8:.65}[uid]
   if uid!=3: av*=factor; req*=factor; safe*=factor; d*=factor
   rows.append((uid,r,c,u,round(av,1),round(req,1),round(safe,1),round(d,1)))
 con.executemany('INSERT INTO inventory(unit_id,resource,category,unit,available,required,safety_stock,daily_consumption) VALUES (?,?,?,?,?,?,?,?)',rows)
 # 30 days history, with Charlie fuel upward trend
 h=[]
 for uid,*_ in UNITS:
  for r,_,_ in RES:
   base_daily=next(x[7] for x in rows if x[0]==uid and x[1]==r)
   for i in range(30):
    trend=1+(i/29*.22 if uid==3 and r=='Fuel' else 0.03*math.sin(i/3))
    noise=np.random.default_rng(uid*100+i).normal(0,.025)
    q=max(.1,base_daily*trend*(1+noise))
    h.append((uid,r,(now-timedelta(days=29-i)).date().isoformat(),round(q,2)))
 con.executemany('INSERT INTO consumption_history(unit_id,resource,day,quantity) VALUES (?,?,?,?)',h)
 routes=[(1,'ROUTE-A',1,3,142,4.33,18,10,'AVAILABLE'),(2,'ROUTE-B',2,3,87,3.83,68,75,'AVAILABLE'),(3,'ROUTE-C',3,3,118,3.95,52,75,'AVAILABLE'),(4,'ROUTE-D',4,3,165,4.75,32,25,'AVAILABLE'),(5,'ROUTE-E',1,1,95,2.8,15,10,'AVAILABLE'),(6,'ROUTE-F',3,2,102,3.1,28,35,'AVAILABLE')]
 con.executemany('INSERT INTO routes VALUES (?,?,?,?,?,?,?,?,?)',routes)
 conv=[(1,'CON-021',2,3,'Fuel',2500,(now-timedelta(hours=1)).isoformat(),(now+timedelta(hours=3.75)).isoformat(),'DELAYED',4.0,72),(2,'CON-022',1,2,'Food',3200,(now-timedelta(hours=2)).isoformat(),(now+timedelta(hours=2)).isoformat(),'ON ROUTE',0,30),(3,'CON-023',3,5,'Water',5000,(now-timedelta(hours=1)).isoformat(),(now+timedelta(hours=4)).isoformat(),'DEPARTED',0,25),(4,'CON-024',4,6,'Medical',900,(now-timedelta(hours=3)).isoformat(),(now+timedelta(hours=2)).isoformat(),'ON ROUTE',0,35),(5,'CON-025',1,4,'Fuel',1800,now.isoformat(),(now+timedelta(hours=3)).isoformat(),'PLANNED',0,20),(6,'CON-026',2,8,'Food',1600,now.isoformat(),(now+timedelta(hours=3.2)).isoformat(),'LOADING',0,18),(7,'CON-027',3,7,'Spare Parts',500,now.isoformat(),(now+timedelta(hours=2.5)).isoformat(),'PLANNED',0,15),(8,'CON-028',4,1,'Fuel',2200,now.isoformat(),(now+timedelta(hours=2.8)).isoformat(),'ON ROUTE',0,22),(9,'CON-029',1,5,'Water',4300,now.isoformat(),(now+timedelta(hours=3.1)).isoformat(),'DEPARTED',0,25),(10,'CON-030',2,6,'Food',2500,now.isoformat(),(now+timedelta(hours=3.5)).isoformat(),'ON ROUTE',0,30)]
 con.executemany('INSERT INTO convoys VALUES (?,?,?,?,?,?,?,?,?,?,?)',conv)
 con.execute("INSERT INTO simulation_state VALUES (1,0,0,'IDLE',NULL,?)",(now.isoformat(),))
 con.commit(); con.close()

if __name__=='__main__': seed(); print(DB)
