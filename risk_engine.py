def risk_score(pred):
    stock=0 if pred['current_stock']>=pred['safety_stock']*1.5 else 20 if pred['current_stock']>=pred['safety_stock'] else 45
    h=pred['shortage_hours']
    shortage=0 if h is None or h>120 else 20 if h>72 else 40 if h>48 else 100
    trend=min(20,max(0,(pred['trend_factor']-1)*100))
    convoy=min(15,pred['convoy_delay_hours']*2)
    weather=pred['weather']['impact_score']*.12
    score=round(min(100,stock*.20+shortage*.55+trend*.10+convoy*.05+weather*.10),1)
    level='LOW' if score<=25 else 'MEDIUM' if score<=50 else 'HIGH' if score<=75 else 'CRITICAL'
    return score,level
