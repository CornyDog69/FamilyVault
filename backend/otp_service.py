import os
import random
import smtplib #for calling SMTP services
import string
from datetime import datetime,timedelta
from email.mime.multipart import MIMEMultipart # for making html emails
from email.mime.text import MIMEText
import secrets
from dotenv import load_dotenv
from backend.database import otp_codes_col

load_dotenv
SMTP_HOST=os.getenv("SMTP_HOST","smtp.gmail.com")
SMTP_PORT=int(os.getenv("SMTP_PORT",587))
SMTP_USER= os.getenv("SMTP_USER","")
SMTP_PASS= os.getenv("SMTP_PASS","")
APP_NAME=os.getenv("APP_NAME","Family Document Vault")

OTP_EXPIRY_MINUTES=5
MAX_OTP_REQUESTS_PER_HOUR=5

def generate_otp()-> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))

def check_rate_limit(email:str)-> bool:
    one_hour_ago=datetime.utcnow()-timedelta(hours=1)
    count= otp_codes_col.count_documents({"email":email,"created_at":{"$gte":one_hour_ago}})
    return count<MAX_OTP_REQUESTS_PER_HOUR

def store_otp(email:str,otp:str)->None:
    otp_codes_col.delete_many({"email":email})
    otp_codes_col.insert_one ({
        "email":email,
        "otp":otp,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow()+timedelta(minutes=OTP_EXPIRY_MINUTES),
    })

def verify_otp(email:str,otp:str)->  bool:
    record=otp_codes_col.find_one({
        "email":email,
        "otp":otp,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    if record:
        otp_codes_col.delete_many({"email":email})
        return True
    return False


def send_otp_email(email:str,otp:str)-> bool:
    try:
        msg=  MIMEMultipart("alternative")
        msg["Subject"]=f"Your {APP_NAME}Login Code"
        msg["From"]=SMTP_USER
        msg["To"]=email

        html_body=f"""
        <html>
        <body style="font-family: Georgia, serif; background: #f9f6f0; padding: 40px;">
          <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 12px;
                      padding: 40px; border: 1px solid #e8e0d0; box-shadow: 0 4px 20px rgba(0,0,0,0.06);">
            <h2 style="color: #2c1810; font-size: 24px; margin-bottom: 8px;"> {APP_NAME}</h2>
            <p style="color: #6b5c4e; font-size: 15px; margin-bottom: 28px;">
              Your one time login code is:
            </p>
            <div style="background: #2c1810; color: #f5efe6; font-size: 36px; font-weight: bold;
                        letter-spacing: 12px; text-align: center; padding: 20px; border-radius: 8px;
                        margin-bottom: 24px;">
              {otp}
            </div>
            <p style="color: #9e8e80; font-size: 13px;">
              code expires in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.
            </p>
          </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body,"html"))
        with smtplib.SMTP(SMTP_HOST,SMTP_PORT)as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER,SMTP_PASS)
            server.sendmail(SMTP_USER,email,msg.as_string())
        
        return True
    except Exception as e:
        print(f"[EMAIL ERROR]{e}")
        return False

