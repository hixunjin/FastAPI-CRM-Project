"""
一、
创建 pydantic 数据校验模型
1.应该知道，无论是前端发来的数据，还是后端响应的数据，一般都会在中间定义 pydantic 模型进行校验、接收、返回响应这三个功能
2.应该根据路径操作函数进行定义 pydantic 模型

二、一般分为三类模型（建议分文件夹存放在 schemas/）
作用	示例	模型名建议
请求模型	前端发数据过来（POST/PUT）	UserCreate, CustomerUpdate
响应模型	返回给前端的数据（GET）	UserOut, CustomerDetail
通用模型	请求/响应都可能用	UserBase, TagSchema 等

"""
from datetime import datetime

from pydantic import BaseModel,EmailStr
from typing import Optional,List
#定义Users请求体模型，对用户数据接收和校验


#pydantic模型:用于接收和校验创建管理员的数据
class UserCreate(BaseModel):
    username:str
    password:str

    #角色，默认为  user
    role:str = "user"

#pydantic模型:接收和校验登录数据
class UserLogin(BaseModel):
    username:str
    password:str

#pydantic模型:修改密码
class AdminPasswordUpdate(BaseModel):
    new_password:str


class PasswordUpdate(BaseModel):
    old_password:str
    new_password:str

#定义pydantic响应模型 UserOut,
#输出用户，用来查看用户信息

class UserOut(BaseModel):
    username:str
    role:str





#客户端模型

#响应模型,id name email tag created_at updated_at
class Customer_Response(BaseModel):
    id:int
    name:str
    email:EmailStr
    tags:List[str]
    created_at:datetime
    updated_at:datetime


    """
    model_config = { "from_attributes": True } 的功能
    这是 Pydantic v2 的配置，作用是让 Pydantic 支持从 ORM 对象（如 SQLAlchemy 的模型实例）自动读取属性，
    实现模型的自动转换。
    等价于 Pydantic v1 的 Config.orm_mode = True。
    有了这个配置，你可以直接返回 SQLAlchemy 的模型对象，Pydantic 会自动把它转换成响应体模型（如 CustomerOut）。
    
    """
    model_config = {
        "from_attributes": True
    }






#定义请求体模型/输入模型，添加客户端信息
#需要的字段:id默认的，name email tags 创建、更新时间

class CreateCustomer(BaseModel):
    name:str
    email:EmailStr

    tags:Optional[List[str]] = None

    #下面两个时间是自动添加的，不用输入数据
    #created_at:datetime
    #updated_at:datetime



#修改模型
#修改哪些数据:name 和 tag

class UpdateCustomer(BaseModel):
    name: Optional[str]
    tags: Optional[List[str]]



#创建响应体模型
#包含字段:id title tags created_time count success_count  fail_count

class ResponseTask(BaseModel):
    id:int
    title:str
    content: str
    tag:Optional[str]     #数据库中的字段为 tag
    created_at:datetime
    total:int
    success:int
    fail:int

    model_config = {
        "from_attributes": True
    }


#请求体模型，接收用户创建邮箱任务数据
#标签，结构为列表，主题，内容
class CreateTask(BaseModel):
    title:str
    content:str
    tag: Optional[str] = None  # 可以填写，也可以为None，代表不选择标签，向所有用户发送邮件









#黑名单模型

#响应模型,id、email、created_at
class BlackEmailResponse(BaseModel):
    id:int
    email:EmailStr
    created_at:datetime
    model_config = {
        "from_attributes": True
    }


#校验模型，添加黑名单，本质就是创建黑名单记录
#只需要设置邮箱字段，另外两个是自己设置的，应该知道，在开发中，id值和数据记录对应的数据一般是默认的，id自增，时间默认当前时间
#不需要用户去设置

class CreateBlackEmail(BaseModel):
    email:EmailStr









