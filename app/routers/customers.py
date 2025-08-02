import pandas as pd
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File
from  sqlalchemy.orm import Session
from typing import List,Optional
from  app import models,auth,schemas
from app.auth import get_session,get_current_user
import pandas as d
from sqlalchemy.exc import IntegrityError
from io import BytesIO
from app.schemas import CreateCustomer,Customer_Response,UpdateCustomer


router = APIRouter()


"""客户列表展示"""
#参数:登录验证、返回列表响应、数据库查询对象


# 工具函数：字符串转列表
#比如：把字符串 "A, B, C" → ["A", "B", "C"]，用于格式美化输出

def parse_tags(tags_str: str):
    #转换功能
    return [t.strip() for t in tags_str.split(",") if t.strip()]




#把标签列表转换为字符串，用于存储到数据库
def join_tags(tags: List[str]):
    return ",".join(tags)

@router.get('/get_all_customers/',response_model=List[Customer_Response])
def get_all_customers(
        db:Session = Depends(get_session),
        keyword:Optional[str] = None,  #姓名
        tag:Optional[str] = None,  #标签

        #分页
        skip: int = 0,
        limit:int = 10,
        current_user:models.User = Depends(get_current_user)):

    #查询功能
    query = db.query(models.Customers)  #select * from Customers

    #如果有关键字或者标签，将执行查询，如果什么也不添加，将表示不执行查询功能

    #姓名
    if keyword:
        #模糊查询
        query = query.filter(models.Customers.name.contains(keyword))

    #标签
    if tag:
        query = query.filter(models.Customers.tags.contains(tag))

    #分页功能
    # query 代表全部数据，下面对其进行分页显示
    # customers 是列表结构
    customers = query.order_by(models.Customers.updated_at.desc()).offset(skip).limit(limit).all()

    #对结果进行转换
    #整体就是一个列表，列表中嵌套多个字典，字典中有一组信息
    result = []

    for c in customers:
        result.append(
            {
                **c.__dict__,
                'tags':parse_tags(c.tags)
            }
        )
    #返回列表
    return result



#创建客户
#先登录
#字段:name email 标签列表（允许为空）
#参数:登录依赖、数据库会话对象、校验模型

@router.post('/create_customers')
def Create_Customer(
        customer: CreateCustomer,
        current_user:models.User = Depends(get_current_user),
        db:Session = Depends(get_session)):
    #先检查下用户是否已经存在，应该根据邮箱查询出来
    get_customer = db.query(models.Customers).filter(models.Customers.email == customer.email).first()

    if get_customer:
        raise HTTPException(status_code=400,detail="邮箱已经存在")
    #不存在则添加

    new_customer = models.Customers(
        name=customer.name,email=customer.email,tags=join_tags(customer.tags)  #需要转换一下
    )
    db.add(new_customer)
    db.commit()

    #页面更新，并返回数据
    return {
        **new_customer.__dict__,
        'tags':parse_tags(new_customer.tags)
    }



#修改客户数据，名称和标签，因为邮箱是唯一的
#需要登录、获取数据库会话
#根据 id值 修改字段:name 标签，和django一样

@router.put('/UpdateCustomer/{customer_id}')
def UpdateCustomer(
        customer:UpdateCustomer,
        customer_id:int,
        current_user:models.User = Depends(get_current_user),
        db:Session = Depends(get_session)):

    #查询出要修改的客户
    get_customer = db.query(models.Customers).filter(models.Customers.id == customer_id).first()
    if get_customer is None:
        raise HTTPException(status_code=400,detail="用户不存在")
    #更新用户数据
    if customer.name:
        get_customer.name = customer.name
    if customer.tags:
        get_customer.tags = join_tags(customer.tags)

    db.commit()
    db.refresh(get_customer)

    #返回数据
    return {

        **get_customer.__dict__,
        "tags":parse_tags(get_customer.tags)
    }






#删除客户，根据前端传来的 id 进行删除
#登录、数据库会话、查询、删除、更新列表

@router.delete('/delete/{customer_id}')
def DeleteCustomer(
        customer_id:int,
        current_user:models.User = Depends(get_current_user),
        db:Session = Depends(get_session)):

    #查询记录
    get_customer = db.query(models.Customers).filter(models.Customers.id==customer_id).first()
    if get_customer is None:
        raise HTTPException(status_code=404,detail="用户不存在!")

    #删除用户
    db.delete(get_customer)
    db.commit()
    return {"msg":"删除成功！"}




#定义导入文件功能
@router.post('/import_excel')
async def import_excel(
        file:UploadFile = File(...), #文件接收对象，必传参数
        db:Session = Depends(get_session),
        current_user:models.User = Depends(get_current_user)  #登录验证，仅仅是让函数有登录功能，无其它作用
):
    #检查文件扩展名格式是否为 Excel 的格式
    if not file.filename.endswith((".xls",".xlsx")):
        raise HTTPException(status_code=400,detail="请上传Excel文件")
    #读取文件内容

    try:
        content = await file.read()  #读取文件内容
        df = pd.read_excel(BytesIO(content))

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"读取失败{str(e)}")
    #检查必传的字段  name email
    if "name" not in df.columns or "email" not in df.columns:
        raise HTTPException(status_code=400,detail="缺少必要字段name或者email")

    #记录成功的导入量
    imported = 0

    #通过遍历进行数据处理，并将数据插入到数据库中
    """
    for _, row in df.iterrows():
    这是 Pandas 中的 DataFrame.iterrows() 方法，用于按行遍历表格数据,
    
    参数
    df.iterrows() 返回的是每一行的索引和数据，格式是一个 (index, row) 的二元组
    
    for index, row in df.iterrows():
    
    我们的代码中
    for _, row in df.iterrows():
    
    使用了 _ 来忽略 index，意思是**“我不关心这一行的索引”**，只取行的内容 row。
    这是一种 Python 中常见的临时占位变量写法

    
    
    """

    for _,row in df.iterrows():
        #获取name email ，并去除空格
        name = str(row["name"]).strip()
        email = str(row["email"]).strip()

        #获取tags内容
        tags = parse_tags(str(row.get("tags","")))

        #如果其中一个数据不存在，则返回下一个遍历对象
        if not name or not email:
            continue


        #检查邮箱是否存在于数据库中
        email_existing = db.query(models.Customers).filter(models.Customers.email == email).first()
        if email_existing:
            continue

         #构建Customer实例，导入数据库
        customer = models.Customers(
            name=name,
            email=email,
            tags=join_tags(tags)
        )


        #尝试提交
        try:
            db.add(customer)
            db.commit()
            imported += 1
        except IntegrityError:
            db.rollback()       #如果有插入错误则进行事务回滚

    return {"msg":f"成功插入{imported}个客户数据"}














