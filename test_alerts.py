from services.alert_service import refresh_alerts
from config import DATABASE_PATH
from services.db import get_db
def test_alert_generation_and_ack():
 a=refresh_alerts(DATABASE_PATH); assert len(a)>0
 x=a[0]
 with get_db() as c: c.execute("UPDATE alerts SET status='ACKNOWLEDGED' WHERE id=?",(x['id'],)); c.commit()
