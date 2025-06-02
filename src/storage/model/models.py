from sqlmodel import Field, SQLModel

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    user_id: int | None = Field(default=None, foreign_key="user.id")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    expire: str