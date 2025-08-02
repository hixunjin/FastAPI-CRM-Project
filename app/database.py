"""
mysql数据库配置
数据库:fastapi_crm
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 替换成你的实际 MySQL 配置
DB_USER = "root"
DB_PASSWORD = "As20010504"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "fastapi_crm1"

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

#引擎
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 可选：打印SQL语句，调试用
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

