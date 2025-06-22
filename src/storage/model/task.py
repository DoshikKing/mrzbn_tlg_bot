from typing import Optional
import uuid
from .doc import Document


class Task(Document):
    def __init__(
            self,
            user_id: str,
            doc_id: Optional[str] = uuid.uuid4(),
            retro: Optional[bool] = False,
            status: Optional[str] = None
    ):
        self.user_id = user_id
        self.doc_id = doc_id
        self.retro = retro
        self.status = status
        self.modify()