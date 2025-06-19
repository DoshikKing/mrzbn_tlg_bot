from abc import ABC, abstractmethod


class Repo(ABC):
    @abstractmethod
    def __init__(self, table, conn):
        self.table = table
        self.conn = conn
        pass

    @abstractmethod
    def get_document(self, doc_id):
        pass

    @abstractmethod
    def get_document_by_filter(self, doc_id, doc_filter):
        pass

    @abstractmethod
    def create_document(self, doc):
        pass

    @abstractmethod
    def update_document(self, doc):
        pass

    @abstractmethod
    def delete_document(self, doc_id):
        pass
