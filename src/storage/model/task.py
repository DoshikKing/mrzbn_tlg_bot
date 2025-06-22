from typing import Optional
import uuid

from src.storage.storage_enum.task_status import Status


class Task:
    def __init__(
            self,
            user_id: str,
            modified,
            doc_id: Optional[str] = uuid.uuid4(),
            retro: Optional[bool] = False,
            status: Optional[Status] = Status
    ):
        self.user_id = user_id
        self.doc_id = doc_id
        self.retro = retro
        self.status = status
        self.modified = modified