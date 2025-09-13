import time, json, requests, argparse
from app_services.ingest_service import load_sample_df
from datetime import datetime

def run(endpoint="http://localhost:5000/api/ingest_tick", rate=5):
    df = load_sample_df()
    rows = df.tail(100).reset_index(drop=True).to_dict(orient="records")
    i = 0
    print("Starting simulator → POSTing ticks to", endpoint)
    try:
        while True:
            r = rows[i % len(rows)]
            tick = {"symbol": r["symbol"], "price": float(r["price"]), "volume": int(r["volume"]), "timestamp": datetime.utcnow().isoformat()}
            try:
                requests.post(endpoint, json=tick, timeout=2.0)
                print("sent", tick)
            except Exception as e:
                print("POST failed:", e)
            i += 1
            time.sleep(1.0 / rate)  # rate ticks per second
    except KeyboardInterrupt:
        print("simulator stopped")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://localhost:5000/api/ingest_tick")
    parser.add_argument("--rate", type=float, default=2.0)
    args = parser.parse_args()
    run(endpoint=args.endpoint, rate=args.rate)
