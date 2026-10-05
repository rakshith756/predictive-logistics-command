from models.prediction_engine import PredictionEngine
from models.risk_engine import risk_score
from models.recommendation_engine import recommend
from config import DATABASE_PATH

def test_charlie_fuel_prediction():
 p=PredictionEngine(DATABASE_PATH).predict(3,'Fuel'); assert p['predicted_daily']>0; assert p['current_stock']==1200; assert p['shortage_hours'] is not None

def test_risk_levels():
 base={'current_stock':2000,'safety_stock':500,'predicted_daily':500,'historical_average':500,'trend_factor':1,'incoming_supply':0,'convoy_delay_hours':0,'shortage_hours':200,'weather':{'impact_score':0}}
 assert risk_score(base)[1]=='LOW'; base['shortage_hours']=30; assert risk_score(base)[1] in ('HIGH','CRITICAL')

def test_recommendation_nonnegative():
 p=PredictionEngine(DATABASE_PATH).predict(3,'Fuel'); assert recommend(p)['quantity']>=0
