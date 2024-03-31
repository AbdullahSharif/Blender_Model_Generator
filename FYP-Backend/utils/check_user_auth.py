from fastapi import Header

async def check_user_auth(x_user_auth: str = Header()):
    if x_user_auth is None:
        return {"error": "Please login!"}
    return x_user_auth
