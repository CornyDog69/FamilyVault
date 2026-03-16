import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
load_dotenv()

MONGO_URI=os.getenv("MONGO_URI","mongodb://localhost:27017/family")# here mongo_uri read url of database of mono atlas from .env file and if it now available then i run loccaly
#this make it run both locally or cloud deployed

client=MongoClient(MONGO_URI)
db= client["Guptavault"]
#COLLECTION(table in sql)
users_col = db["users"]  
documents_col = db["documents"]
otp_codes_col = db["otp_codes"]

users_col.create_index("email",unique=True)
users_col.create_index("username", unique=True)
otp_codes_col.create_index("expires_at",expireAfterSeconds=0)

otp_codes_col.create_index("email")
documents_col.create_index("uploaded_at")