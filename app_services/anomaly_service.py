import os, joblib, numpy as np, pandas as pd
from sklearn.ensemble import IsolationForest
from app.config import Config
from app_services.ingest_service import load_sample_df, get_realtime_snapshot
from app.utils import logger

ANOM_PATH = os.path.join(Config.MODELS_DIR, "anomaly_if.pkl")

def featurize_df(df):
    df = df.sort_values("timestamp")
    prices = df["price"].astype(float).values
    vols = df["volume"].astype(float).values if "volume" in df else np.zeros(len(prices))
    ret1 = np.concatenate([[0], (prices[1:]-prices[:-1]) / (prices[:-1] + 1e-9)])
    vol_ma5 = pd.Series(vols).rolling(5).mean().fillna(vols.mean()).values
    price_std5 = pd.Series(prices).rolling(5).std().fillna(prices.std()).values
    X = np.vstack([ret1, vol_ma5, price_std5]).T
    return X

def train_iforest(symbol="BTC"):
    df = load_sample_df()
    df = df[df["symbol"]==symbol].sort_values("timestamp")
    if len(df) < 200:
        logger.warning("not enough data to train anomaly model")
        return False
    X = featurize_df(df)
    clf = IsolationForest(n_estimators=200, contamination=0.01, random_state=42)
    clf.fit(X)
    joblib.dump(clf, ANOM_PATH)
    logger.info("Anomaly model trained & saved")
    return True

def _load_iforest():
    if not os.path.exists(ANOM_PATH):
        train_iforest()
    return joblib.load(ANOM_PATH)

def detect_anomaly_single(payload):
    # single tick
    if payload and "price" in payload and "volume" in payload:
        clf = _load_iforest()
        price = float(payload["price"]); vol = float(payload["volume"])
        # crude features
        feat = np.array([[0.0, vol, max(1.0, vol / max(price, 1.0))]])
        score = float(clf.decision_function(feat)[0])
        is_anom = int(clf.predict(feat)[0] == -1)
        return {"score": score, "is_anomaly": bool(is_anom)}
    # batch / buffer
    rows = get_realtime_snapshot(500)
    if not rows:
        return {"flags": []}
    df = pd.DataFrame(rows)
    X = featurize_df(df)
    clf = _load_iforest()
    preds = clf.predict(X)
    df["anomaly"] = (preds == -1).astype(int)
    flags = df[df["anomaly"]==1][["timestamp","symbol","price","volume"]].to_dict(orient="records")
    return {"flags": flags}
