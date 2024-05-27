import psycopg2
from psycopg2 import OperationalError

def create_connection():
    try:
        conn = psycopg2.connect(
            dbname="packrunnerDB",
            user="packrunnerDB_owner",
            password="GXJyfgEB23nj",
            host="ep-hidden-king-a5h5vm2e.us-east-2.aws.neon.tech",
            sslmode="require"
        )
        print("Connection to the PostgreSQL database successful")
        return conn
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None

def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()

def execute_sql_file(connection, filepath):
    try:
        with open(filepath, 'r') as file:
            sql_file = file.read()
            execute_query(connection, sql_file)
    except IOError as e:
        print(f"Error opening file {filepath}: {e}")

# Testing the connection and creating tables
connection = create_connection()
if connection is not None:
    execute_sql_file(connection, "schema.sql")
