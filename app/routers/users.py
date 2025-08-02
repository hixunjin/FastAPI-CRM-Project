from app.schemas import *   #导入 pydantic 模型
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import models, auth
from app.auth import get_session, get_current_user
from pydantic import BaseModel
from typing import List
from app.schemas import UserCreate,UserOut,UserLogin,PasswordUpdate,AdminPasswordUpdate   #导入 pydantic 模型
from fastapi import APIRouter, Depends, HTTPException



#创建应用接口
router = APIRouter()

#普通用户注册接口（不需要登录）
@router.post("/register")
def public_register(user:UserCreate,db:Session = Depends(get_session)):
    """普通用户注册，不用登录"""
    existing = db.query(models.User).filter(models.User.username == user.username).first()
  #检查用户是否存在
    if existing:
        raise HTTPException(status_code=400,detail='用户名已经存在')

    #密码加密
    hashed = auth.hash_password(user.password)
    #创建 User 实例，并未写入数据库
    new_user = models.User(username=user.username,password=hashed,role=user.role)

    #将记录加入到数据库会话中，等待提交
    db.add(new_user)
    db.commit()

    db.refresh(new_user)
    return {"msg":"注册成功！"}

"""

创建管理员账户，需要登录,但是并不是具体的登录功能，它只是需要用户登录并且身份是 admin，
登录验证功能需要在后面编写

功能和登录绑定原理

只要路径操作函数（接口函数）中使用了 current_user: models.User = Depends(get_current_user) 这样的依赖注入，
就代表该接口需要登录验证。

原理：

get_current_user 会自动从请求头中获取并校验 JWT token，只有校验通过（即已登录）才能执行接口逻辑，
否则会直接返回 401 未认证错误。没有用 get_current_user 的接口（如注册、登录）则不需要登录即可访问。

总结：
只要用了 Depends(get_current_user)，就是“需要登录才能访问”的接口。

"""
@router.post('/admin/register')
def admin_register(user:UserCreate,
                   #使用 models.User 作为类型注解，get_current_user 返回的 user 实例将会被 current_user 接收
                   current_user:models.User = Depends(get_current_user),
                   db:Session = Depends(get_session)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403,detail="权限不足")

    #检查要创建的用户是否已经存在
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(400, "用户名已存在")

    #加密
    hashed = auth.hash_password(user.password)
    new_user = models.User(username=user.username, password=hashed, role=user.role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "管理员已创建新用户"}



#定义 docs 文档登录验证功能
#使用  OAuth2PasswordRequestForm，适合在 Swagger UI（docs） 里直接用表单测试，
#因为 Swagger 默认是以 application/x-www-form-urlencoded 方式发送登录请求

@router.post('/login')
def login(
        form_data:OAuth2PasswordRequestForm = Depends(),#注入依赖项，获取登录表单数据
        db:Session = Depends(get_session)):
    #根据表单的 username 查询出数据库中的 username
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # 验证用户名和密码
    if not user or not auth.verify_password(form_data.password,user.password):
        raise HTTPException(status_code=400,detail="账号或者密码错误！")

    #生成 token
    token = auth.create_access_token({'sub':user.username,"role":user.role})

    # 返回 token 和用户角色
    return {"access_token": token, "token_type": "bearer", "role": user.role}


#登录验证功能接口（JSON 格式，前端可用），下面的登录函数供前端使用

"""
两个登录函数的区别

它们的区别就在这一行
form_data: OAuth2PasswordRequestForm = Depends(),
form_data: UserLogin,

"""

@router.post('/login-json')
def login_json(
        form_data:UserLogin,   #请求体，使用 pydantic 模型接收和校验表单数据
        db:Session = Depends(get_session)):
    #根据表单的 username 查询出数据库中的 username
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # 验证用户名和密码
    if not user or not auth.verify_password(form_data.password,user.password):
        raise HTTPException(status_code=400,detail="账号或者密码错误！")

    #生成 token
    token = auth.create_access_token({'sub':user.username,"role":user.role})

    # 返回 token 和用户角色
    return {"access_token": token, "token_type": "bearer", "role": user.role}




#修改密码
@router.post('/change_password')
def change_password(
        data:PasswordUpdate,  #pydantic 模型接收和校验
        current_user:models.User = Depends(get_current_user),  #注入依赖项，接收当前用户对应的数据库实例
        db:Session = Depends(get_session)):
    """验证"""
    if not auth.verify_password(data.old_password,current_user.password):
        raise HTTPException(status_code=400,detail="原密码错误")
    #直接操作数据库实例进行修改密码
    current_user.password = auth.hash_password(data.new_password)
    db.commit()
    return {"msg":"修改成功"}



#管理员修改自己和其它用户的密码
@router.post('/admin/change-password/{username}')
def admin_change_password(
        username:str,   #接收要修改的用户名
        data:AdminPasswordUpdate,  #接收更新密码
        current_user:models.User = Depends(get_current_user),
        db:Session = Depends(get_session)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403,detail="权限不足")

    #查询出管理员选择的用户名对应的数据库记录
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404,detail="要查询的用户不存在")
    user.password = auth.hash_password(data.new_password)
    db.commit()
    return {"msg":"修改成功"}



#管理员查看所有用户
@router.get('/all',response_model=List[UserOut])
def get_all_users(
        db:Session = Depends(get_session),
        current_user:models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403,detail="权限不足")

    #获取所有数据
    users = db.query(models.User).all()

    """
    之所以需要遍历 users，是因为 SQLAlchemy 查询返回的是一组 User 模型对象，而不是字典或 Pydantic 模型。
    你需要把每个 User 实例转换成字典（或 Pydantic 模型）才能作为 JSON 返回
    """
    return [{"username":u.username,"role":u.role} for u in users ]









