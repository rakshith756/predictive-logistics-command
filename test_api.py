from app import app
def test_api_endpoints():
 c=app.test_client()
 for path in ['/api/dashboard','/api/units','/api/inventory','/api/convoys','/api/prediction/3/Fuel','/api/analytics']:
  r=c.get(path); assert r.status_code==200, path

def test_ack_and_resupply():
 c=app.test_client(); a=c.get('/api/alerts').get_json();
 if a: assert c.post(f"/api/alerts/{a[0]['id']}/acknowledge").status_code==200
 assert c.post('/api/resupply',json={'unit_id':3,'resource':'Fuel','quantity':100}).status_code==200
