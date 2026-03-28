import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = None
cursor = None
db_connected = False

def connect_db():
    global conn, cursor, db_connected
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password="password",
            database=os.getenv("DB_NAME", "fake_news")
        )
        cursor = conn.cursor()
        db_connected = True
        print("✅ Database Connected Successfully")
    except Exception as e:
        db_connected = False
        print(f"❌ Database Connection Error: {e}")

def initialize_db():
    """Initialize database table if it doesn't exist"""
    if conn and cursor:
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    text LONGTEXT,
                    label VARCHAR(10),
                    confidence FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ Database table initialized")
        except Exception as e:
            print(f"⚠️ Table initialization error: {e}")

conn_status = connect_db()
if conn and cursor:
    initialize_db()

def save_result(text, label, confidence):
    """Save prediction result to database"""
    global conn, cursor, db_connected
    
    if not db_connected or not conn or not cursor:
        print("⚠️ Database not connected")
        return False
    
    try:
        query = "INSERT INTO results (text, label, confidence) VALUES (%s, %s, %s)"
        cursor.execute(query, (text[:1000], label, confidence))  # Truncate text
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Insert Error: {e}")
        try:
            conn.reconnect()
            db_connected = True
        except:
            db_connected = False
        return False

def fetch_results():
    """Fetch analysis statistics from database"""
    global conn, cursor, db_connected
    
    if not db_connected or not conn or not cursor:
        return []
    
    try:
        cursor.execute("""
            SELECT label, COUNT(*) as count 
            FROM results 
            GROUP BY label
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"⚠️ Fetch Error: {e}")
        return []

def fetch_recent_results(limit=10):
    """Fetch recent analysis results"""
    global conn, cursor, db_connected
    
    if not db_connected or not conn or not cursor:
        return []
    
    try:
        cursor.execute("""
            SELECT id, text, label, confidence, created_at 
            FROM results 
            ORDER BY created_at DESC 
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"⚠️ Fetch Error: {e}")
        return []

def is_database_connected():
    """Check if database is connected"""
    return db_connected