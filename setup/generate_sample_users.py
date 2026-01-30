import psycopg2
from psycopg2 import sql

# --- Config ---
DB_HOST = "db"        # name of the PostgreSQL service in Docker Compose. use "localhost" if running locally
DB_PORT = "5432"
DB_NAME = "mydb"
DB_USER = "user"
DB_PASS = "pass"

# --- Sample Data ---
sample_users = [
    ("alice", "password123", "alice@example.com"),
    ("bob", "securepass", "bob@example.com"),
    ("charlie", "mypassword", "charlie@example.com"),
]

def load_users():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        # --- Create table if not exists ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        conn.commit()

        # --- Insert sample users ---
        for username, password, email in sample_users:
            cur.execute(
                sql.SQL("""
                    INSERT INTO users (username, password, email)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                """),
                (username, password, email)
            )

        conn.commit()
        print("✅ Table ensured and sample users inserted successfully!")

        cur.close()
        conn.close()

    except Exception as e:
        print("❌ Error inserting users:", e)

if __name__ == "__main__":
    load_users()
