import psycopg2
from psycopg2 import sql

# Database connection details
db_params = {   
        'dbname': 'IntellicaTech',
        'user': 'Intellica',
        'password': '8g^[pQR%!Pv{rL+iW(g)',
        'host': 'intellicatech.cbu0o4ou4s2u.ap-south-1.rds.amazonaws.com',  # Or your database server address
        'port': '5432',       # Default PostgreSQL port
    }   # default PostgreSQL port

try:
    # Establish the connection
    conn = psycopg2.connect(**db_params)
    
    # Create a cursor object
    cur = conn.cursor()
    
    print("Connected to the database!")

    # Sample query (optional)
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    print(f"Database version: {db_version}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error connecting to the database: {e}")
