from abc import ABC, abstractmethod
class DatabaseClient(ABC):

    

    @abstractmethod
    def insert_many(self, table_name,columns, data_list):
        pass
    
    @abstractmethod
    def execute_query_list(self, query_list):
        pass

    @abstractmethod
    def execute_query(self, query):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    
    