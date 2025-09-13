from flask import Blueprint, jsonify, request, current_app, render_template
from .models import db, MarketTick
from app_services.ingest_service import seed_db_from_csv, get_realtime_snapshot
from app_services.lstm_service import predict_price_single, retrain_lstm_if_needed
from app_services.anomaly_service import detect_anomaly_single, retrain_anomaly_if_needed
from app_services.sentiment_service import sentiment_from_text
from .utils import logger
from datetime import datetime

bp = Blueprint("main", __name__)

# web pages
@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

# health
@bp.route("/api/health")
def health():
    return jsonify({"status": "ok"})

# seed DB from CSV (one-time)
@bp.route("/api/admin/seed", methods=["POST"])
def seed_db():
    n = int(request.json.get("n", 500))
    rows = seed_db_from_csv(n=n)
    return jsonify({"inserted": len(rows)})

# historical (query last n rows, optional symbol)
@bp.route("/api/historical", methods=["GET"])
def historical():
    symbol = request.args.get("symbol", None)
    n = int(request.args.get("n", 200))
    q = MarketTick.query
    if symbol:
        q = q.filter_by(symbol=symbol)
    rows = q.order_by(MarketTick.id.desc()).limit(n).all()
    data = [r.to_dict() for r in reversed(rows)]
    return jsonify({"data": data})

# realtime snapshot (last n ticks)
@bp.route("/api/realtime", methods=["GET"])
def realtime():
    n = int(request.args.get("n", 50))
    snapshot = get_realtime_snapshot(n=n)
    return jsonify({"snapshot": snapshot})

# ingestion endpoint for external producers (simulator/consumer can post here)
@bp.route("/api/ingest_tick", methods=["POST"])
def ingest_tick():
    payload = request.get_json(force=True)
    try:
        symbol = payload.get("symbol")
        price = float(payload.get("price"))
        volume = int(payload.get("volume", 0))
        ts = payload.get("timestamp")
        ts_parsed = datetime.fromisoformat(ts) if ts else datetime.utcnow()
        tick = MarketTick(symbol=symbol, price=price, volume=volume, timestamp=ts_parsed)
        db.session.add(tick)
        db.session.commit()
        logger.info(f"Inserted tick: {symbol} {price}")
        return jsonify({"status":"ok"}), 201
    except Exception as e:
        logger.exception("ingest_tick error")
        return jsonify({"error": str(e)}), 400

# prediction endpoint
@bp.route("/api/predict-price", methods=["POST"])
def predict_price():
    payload = request.get_json(force=True)
    try:
        p = predict_price_single(payload)
        return jsonify({"prediction": p})
    except Exception as e:
        logger.exception("predict error")
        return jsonify({"error": str(e)}), 500

# anomaly endpoint
@bp.route("/api/detect-anomaly", methods=["POST"])
def anomaly():
    payload = request.get_json(force=True) if request.data else {}
    try:
        res = detect_anomaly_single(payload)
        return jsonify(res)
    except Exception as e:
        logger.exception("anomaly error")
        return jsonify({"error": str(e)}), 500

# sentiment
@bp.route("/api/sentiment", methods=["POST"])
def sentiment():
    text = request.get_json(force=True).get("text", "")
    out = sentiment_from_text(text)
    return jsonify(out)

# retrain admin endpoints
@bp.route("/api/admin/retrain-lstm", methods=["POST"])
def retrain_lstm():
    out = retrain_lstm_if_needed()
    return jsonify({"retrained": out})

@bp.route("/api/admin/retrain-anom", methods=["POST"])
def retrain_anom():
    out = retrain_anomaly_if_needed()
    return jsonify({"retrained": out})
