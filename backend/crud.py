from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models import Reservation,TableInfo
from fastapi import HTTPException


# 预订功能
class ReservationService:
    def __init__(self, db: Session):
        self.db = db
    # date and time are the data transmit from fontend

    def make_reservation(self,date,time): # date：date 为类型注解，不会对参数进行数据转化
        # 筛选时间和日期都匹配的第一条数据作为可用的桌子信息
        available_table = self.db.query(TableInfo).filter(
            and_(
                TableInfo.available_time==True,
                TableInfo.available_date==True,
                TableInfo.time_choose==time,
                TableInfo.date_choose==date
        )).first()
        # 如果没有可用的，返回错误信息
        if not available_table:
            raise HTTPException(status_code=400, detail="No available table")

        # 在Reservation 表中创建预订信息
        reservation=Reservation(
                table_name=available_table.table_name,
                book_time=available_table.time_choose,
                book_date=available_table.date_choose
        )
        # 更新TableInfo 表里对应的桌子号的available_time状态
        available_table.available_time=False

        # 将reservation 这条数据添加到Reservation 表
        self.db.add(reservation)
        # 执行所有数据库操作
        self.db.commit()
        self.db.refresh(reservation)
        # 返回预订成功的信息
        return {"status": "success", "message": f'reservation made for {reservation.book_date} at {reservation.book_time}'}

#不可用日期筛选
class unavailable_date:
    def __init__(self,db:Session):
        self.db = db

# self.db 是传递给服务类的 Session 实例。这样，self.db 可以用于执行各种数据库操作，比如查询、添加、更新等
    def get_unavailable_date(self):
        # 筛选日期为false （即不可用）的具体日期，去重只保留一个
        unavailble_dates=(self.db.query(TableInfo.date_choose).filter(
            TableInfo.available_date==False)
         .distinct()
         .all()
        )
        # 将获取到的不可用日期转换成一个列表
        unavailble_dates_list=[date[0] for date in unavailble_dates]
        # 获取桌子名称
        table_names=self.db.query(TableInfo.table_name).filter().distinct()
        # 将桌子名称转化成一个列表
        table_names_list=[table[0] for table in table_names]
        final_unavailble_dates_list=[]
        # 对于每一个不可用日期列表里的日期进行桌子名字的筛选
        for date in unavailble_dates_list:
            # 只保留那些在指定日期中不可用的桌子名称
            table_name_with_date=(self.db.query(TableInfo.table_name).filter(
                and_(
                TableInfo.available_date==False,
                TableInfo.date_choose==date))
                .distinct()
                .all()
            )
            # 将不可用日期下的桌子名称转换成一个列表
            table_names_with_date_list=[table[0] for table in table_name_with_date]
            # 比较集合: 使用集合 (set) 来比较两个列表是否包含相同的元素，可以避免顺序问题和重复项。
            # 如果不可用日期下的桌子列表等于桌子名称列表 （即同一不可用天数下，所有的桌子都不能用）
            if set(table_names_with_date_list)==set(table_names_list):
                # 则把这一天明确成为不可用日期
                final_unavailble_dates_list.append(date)
        return {"unavailable_dates":final_unavailble_dates_list}

class unavailable_time:
    def __init__(self,db:Session):
        self.db = db

    def get_unavailable_time(self,target_date):
        # 获取传入date下不可用时间，去重
        unavailable_times_by_date=(self.db.query(TableInfo.time_choose).filter(
            and_(
            TableInfo.date_choose==target_date,
            TableInfo.available_time==False))
            .distinct()
            .all()
        )
        unavailable_times_by_date_list=[time[0] for time in unavailable_times_by_date]
        print(unavailable_times_by_date_list,"unavailable_times_by_date_list")
        final_unavailable_times = []
        table_names = self.db.query(TableInfo.table_name).filter().distinct()
        table_names_list = [table[0] for table in table_names]
        print(table_names_list,"table_names_list")
        # 对于指定日期下不可用时间进行二次筛选，保留对应桌子名称
        for time in unavailable_times_by_date_list:
            table_name_with_time_and_date=(self.db.query(TableInfo.table_name).filter(
                and_(
                TableInfo.time_choose==time,
                TableInfo.available_time==False,
                TableInfo.date_choose==target_date
            )).distinct().
            all())
            table_name_with_time_and_date_list=[table[0] for table in table_name_with_time_and_date]
            print(table_name_with_time_and_date_list,"table_name_with_time_and_date_list")
            # 不可用时间下桌子名称等于全集，则把该时间列为该日期下的不可用时间
            if set(table_name_with_time_and_date_list)==set(table_names_list):
                final_unavailable_times.append(time)
        return {"unavailable_times":final_unavailable_times}
