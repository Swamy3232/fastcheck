from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Database connection details
DB_HOST = "aws-1-ap-south-1.pooler.supabase.com"
DB_PORT = 6543
DB_NAME = "postgres"
DB_USER = "postgres.vegkphzwxjmazpzkofex"
DB_PASSWORD = "Swamygowda32"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor  # returns dict instead of tuple
    )
    return conn

@app.get("/products")
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"products": rows}
