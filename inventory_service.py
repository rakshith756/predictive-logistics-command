from services.db import rows
def inventory(unit_id=None):
    q='SELECT i.*,u.name unit_name FROM inventory i JOIN units u ON u.id=i.unit_id'; args=()
    if unit_id: q+=' WHERE i.unit_id=?'; args=(unit_id,)
    out=rows(q,args)
    for x in out:
        x['days_remaining']=round(x['available']/x['daily_consumption'],1) if x['daily_consumption'] else 999
        x['status']='CRITICAL' if x['available']<x['safety_stock'] else 'LOW' if x['available']<x['required'] else 'HEALTHY'
        x['availability_pct']=round(min(100,x['available']/max(x['required'],1)*100),1)
    return out
