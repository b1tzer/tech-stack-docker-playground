import os
import time
import pymysql

def get_db_connection(max_retries=5, delay=5):
    """
    Creates and returns a connection to the MySQL database using environment variables.
    Includes retry logic for container startup scenarios.
    """
    retries = 0
    while retries < max_retries:
        try:
            return pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', 'rootpassword123'),
                database=os.environ.get('MYSQL_DATABASE', 'business_db'),
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.err.OperationalError as e:
            retries += 1
            print(f"Database connection failed. Retry {retries}/{max_retries} in {delay} seconds... ({e})")
            time.sleep(delay)
    
    raise Exception("Failed to connect to the database after multiple retries.")
