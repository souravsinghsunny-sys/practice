
import os
import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password123@localhost:3306/sourav")
engine = create_engine(DATABASE_URL)
app = FastAPI()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "s3-replication-source-2026-sourav")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    config=Config(signature_version="s3v4")
)

print("Database connection initialized.")

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connected:", result.fetchone())
except Exception as e:
    print(f"Warning: Database connection could not be established on startup: {e}")

    



# Allow frontend to connect with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/students/")
@app.get("/students")
def get_students():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT id, name, age, email, course, city
                FROM students
                ORDER BY id
            """)
        )
       
        students = []               

        for row in result:
            students.append({
                "id": row.id,
                "name": row.name,
                "age": row.age,
                "email": row.email,
                "course": row.course,
                "city": row.city
            })

        return {"students": students}


@app.post("/students/")
@app.post("/students")
def create_student(student: dict):
    with engine.connect() as connection:
        connection.execute(
            text("""
                INSERT INTO students (name, age, email, course, city)
                VALUES (:name, :age, :email, :course, :city)
            """),
            {
                "name": student.get("name"),
                "age": student.get("age"),
                "email": student.get("email"),
                "course": student.get("course"),
                "city": student.get("city")
            }
        )
        connection.commit()

    return {"message": "Student created successfully"}



@app.put("/students/{student_id}/")
@app.put("/students/{student_id}")
def update_student(student_id: int, student: dict):
    with engine.connect() as connection:
        connection.execute(
            text("""
                UPDATE students
                SET name = :name, age = :age, email = :email, course = :course, city = :city
                WHERE id = :id
            """),
            {
                "id": student_id,
                "name": student.get("name"),
                "age": student.get("age"),
                "email": student.get("email"),
                "course": student.get("course"),
                "city": student.get("city")
            }
        )
        connection.commit()

    return {"message": "Student updated successfully"}


# DELETE STUDENT
@app.delete("/students/{student_id}/")
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    with engine.connect() as connection:
        connection.execute(
            text("""
                DELETE FROM students
                WHERE id = :id
            """),
            {"id": student_id}
        )
        connection.commit()

    return {"message": "Student deleted successfully"}
@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Upload file to S3
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file.filename
        )

        # Create a temporary presigned URL
        download_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file.filename,
                "ResponseContentDisposition": "inline"
            },
            ExpiresIn=3600
        )

        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "download_url": download_url
        }
    except NoCredentialsError:
        raise HTTPException(
            status_code=500,
            detail="AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@app.get("/download/{filename}")
async def download_file(filename: str):
    try:
        download_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": filename,
                "ResponseContentDisposition": "inline"
            },
            ExpiresIn=3600
        )

        return {
            "filename": filename,
            "download_url": download_url
        }
    except NoCredentialsError:
        raise HTTPException(
            status_code=500,
            detail="AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )
