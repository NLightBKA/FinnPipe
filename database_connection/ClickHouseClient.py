import clickhouse_connect

from database_connection.DatabaseClient import DatabaseClient
class ClickHouseClient(DatabaseClient):
    def __init__(self,host="localhost", port=8123, user="finnpipe", password="2437824378"):
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            user=user,
            password=password
        )

    def insert_many(self, table_name, columns, data_list):
        self.client.insert(table_name,  data_list,columns)
      

   

    def execute_query_list(self, query_list):
        fetchall_results = []
        for query in query_list:
            fetchall_results.append(self.execute_query(query))
      
        return fetchall_results

    def execute_query(self, query):
        query_type = query.strip().upper()

        if query_type.startswith(("SELECT", "WITH", "SHOW", "DESCRIBE")):
            return self.client.query(query).result_rows

        self.client.command(query)
      
        return None

    def commit(self):
        pass

    def rollback(self):
        pass

  