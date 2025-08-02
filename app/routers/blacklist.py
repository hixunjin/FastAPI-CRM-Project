from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.auth import get_session, get_current_user
from typing import List
from app.schemas import BlackEmailResponse,CreateBlackEmail

router = APIRouter()


#查询黑名单记录

@router.get('/GetBlackEmail',response_model=List[BlackEmailResponse])
def GetBlackEmail(
        current_user:models.User = Depends(get_current_user),
        db:Session = Depends(get_session)
):
    #获取所有记录
    all_black_email = db.query(models.EmailBlackList).order_by(models.EmailBlackList.created_at.desc()).all()
    return all_black_email



#添加/创建黑名单记录
#只需要添加一个邮箱即可
@router.post('/AddBlackEmail',response_model=BlackEmailResponse)
def AddBlackEmail(
        balck_email:CreateBlackEmail,
        current_user:models.User = Depends(get_current_user),
        db:Session = Depends(get_session)
):
    #校验数据库中是否已经存在邮箱
    get_email = db.query(models.EmailBlackList).filter(models.EmailBlackList.email == balck_email.email).first()
    if get_email:
        raise HTTPException(status_code=400,detail="用户邮箱已经存在")

    #不存在，添加
    current_email = models.EmailBlackList(email = balck_email.email)
    db.add(current_email)
    db.commit()
    db.refresh(current_email)
    return current_email



#删除黑名单记录,根据前端传过来的id值删除记录

@router.delete('/Delete/{email}')
def DeleteEmail(
        email:str,
        current_user:models.User = Depends(get_current_user),
        db:Session = Depends(get_session),

):
    #查询记录
    get_email = db.query(models.EmailBlackList).filter(models.EmailBlackList.email == email).first()

    #检查查询结果
    if not get_email:
        raise HTTPException(status_code=404,detail="用户邮箱不存在")

    #删除记录
    db.delete(get_email)
    db.commit()
    return {"msg":"删除成功!"}







