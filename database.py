import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

def get_db_connection():
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("Connection successful!")
        return connection
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def fetch_current_time():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print("Current Time:", result)
        cursor.close()
        connection.close()
        print("Connection closed.")
    else:
        print("No connection available.")

def init_db():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS resource (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            category VARCHAR(100),
            location VARCHAR(100),
            contact VARCHAR(100),
            details TEXT
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Table created successfully.")
        cursor.close()
        connection.close()
        print("Connection closed.")
    else:
        print("No connection available.")

# Example usage
if __name__ == "__main__":
    init_db()
    fetch_current_time()