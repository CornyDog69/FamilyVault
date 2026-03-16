import os
from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException,Response,status
from pydantic import BaseModel,EmailStr
from backend.database import users_col
from backend.otp_service import(
    check_rate_limit,generate_otp,send_otp_email,store_otp,verify_otp,)
from backend.auth import create_access_token,get_current_user,is_email_allowed

router=APIRouter(prefix="/api/auth",tags=["auth"])
COOKIE_SETTINGS=dict(key="access_token",httponly=True,max_age=60*60*72,samesite="lax",secure=False,)
class EmailRequest(BaseModel):
    email:EmailStr
class OTPVerifyRequest(BaseModel):
    email:EmailStr
    otp:str
class SetUsernameRequest(BaseModel):
    email: EmailStr
    username:str



@router.post("/request-otp")
async def request_otp(body:EmailRequest):
    email=body.email.lower()
    if not is_email_allowed(email):
        raise HTTPException(status_code=403,detail="Your not Allowed")
    if not check_rate_limit(email):
        raise HTTPException(status_code=429,detail="Too many otp requests. Try again Later")
    otp=generate_otp()
    store_otp(email,otp)
    if not send_otp_email(email,otp):
        raise HTTPException(status_code=500,detail="Failed to send OTP")
    return{"message":"OTP sent, check ur mail"}

@router.post("/verify-otp")
async def verify_otp_endpoint(body:OTPVerifyRequest,response:Response):
    email=body.email.lower()
    if not is_email_allowed(email):
        raise HTTPException(status_code=403,detail="Your not Allowed")
    if not verify_otp(email,body.otp):
        raise HTTPException(status_code=401,detail="Invalid/expired otp")
    user=users_col.find_one({"email":email})
    is_new= user is None
    if not is_new:
        token=create_access_token(email)
        response.set_cookie(value=token,**COOKIE_SETTINGS)
    return {"message":"OTP verified","needs_username":is_new,"email":email}

@router.post("/set-username")
async def set_username(body: SetUsernameRequest,response:Response):
    email=body.email.lower()
    if not is_email_allowed(email):
        raise HTTPException(status_code=403,detail="Your not Allowed")
    username=body.username.strip()
    if len(username)<2 or len(username)>40:
        raise HTTPException(status_code=400,detail="Username must be 2-40 character")
    if users_col.find_one({"email": email}):
        raise HTTPException(status_code=400,detail="User already registered")
    users_col.insert_one({"email":email,"username":username,"created_at":datetime.utcnow()})
    token=create_access_token(email)
    response.set_cookie(value=token,**COOKIE_SETTINGS)
    return {"message":"WELCOME TO FAMILY","username":username}

@router.post("/logout")
async def logout (response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged Out"}

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return{
        "email" : current_user["email"],
        "username": current_user.get("username",""),
        "is_admin": current_user["email"].lower()==os.getenv("ADMIN_EMAIL","").lower(),
    }