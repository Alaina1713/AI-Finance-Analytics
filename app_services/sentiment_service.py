from app.utils import logger
try:
    from transformers import pipeline
    HF_AVAILABLE = True
except Exception:
    HF_AVAILABLE = False
    logger.info("transformers not available — will use keyword fallback")

_pipe = None
def _get_pipe():
    global _pipe
    if _pipe is None and HF_AVAILABLE:
        try:
            _pipe = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        except Exception as e:
            logger.exception("HF pipeline load failed")
            _pipe = None
    return _pipe

def sentiment_from_text(text):
    if not text or text.strip()=="":
        return {"label":"Neutral","score":0.0}
    pipe = _get_pipe()
    if pipe:
        try:
            out = pipe(text[:512])
            return out[0]
        except Exception:
            logger.exception("HF inference failed")
    # fallback: keyword analyzer
    low = text.lower()
    score = 0
    for w in ["gain","up","beat","bull","positive","surge"]:
        if w in low: score += 1
    for w in ["loss","down","miss","bear","negative","drop"]:
        if w in low: score -= 1
    label = "Positive" if score>0 else ("Negative" if score<0 else "Neutral")
    return {"label": label, "score": float(min(1.0, abs(score)/5))}
