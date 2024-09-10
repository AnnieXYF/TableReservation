from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel, constr, validator
from backend.database import SessionLocal
from sqlalchemy.orm import Session
from backend.crud import ReservationService, unavailable_date, unavailable_time
import datetime
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app=FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# pydantic会进行前端传输数据的basemodel 校验，以保证数据可以进行有效转化成要求的格式
class ReservationModel(BaseModel):
    date: str
    time: str

def format_date(date: datetime.date) -> str:
    return date.strftime("%d-%m-%Y")

def format_time(time: datetime.time) -> str:
    return time.strftime("%H:%M")

# 接收预订请求
@app.post("/reserve")
def reserve_table(request:ReservationModel,db:Session=Depends(get_db)):
    # 如果缺失date 或者 time，直接返回数据缺失的提示
    if not request.date or not request.time:
        raise HTTPException(status_code=400, detail="Missing necessary information")
    # 创建service实例变量用来调用方法
    service=ReservationService(db)
    # 将date 转换成 “YY-MM-DD" 格式
    # formatted_date = datetime.strptime(request.date, "%d-%m-%Y").strftime("%d-%m-%Y")
    # # 将time 转换成 "HH:MM:SS" 格式
    # formatted_time = datetime.strptime(request.time, "%H:%M").strftime("%H:%M")
    # 调用make_reservation 方法并传入两个参数，返回相应信息
    reservation= service.make_reservation(request.date,request.time)
    return reservation

# 获取不可用日期
@app.get("/unavailable_dates")
def get_unavailable_dates(db:Session=Depends(get_db)):
    # 创建unavailable_date_service实例变量用来调用方法
    unavailable_date_service=unavailable_date(db)
    # 调用get_unavailble_date方法
    unavailable_dates=unavailable_date_service.get_unavailable_date()
    return unavailable_dates

# 获取可用日期中不可用时间段
@app.get("/unavailable_times/{date}")
def get_unavailable_times(date:str, db:Session=Depends(get_db)):
    # Convert date_str from "DD-MM-YYYY" to "YYYY-MM-DD"
    # date_obj = datetime.datetime.strptime(date, "%d-%m-%Y").date()
    unavailable_time_service=unavailable_time(db)
    unavailable_times=unavailable_time_service.get_unavailable_time(date)
    return unavailable_times

origins = [
    "http://localhost:5137",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5137",# 允许的前端地址
    "http://localhost:5173"  # 将这个端口加入
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("user_router:app", host="0.0.0.0", port=8000)

