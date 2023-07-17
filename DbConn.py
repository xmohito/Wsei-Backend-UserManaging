import psycopg2

# Connect to the PostgreSQL database
def conn_to_db():
    conn = psycopg2.connect(
        host="localhost",
        database="back",
        user="postgres",
        password="1234",
        port=5432
    )
    return conn
