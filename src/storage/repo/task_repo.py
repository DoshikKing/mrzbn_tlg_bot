from src.storage.config.conn import Conn
from .repo import Repo
from src.storage.model.task import Task

class TaskRepo(Repo):
    def __init__(
            self,
            conn: Conn
    ):
        self.table = "tasks"
        self.conn = conn

    def get_document_by_filter(self, doc_id, doc_filter):
        task = Task();
        with self.conn as cn:
            with cn.cursor() as cur:
                cur.execute("SELECT * FROM (%s) WHERE ID=(%s) AND (%s);", (self.table, doc_id, doc_filter))
                cur.fetchone()

    def get_document(self, doc_id):
        task = None
        with self.conn as cn:
            with cn.cursor() as cur:
                cur.execute("SELECT * FROM (%s) WHERE ID=(%s);", (self.table, doc_id))
                task = cur.fetchone()
                cn.commit()
        return task

    def create_document(self, doc):
        pass

    def update_document(self, doc):
        pass

    def delete_document(self, doc_id):
        pass
