from app import app
def test_simulation_controls():
 c=app.test_client(); assert c.post('/api/simulator/run',json={'mode':'RUNNING'}).status_code==200; assert c.post('/api/simulator/tick').status_code==200; assert c.post('/api/simulator/reset').status_code==200
