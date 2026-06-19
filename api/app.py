from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from fastapi.responses import FileResponse

import pika
import psycopg2
import os
import redis

UPLOAD_DIR = "uploads"
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=6379,
    decode_responses=True
)

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

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def get_current_user(token: str):

    if redis_client.exists(
        f"blacklist:{token}"
    ):
        raise HTTPException(
            status_code=401,
            detail="Token revoked"
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = int(payload["sub"])

        session = redis_client.get(f"session:user:{user_id}")

        if not session:
            raise HTTPException(
                status_code=401,
                detail="Session expired"
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "")

    user_id = get_current_user(token)

    rate_key = f"upload_limit:{user_id}"

    count = redis_client.incr(rate_key)

    if count == 1:
        redis_client.expire(rate_key, 60)

    if count > 5:
        raise HTTPException(
            status_code=429,
            detail="Too many uploads. Try again later."
        )

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO files
        (
            user_id,
            filename,
            filepath,
            status
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (
            user_id,
            file.filename,
            file_path,
            "uploaded"
        )
    )

    file_id = cur.fetchone()[0]

    conn.commit()

    redis_client.set(
        f"file:{file_id}:status",
        "uploaded",
        ex=3600
    )

    cur.close()
    conn.close()

    credentials = pika.PlainCredentials('admin', 'admin')

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST"),
            credentials=credentials
        )
    )

    channel = connection.channel()

    channel.queue_declare(queue='file_queue')

    channel.basic_publish(
        exchange='',
        routing_key='file_queue',
        body=file.filename
    )

    connection.close()

    return {
        "message": "File uploaded",
        "filename": file.filename
    }

@app.get("/files")
def get_files():

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            user_id,
            filename,
            status
        FROM files
        ORDER BY id DESC
        """
    )

    files = cur.fetchall()

    cur.close()
    conn.close()

    result = []

    for file in files:
        file_id = file[0]

        redis_status = redis_client.get(
            f"file:{file_id}:status"
        )

        status = (
            redis_status
            if redis_status
            else file[3]
        )

        result.append(
            {
                "id": file[0],
                "user_id": file[1],
                "filename": file[2],
                "status": status
            }
        )

    return result

@app.get("/results/{file_id}")
def get_results(file_id: int):

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            file_id,
            pages,
            words,
            symbols
        FROM analysis_results
        WHERE file_id = %s
        """,
        (file_id,)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result is None:
        return {
            "error": "Analysis not found"
        }

    return {
        "file_id": result[0],
        "pages": result[1],
        "words": result[2],
        "symbols": result[3]
    }

@app.get("/document/{file_id}")
def get_document(file_id: int):

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT content
        FROM document_texts
        WHERE file_id = %s
        """,
        (file_id,)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result is None:
        return {
            "error": "Document not found"
        }

    return {
        "file_id": file_id,
        "content": result[0]
    }

@app.get("/ai-analysis/{file_id}")
def get_ai_analysis(file_id: int):

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT analysis
        FROM ai_analysis
        WHERE file_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (file_id,)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result is None:
        return {
            "error": "Analysis not found"
        }

    return {
        "analysis": result[0]
    }

@app.delete("/files/{file_id}")
def delete_file(file_id: int):

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM ai_analysis WHERE file_id=%s",
        (file_id,)
    )

    cur.execute(
        "DELETE FROM document_texts WHERE file_id=%s",
        (file_id,)
    )

    cur.execute(
        "DELETE FROM analysis_results WHERE file_id=%s",
        (file_id,)
    )

    cur.execute(
        "DELETE FROM files WHERE id=%s",
        (file_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "deleted"}

@app.get("/download/{file_id}")
def download_file(file_id: int):

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT generated_file
        FROM files
        WHERE id = %s
        """,
        (file_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        return {
            "error": "File not found"
        }

    if row[0] is None:
        return {
            "error": "Generated file not found"
        }

    return FileResponse(
        path=f"/app/generated_files/{row[0]}",
        filename=row[0],
        media_type="application/pdf"
    )

@app.get("/redis-test")
def redis_test():

    redis_client.set(
        "test_key",
        "Hello Redis"
    )

    value = redis_client.get(
        "test_key"
    )

    return {
        "redis_value": value
    }