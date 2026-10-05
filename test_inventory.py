from services.inventory_service import inventory
def test_inventory_days_and_status():
 d=inventory(3); assert len(d)==5; assert all('days_remaining' in x and x['status'] in ('HEALTHY','LOW','CRITICAL') for x in d)
