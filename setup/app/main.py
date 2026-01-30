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

# --- RabbitMQ Helpers ---
def rabbitmq_publish(queue: str, message: str):
    try:
        conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
        channel = conn.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(exchange='', routing_key=queue, body=message)
        conn.close()
        return True
    except Exception:
        return False

def rabbitmq_check_real():
    """Publish and immediately consume a test message to prove broker works."""
    try:
        conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
        channel = conn.channel()
        channel.queue_declare(queue='status_test', durable=True)

        # Publish test message
        channel.basic_publish(exchange='', routing_key='status_test', body='ping')

        # Try to consume it back
        method_frame, header_frame, body = channel.basic_get(queue='status_test', auto_ack=True)
        conn.close()
        return body == b'ping'
    except Exception:
        return False

# --- Auth ---
def authenticate_user(username, password):
    # First check Redis cache
    cached_pw = redis_client.get(f"user:{username}:pw")
    if cached_pw:
        return cached_pw.decode() == password

    # If not cached, query PostgreSQL
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT password FROM users WHERE username=:u"), {"u": username}
        ).fetchone()
        if result:
            # Cache the password for 5 minutes
            redis_client.setex(f"user:{username}:pw", 300, result[0])
            return result[0] == password
    return False

@app.post("/login")
def login(username: str, password: str):
    if not authenticate_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"user": username}, SECRET_KEY, algorithm="HS256")

    # Publish login event to RabbitMQ
    rabbitmq_publish("login_events", f"User {username} logged in")

    return {"token": token}

@app.get("/status")
def status(token: str):
    # Validate JWT
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check DB
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except:
        pass

    # Check Redis by storing and retrieving a test key
    redis_ok = False
    try:
        redis_client.set("status:test", "ok", ex=10)
        redis_ok = redis_client.get("status:test") == b"ok"
    except:
        pass

    # Check RabbitMQ by publish/consume
    rabbit_ok = rabbitmq_check_real()

    return {
        "database": db_ok,
        "cache": redis_ok,
        "message_broker": rabbit_ok,
        "status": "All integrations successful" if (db_ok and redis_ok and rabbit_ok) else "Some integrations failed"
    }
