from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from .crud import create_user, get_user
from .models import User
from .schemas import UserCreate
from .auth import get_password_hash, create_access_token, oauth2_scheme, verify_password


SECRET_KEY = "1111"  #for simplicity
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup
app = FastAPI()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def read_root():
    return {"Hello": "World"}

def authenticate_user(email: str, password: str):
    user = get_user(email)  
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# Function to get current active user
async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(email)  
    if user is None:
        raise credentials_exception
    return user

# registerr
@app.post("/users/")
def register_user(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password=hashed_password)
    create_user(db_user)
    return {"message": "User created successfully"}

# login and get access token
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# get current user information
@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user