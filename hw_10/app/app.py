import jwt
import bcrypt
import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from model.model import load_model

model = None
app = FastAPI()

# JWT config
SECRET_KEY = "56203a89bb86eeb81f8c4c9245a7faea99134eea14e11665d495bf14b86239fb"
# openssl rand -hex 32 in Linux or using Python:
# import secrets
# print(secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



# User model and database emulation
class User(BaseModel):
    username: str
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


fake_users_db = {
    "user": {
        "username": "user",
        "full_name": "Regular User",
        "email": "user@example.com",
        "hashed_password": bcrypt.hashpw(
            "password".encode("utf-8"), bcrypt.gensalt() # Secure password hashing
        ).decode("utf-8"),
        "disabled": False,
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": bcrypt.hashpw(
            "admin_password".encode("utf-8"), bcrypt.gensalt() # Secure password hashing
        ).decode("utf-8"),
        "disabled": False,
    },
}

# Define user roles
roles = {
    "user": ["user"],
    "admin": ["admin"],
}


# Define request models
class ToxicResponse(BaseModel):
    text: str
    sentiment_label: str
    sentiment_score: float


# Route
@app.get("/")
def index():
    return {"text": "Toxicity Analysis"}


# Load ML model during startup
@app.on_event("startup")
def startup_event():
    global model
    model = load_model()


# Utility functions for authentication
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (
            expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Token route
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Function to verify token and role
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = User(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Role check function
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# FastAPI route handlers
@app.get("/predict", response_model=ToxicResponse)
async def predict_toxicity(text: str, current_user: User = Depends(get_current_active_user)):
    if current_user.username not in roles["user"]:
        raise HTTPException(status_code=403, detail="Operation not permitted.")

    sentiment = model(text)

    response = ToxicResponse(
        text=text,
        sentiment_label=sentiment.label,
        sentiment_score=sentiment.score,
    )

    return response

# uvicorn app.app:app --host 127.0.0.1 --port 8080
