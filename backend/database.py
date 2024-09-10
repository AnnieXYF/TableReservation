# 建立与MySQL 数据库的链接，实现数据库的创建
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# 明确数据库连通地址
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Wsxedcrfvtgb10!@127.0.0.1:3306/TableReservation"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True) # log function has been used

# sessionmaker is used to establish session worked by "CRUD" for database DLL and DML
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=True)

#当你使用这个基类定义你的模型时，SQLAlchemy 会利用这个目录自动生成和映射数据库的模式。
Base = declarative_base(name='Base')
