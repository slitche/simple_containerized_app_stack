from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
import redis
import pika
import jwt

# Import config values
from app.config import DB_URL, REDIS_URL, RABBIT_URL, SECRET_KEY

app = FastAPI()

# --- Connections ---
engine = create_engine(DB_URL)
redis_client = redis.Redis.from_url(REDIS_URL)

def rabbitmq_check():
    try:
        conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
        channel = conn.channel()
        channel.queue_declare(queue='test')
        channel.basic_publish(exchange='', routing_key='test', body='ping')
        conn.close()
        return True
    except Exception:
        return False

# --- Auth ---
def authenticate_user(username, password):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT password FROM users WHERE username=:u"), {"u": username}).fetchone()
        return result and result[0] == password

@app.post("/login")
def login(username: str, password: str):
    if not authenticate_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"user": username}, SECRET_KEY, algorithm="HS256")
    return {"token": token}

@app.get("/status")
def status(token: str):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except:
        pass

    redis_ok = redis_client.ping()
    rabbit_ok = rabbitmq_check()

    return {
        "database": db_ok,
        "cache": redis_ok,
        "message_broker": rabbit_ok,
        "status": "All integrations successful" if (db_ok and redis_ok and rabbit_ok) else "Some integrations failed"
    }
