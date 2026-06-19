from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import psycopg2
import redis
import os


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                "http://192.168.49.2:30522"
                   ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = os.getenv("JWT_SECRET")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = 60
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=6379,
    decode_responses=True
)

class UserRegister(BaseModel):
    email: str
    password: str


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

class UserLogin(BaseModel):
    email: str
    password: str

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {"exp": expire}
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


@app.post("/register")
def register(user: UserRegister):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE email = %s",
        (user.email,)
    )

    if cur.fetchone():
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    password_hash = pwd_context.hash(
        user.password
    )

    cur.execute(
        """
        INSERT INTO users
        (email, password_hash)
        VALUES (%s, %s)
        """,
        (
            user.email,
            password_hash
        )
    )

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "User created"
    }

@app.post("/login")
def login(user: UserLogin):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, password_hash
        FROM users
        WHERE email = %s
        """,
        (user.email,)
    )

    db_user = cur.fetchone()

    cur.close()
    conn.close()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    user_id, password_hash = db_user

    if not pwd_context.verify(
        user.password,
        password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {
            "sub": str(user_id),
            "email": user.email
        }
    )

    redis_client.set(
        f"session:user:{user_id}",
        user.email,
        ex=3600
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/logout")
def logout(token: str):

    redis_client.set(
        f"blacklist:{token}",
        "true",
        ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {
        "message": "Logged out"
    }
