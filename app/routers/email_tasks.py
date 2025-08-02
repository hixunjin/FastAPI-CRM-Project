#邮箱任务
#整体是邮件任务列表页面，用于展示邮件任务的执行状态
#页面嵌套功能:创建并发送邮件任务



from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.models import EmailTask,EmailBlackList,User,Customers
from app.auth import get_session,get_current_user
from app.schemas import CreateTask,ResponseTask
from typing import List

#导入其它功能模块的函数
from app.routers.customers import parse_tags


router = APIRouter()

#接口:获取任务列表，用于页面展示
@router.get('/',response_model=List[ResponseTask])
def get_email_tasks_list(
        db:Session = Depends(get_session),
        current_user:User = Depends(get_current_user)  #需要登录
):
    #直接获取全部的数据，返回给前端
    all_email_tasks = db.query(EmailTask).order_by(EmailTask.created_at.desc()).all()

    #我们查询出的数据会经过模型 ResponseTask 校验后返回给前端
    return all_email_tasks



#定义任务邮箱详情页面
@router.post('/CreateEmailTask/{task_id}',response_model=ResponseTask)
def CreateEmailTask(
        task_id:int,
        task:CreateTask,
        current_user:User=Depends(get_current_user),
        db:Session = Depends(get_session)
):
    #根据传入的id值查询记录
    detail_task = db.query(EmailTask).filter(EmailTask.id==task_id).first()

    #检查结果是否存在
    if detail_task:
        raise HTTPException(status_code=400,detail="记录不存在!")


    #返回响应
    return detail_task





#定义工具函数
def replace_vars(text:str,customer:Customers):
    return text.replace("{name}",customer.name)


#接口:创建任务并发送

@router.post('/SentEmail',response_model=ResponseTask)
def SentEmail(
        task:CreateTask,
        current_user:User = Depends(get_current_user),
        db:Session = Depends(get_session)
):
    #根据 task.tag 选中目标客户，如果不存在值，在是对所有客户进行发送邮件

    #相当于是 select* from customers
    #还应该知道，从数据库查询出的数据集合可以使用相同的 ORM方法 进行层层筛选
    query = db.query(Customers)

    if task.tag:
        #根据 task.tag对 query 进行条件筛选
        query = query.filter(Customers.tags.like(f"%{task.tag}%"))

    #获取所有用户
    customers = query.all()

    #组织任务状态相关数据
    total = len(customers)
    success = 0
    fail = 0


    #黑名单过滤

    #获取全部黑名单邮箱
    all_blacklist = db.query(EmailBlackList.email).all()

    #组织黑名单集合
    black_emails = {row[0] for row in all_blacklist}

    # 下面是模拟发送邮件，如果是黑名单集合中的邮箱，将跳过当前循环，开始下一个循环，‘
    # 如果是不是，则发送邮件

    for c in customers:
        #如果当前邮箱在黑名单集合中，结束本次循环，开始下次循环
        if c.email in black_emails:
            print(f"[跳过黑名单] {c.email}")
            continue

        #发送数据
        try:
            #组织标题和内容
            subject = replace_vars(task.title,c)
            content = replace_vars(task.content,c)
            print(f"📧 正在向 {c.email} 发送：\n主题：{subject}\n内容：{content}\n")

            #对成功此时进行计数
            success +=1

        except Exception as e:
            print(f"❌ 发送失败：{c.email}，错误：{e}")
            fail +=1

    #直接通过字段赋值预插入数据
    db_task = EmailTask(
        title = task.title,
        content = task.content,
        tag = task.tag,
        total = total,
        success = success,
        fail = fail
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task












