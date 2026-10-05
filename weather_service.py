from services.db import row
def get_weather(unit_id):
    r=row('SELECT w.* FROM weather w JOIN units u ON u.weather_id=w.id WHERE u.id=?',(unit_id,))
    return r or {'condition':'Synthetic fallback','temperature':22,'impact':'MEDIUM','impact_score':35}
