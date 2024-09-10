from pydantic import BaseModel
from datetime import time,date

class Reservation (BaseModel):
    id: int
    table_name: str
    book_time: time
    book_date: date

#pydantic：Pydantic 是一个用于数据校验和解析的库，基于 Python 的类型提示系统。
    # 它允许开发者定义数据结构，并且可以自动地验证传入的数据是否符合这些结构
    class Config:
        orm_mode = True
