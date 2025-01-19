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
<<<<<<< HEAD
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
=======
        cursor.close()
        connection.close()

def get_user_resources(user_id):
>>>>>>> c899748a2451722d99a1674cd36ae613e948908f
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
<<<<<<< HEAD
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
=======
            query = '''
                SELECT id, name, category, location, description 
                FROM resource 
                WHERE user_id = %s AND is_deleted = FALSE
                ORDER BY created_at DESC
            '''
            cursor.execute(query, (str(user_id),))
            return cursor.fetchall()
        finally:
            cursor.close()
            connection.close()
    return []

def delete_resource(resource_id, user_id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # First, verify ownership
            verify_query = '''
                SELECT id FROM resource 
                WHERE id = %s AND user_id = %s AND is_deleted = FALSE
            '''
            cursor.execute(verify_query, (resource_id, str(user_id)))
            if not cursor.fetchone():
                return False, "Ads not found or you don't have permission to delete it"
            
            # Perform soft delete
            delete_query = '''
                UPDATE resource 
                SET is_deleted = TRUE 
                WHERE id = %s AND user_id = %s
                RETURNING id
            '''
            cursor.execute(delete_query, (resource_id, str(user_id)))
            connection.commit()
            return True, "Ads deleted successfully"
        except Exception as e:
            connection.rollback()
            return False, f"Error deleting resource: {str(e)}"
        finally:
            cursor.close()
            connection.close()
    return False, "Database connection error"

def update_resource(resource_id, user_id, updates):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # First, verify ownership
            verify_query = '''
                SELECT id FROM resource 
                WHERE id = %s AND user_id = %s AND is_deleted = FALSE
            '''
            cursor.execute(verify_query, (resource_id, str(user_id)))
            if not cursor.fetchone():
                return False, "Ads not found or you don't have permission to update it"
            
            # Build update query dynamically based on provided fields
            update_fields = []
            params = []
            for key, value in updates.items():
                if key in ['name', 'category', 'location', 'description']:
                    update_fields.append(f"{key} = %s")
                    params.append(value)
            
            if not update_fields:
                return False, "No valid fields to update"
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.extend([resource_id, str(user_id)])
            
            update_query = f'''
                UPDATE resource 
                SET {", ".join(update_fields)}
                WHERE id = %s AND user_id = %s
                RETURNING id
            '''
            
            cursor.execute(update_query, params)
            connection.commit()
            return True, "Ads updated successfully"
        except Exception as e:
            connection.rollback()
            return False, f"Error updating Ads: {str(e)}"
        finally:
            cursor.close()
            connection.close()
    return False, "Database connection error"

def dbupload(name, category, location, user_id, description):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        insert_query = '''
        INSERT INTO resource (name, category, location, contact, description)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        '''
        cursor.execute(insert_query, (name, category, location, user_id, description))
        resource_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        connection.close()
        return resource_id
    else:
        return None

def dbsearch(query_terms):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Build dynamic query with AND conditions for multiple terms
            conditions = []
            params = []
            
            for term in query_terms:
                term = term.strip()
                if term:
                    conditions.append("""
                        (name ILIKE %s OR 
                         category ILIKE %s OR 
                         location ILIKE %s OR 
                         description ILIKE %s)
                    """)
                    params.extend([f"%{term}%"] * 4)
            
            if conditions:
                search_query = """
                    SELECT name, category, location, description 
                    FROM resource
                    WHERE """ + " AND ".join(conditions)
                
                cursor.execute(search_query, params)
                results = cursor.fetchall()
                return results
            return []
            
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
    init_db()
>>>>>>> c899748a2451722d99a1674cd36ae613e948908f
    query = "sport"
    results = dbsearch(query)
    print(results)