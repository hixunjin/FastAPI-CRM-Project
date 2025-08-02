from fastapi import FastAPI
from app.routers import users,customers,email_tasks,blacklist
from fastapi.staticfiles import StaticFiles
app = FastAPI()

# 路由配置
app.include_router(users.router, prefix="/api/users", tags=["用户接口列表"])
app.include_router(customers.router, prefix="/api/customers", tags=["客户接口列表"])
app.include_router(email_tasks.router, prefix="/api/email_tasks", tags=["邮箱任务接口列表"])
app.include_router(blacklist.router, prefix="/api/blacklist", tags=["黑名单接口列表"])



#静态网页配置
app.mount("/static",StaticFiles(directory="static"),name="static")



