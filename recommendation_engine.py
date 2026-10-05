def recommend(pred, planning_horizon=6.0):
    required=pred['predicted_daily']*planning_horizon+pred['safety_stock']
    qty=max(0,required-pred['current_stock']-pred['incoming_supply'])
    return {'quantity':round(qty/50)*50,'planning_horizon_days':planning_horizon,'required_stock':round(required,1),'reason':'Cover forecast demand across the planning horizon while restoring the safety buffer.'}
