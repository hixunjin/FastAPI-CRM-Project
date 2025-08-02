#数据库迁移文件
from app.database import Base,engine
from app import models
print("正在创建数据表")
Base.metadata.create_all(bind=engine)