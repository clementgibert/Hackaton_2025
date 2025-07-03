# database_logger.py
import snowflake.connector
from datetime import datetime

def insert_alert(student_id, site, url, timestamp=None):
    try:
        conn = snowflake.connector.connect(
            user='duchelle',
            password='QxWxaUfe9z3RVsR',
            account='jjzpzio-kx53081.snowflakecomputing.com',
            warehouse='MY_WAREHOUSE',
            database='MY_DETECTION_DB',
            schema='DETECTION_SCHEMA'
        )

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (student_id, site, url, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (student_id, site, url, timestamp or datetime.now()))

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR] Insertion BDD échouée: {e}")
