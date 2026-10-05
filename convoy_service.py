from services.db import rows
def convoys():
 return rows('SELECT c.*,d.name origin,u.name destination FROM convoys c JOIN depots d ON d.id=c.origin_id JOIN units u ON u.id=c.destination_unit_id ORDER BY c.id DESC')
