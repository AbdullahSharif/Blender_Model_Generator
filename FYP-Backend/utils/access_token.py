from jose import jwt
import os
import datetime
from datetime import timedelta, timezone

# Secret key to sign the JWT token
SECRET_KEY = os.getenv("SECRET_KEY")
# Algorithm used for signing the JWT token
ALGORITHM = os.getenv("ALGORITHM")
# Expiry time for the JWT token (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")



def create_access_token(user_id: str):
    expire = datetime.datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "_id":user_id,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(x_user_auth : str):
    payload = jwt.decode(x_user_auth, SECRET_KEY, algorithms=[ALGORITHM])    
    return payload