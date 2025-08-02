from datetime import datetime, timedelta  ## 导入标准库中的 datetime 和 timedelta，用于处理 token 的创建时间和过期时间

# 使用 `python-jose` 库提供的 JWT 编码和解码功能
# JWTError 是处理 token 异常时用的，jwt 是签发与解码 token 的核心函数
from jose import JWTError, jwt

from passlib.context import CryptContext  # 用于创建密码哈希上下文（比如 bcrypt），负责加密密码和验证密码是否匹配
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session     # SQLAlchemy 中用于数据库操作的 Session 类
from app.database import SessionLocal  # 导入你定义的数据库连接会话工厂，用于生成数据库 Session 实例
from app.models import User


#密码加密初始设置
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

#JWT设置
SECRET_KEY = "your-secret-key"  # 可随机生成
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


#创建登录依赖项
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


#获取 session 操作对象
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#密码加密与校验
def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_passowrd,hashed_password):
    return pwd_context.verify(plain_passowrd,hashed_password)


#JWT 生成
def create_access_token(data:dict,expires_delta:timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


#JWT解析
def decode_token(token:str):
    """
    # 使用 SECRET_KEY 和指定算法对 token 进行解码
    # 解码成功将返回 payload（一个包含用户信息等的字典）
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # 参数是已经配置好的信息
        return payload
    except JWTError:
        raise HTTPException(status_code=401,detail="认证失败")



#获取当前用户，先对前端数据进行解码，再根据解码数据 username 从数据库中获取信息
def get_current_user(token:str=Depends(oauth2_scheme),db:Session = Depends(get_session)):
    #解码
    payload = decode_token(token)
    #获取 username
    username:str = payload.get('sub')

    if username is None:
        raise HTTPException(status_code=401,detail="Token无效")

    #根据 username 从数据库中查询数据
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user





















