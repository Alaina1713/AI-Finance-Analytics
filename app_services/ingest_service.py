import os, random
import pandas as pd
from datetime import datetime
from app.models import db, MarketTick
from app.config import Config
from app.utils import logger

CSV_PATH = os.path.join(Config.DATA_DIR, "sample_market.csv")

def _create_sample_csv():
    # create a basic sample CSV with 1000 minutes of BTC ticks
    import numpy as np
    logger.info("creating sample_market.csv")
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    times = pd.date_range(end=pd.Timestamp.utcnow(), periods=1000, freq='T')
    prices = 40000 + (pd.Series(range(1000)).apply(lambda x: random.uniform(-50,50))).cumsum()
    volumes = [random.randint(1,500) for _ in range(1000)]
    df = pd.DataFrame({"timestamp": times, "symbol": ["BTC"]*1000, "price": prices.values, "volume": volumes})
    df.to_csv(CSV_PATH, index=False)
    return df

def load_sample_df():
    if not os.path.exists(CSV_PATH):
        return _create_sample_csv()
    return pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

def seed_db_from_csv(n=500):
    df = load_sample_df().sort_values("timestamp")
    rows = []
    for _, r in df.tail(n).iterrows():
        tick = MarketTick(symbol=r["symbol"], price=float(r["price"]), volume=int(r["volume"]), timestamp=r["timestamp"].to_pydatetime())
        db.session.add(tick)
        rows.append(tick)
    db.session.commit()
    logger.info(f"seeded {len(rows)} ticks")
    return rows

def get_realtime_snapshot(n=50):
    rows = MarketTick.query.order_by(MarketTick.id.desc()).limit(n).all()
    return [r.to_dict() for r in reversed(rows)]

def simulate_tick(symbol="BTC"):
    # small random walk based on last DB price
    last = MarketTick.query.order_by(MarketTick.id.desc()).first()
    last_price = last.price if last else 40000.0
    new_price = round(last_price * random.uniform(0.999, 1.002), 2)
    tick = MarketTick(symbol=symbol, price=new_price, volume=random.randint(1,200), timestamp=datetime.utcnow())
    db.session.add(tick)
    db.session.commit()
    logger.info(f"simulated tick {symbol} {new_price}")
    return tick.to_dict()
