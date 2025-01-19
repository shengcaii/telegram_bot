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

def dbupload(name, category, location, contact, details):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        insert_query = '''
        INSERT INTO resource (name, category, location, contact, details)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        '''
        cursor.execute(insert_query, (name, category, location, contact, details))
        resource_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        connection.close()
        return resource_id
    else:
        return None

def dbsearch(query):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            search_query = '''
            SELECT name, category, location, details FROM resource
            WHERE name ILIKE %s OR category ILIKE %s OR location ILIKE %s OR details ILIKE %s;
            '''
            cursor.execute(search_query, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Failed to search: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    else:
        print("No connection to the database.")
        return []

# Example usage
if __name__ == "__main__":
    query = "sport"
    results = dbsearch(query)
    print(results)