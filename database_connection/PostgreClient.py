import psycopg2
from psycopg2 import sql
from database_connection.DatabaseClient import DatabaseClient
class PostgreClient(DatabaseClient):
    def __init__(self, host="localhost",port=5432, database="finnpipe", user="finnpipe", password="2437824378"):
        self.client = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )   

    def execute_query_list(self, query_list):
        fetchall_results = []
        with self.client.cursor() as cursor:
            for query in query_list:
                cursor.execute(query)
                if cursor.description is not None:
                    fetchall_results.append(cursor.fetchall())
                else:
                    fetchall_results.append(None)
        return fetchall_results

    def execute_query(self, query):
        with self.client.cursor() as cursor:
            cursor.execute(query)
            if cursor.description is not None:
                return cursor.fetchall()
        return None 

    def commit(self):
        try:
            self.client.commit()
        except Exception as e:
            self.rollback()
            print(f"Error occurred while committing: {e}")

    def rollback(self):
        try:
            self.client.rollback()
        except Exception as e:
            print(f"Error occurred while rolling back: {e}")