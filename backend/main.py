
from sqlalchemy import create_engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
DATABASE_URL = "mysql+pymysql://root:password123@localhost:3306/sourav"
engine = create_engine(DATABASE_URL)
app = FastAPI()

print("Database connection initialized.")

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print(result.fetchone())
    



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

