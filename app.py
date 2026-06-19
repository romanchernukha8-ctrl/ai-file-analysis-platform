from fastapi import FastAPI, UploadFile, File
import pika
import os

from worker.worker import credentials

app = FastAPI()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
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
