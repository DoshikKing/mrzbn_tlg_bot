from src.storage.config.conn import Conn
from src.storage.model.task import Task
from datetime import datetime, timezone

from src.storage.storage_enum.task_status import Status

class TaskRepo:
    def __init__(
            self,
            conn: Conn,
            timezone: timezone
    ):
        self.timezone = timezone
        self.table = "tasks"
        self.conn = conn

    def get_document_by_user_id(self, doc_id, user_id):
        task = None
        with self.conn as cn:
            with cn.cursor() as cur:
                cur.execute("SELECT * FROM (%s) WHERE ID=(%s) AND userId=(%s);", (self.table, doc_id, user_id))
                task = cur.fetchone()
                cn.commit()
        return task

    def get_document(self, doc_id):
        task = None
        with self.conn as cn:
            with cn.cursor() as cur:
                cur.execute("SELECT * FROM (%s) WHERE ID=(%s);", (self.table, doc_id))
                task = cur.fetchone()
                cn.commit()
        return task

    def create_document(self, user_id) -> Task:
        task = Task(user_id, datetime.now(self.timezone), None, False, Status.NEW)
        with self.conn as cn:
            with cn.cursor() as cur:
                cur.execute("INSERT INTO (%s) (id, user_id, status, retro, modified) VALUES (%s, %s, %s, %s, %s);",
                            (self.table, task.doc_id, task.user_id, task.status, task.status, task.retro, task.modified))
                cn.commit()
        return task

    def update_document(self, doc):
        pass

    def delete_document(self, doc_id):
        pass
