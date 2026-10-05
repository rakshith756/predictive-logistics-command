from services.db import rows
def select_route(unit_id,resource='Fuel'):
 routes=rows('SELECT r.*,d.name origin,u.name destination FROM routes r JOIN depots d ON d.id=r.origin_id JOIN units u ON u.id=r.destination_unit_id WHERE r.destination_unit_id=? ORDER BY (r.risk_score+r.weather_impact)+r.eta_hours*5',(unit_id,))
 return routes[0] if routes else None
