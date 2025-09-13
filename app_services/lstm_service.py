import os, joblib, numpy as np
from app.config import Config
from app_services.ingest_service import load_sample_df, get_realtime_snapshot
from app.utils import logger

MODEL_FILE = os.path.join(Config.MODELS_DIR, "price_lstm.h5")
SCALER_FILE = os.path.join(Config.MODELS_DIR, "price_scaler.pkl")

# This module will attempt to use TensorFlow if present; otherwise fallback to a simple predictor.
try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False
    logger.info("TensorFlow not available — LSTM will fallback to naive predictor")

def train_lstm_from_csv(symbol="BTC", lookback=20, epochs=3):
    if not TF_AVAILABLE:
        logger.info("train_lstm skipped: TensorFlow not installed")
        return False
    df = load_sample_df()
    df = df[df["symbol"]==symbol].sort_values("timestamp")
    prices = df["price"].astype(float).values
    mean, std = prices.mean(), prices.std() if prices.std() != 0 else 1.0
    norm = (prices - mean)/std
    X, y = [], []
    for i in range(lookback, len(norm)):
        X.append(norm[i-lookback:i])
        y.append(norm[i])
    X = np.array(X).reshape(-1, lookback, 1)
    y = np.array(y)
    model = Sequential([LSTM(64, input_shape=(lookback,1)), Dense(1)])
    model.compile("adam", "mse")
    model.fit(X, y, epochs=epochs, batch_size=32, verbose=0)
    model.save(MODEL_FILE)
    joblib.dump({"mean": mean, "std": std, "lookback": lookback}, SCALER_FILE)
    logger.info("LSTM trained and saved")
    return True

def predict_price_single(payload):
    # supports {"window":[...]} or {"current_price":float}
    if "window" in payload:
        arr = np.array(payload["window"], dtype=float)
        if TF_AVAILABLE and os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
            model = load_model(MODEL_FILE)
            meta = joblib.load(SCALER_FILE)
            lookback = meta["lookback"]
            if len(arr) != lookback:
                if len(arr) < lookback:
                    arr = np.concatenate([np.repeat(arr[0], lookback-len(arr)), arr])
                else:
                    arr = arr[-lookback:]
            norm = (arr - meta["mean"]) / meta["std"]
            x = norm.reshape(1, lookback, 1)
            pred_norm = model.predict(x)[0][0]
            pred = pred_norm*meta["std"] + meta["mean"]
            return float(round(pred, 4))
        else:
            # naive average + small jitter
            return float(round(arr.mean() * np.random.uniform(0.997, 1.003), 4))
    if "current_price" in payload:
        cp = float(payload["current_price"])
        return float(round(cp * np.random.uniform(0.996, 1.004), 4))
    # fallback: use last buffer
    rows = get_realtime_snapshot(50)
    if not rows:
        raise RuntimeError("no data")
    arr = np.array([r["price"] for r in rows[-20:]], dtype=float)
    return float(round(arr[-1] * np.random.uniform(0.998, 1.002), 4))

def retrain_lstm_if_needed():
    # For demo, retrain quickly if TF present
    if TF_AVAILABLE:
        return train_lstm_from_csv()
    return False
