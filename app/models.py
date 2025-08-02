from sqlalchemy import Column, Integer, String, DateTime, Text, func  # 导入字段
from datetime import datetime
from datetime import datetime, timezone

created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


from app.database import Base  #导入数据库配置

#我们只是在这里创建数据表，数据校验还需要创建 pydantic 模型完成工作
#数据库使用 MySQL 的时候，字段 String 必须要指定长度



#创建管理员表
class User(Base):     #继承 Base
    __tablename__ = 'users'
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String(30),unique=True,index=True,nullable=False)
    password = Column(String(255),nullable=False)

    """
    用于判断用户身份，默认是  user,管理员 admin
    """
    role = Column(String(10),default="user")
    created_time = Column(DateTime(timezone=True),server_default=func.now())


#创建存储客户信息的表

class Customers(Base):
    __tablename__ = 'customers'
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(30),nullable=False)  #不允许为空
    email = Column(String(30),unique=True,index=True,nullable=False)
    #以逗号分隔的标准字符串
    tags = Column(String(30),default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))


#创建邮件模型，用于发送邮件
class EmailTask(Base):
    __tablename__ = 'email_tasks'
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String(30),nullable=False)
    content = Column(Text,nullable=False)
    tag = Column(String(30),nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total = Column(Integer,default=0)   #任务邮件数量
    success = Column(Integer,default=0)  #成功发送的数量
    fail = Column(Integer,default=0)    #发送失败的数量


#黑名单邮箱表
class EmailBlackList(Base):
    __tablename__="email_blacklist"
    id = Column(Integer,primary_key=True,index=True)
    email = Column(String(30),unique=True,nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))





