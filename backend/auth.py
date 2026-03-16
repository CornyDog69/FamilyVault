import os
from datetime import datetime,timedelta
from typing import Optional
from fastapi import Depends,HTTPException,status,Cookie
from jose import JWTError,jwt   #json web token: it stores the seesion on token instead of db
from dotenv import load_dotenv

from backend.database import users_col

load_dotenv
JWT_SECRET= os.getenv("JWT_SECRET","") # jwt-secret is the key set in .env via which server verifies token
JWT_ALGORITHM="HS256" #  afixed widely used algo for jwt
JWT_EXPIRE_HOURS=72

def create_access_token(email:str)-> str:
    payload={
        "sub":email, # to whom token belong
        "exp": datetime.utcnow()+ timedelta(hours=JWT_EXPIRE_HOURS), # token expiry
        "iat": datetime.utcnow(),
    }
    return  jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Optional[str]:
    try:
        payload=jwt.decode(token,JWT_SECRET,algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

def get_current_user(access_token: Optional[str]= Cookie(default=None)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="NOT REGISTERED",)
    email=decode_token(access_token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="INVALID",)
    user=users_col.find_one({"email":email})
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="USER NOT FOUND",)
    return user

def get_allowed_emails()-> set[str]:
    allowed=set()
    admin=os.getenv("ADMIN_EMAIL","").strip().lower()
    if admin:
        allowed.add(admin)
    raw=os.getenv("ALLOWED_EMAILS","")
    for e in raw.split(","):
        e=e.strip().lower()
        if e:
            allowed.add(e)
    return allowed

def is_email_allowed(email:str)-> bool:
    return email.strip().lower() in get_allowed_emails()


def is_admin(user:dict)->bool:
    admin_email = os.getenv("ADMIN_EMAIL","")
    return user.get("email","").lower() == admin_email.lower()

def require_admin(current_user: dict= Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="YOUR NOT ISHAN",)
    return current_user