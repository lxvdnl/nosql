from pymongo import MongoClient, InsertOne
from faker import Faker
from random import randint, choice, sample
from datetime import datetime
import itertools

fake = Faker("ru_RU")

client = MongoClient("mongodb://localhost:27017")
db = client["university"]

departments_col = db["departments"]
teachers_col = db["teachers"]
courses_col = db["courses"]
students_col = db["students"]
enrollments_col = db["enrollments"]


def reset_collections():
    departments_col.delete_many({})
    teachers_col.delete_many({})
    courses_col.delete_many({})
    students_col.delete_many({})
    enrollments_col.delete_many({})


def seed_departments():
    departments = [
        {"department_id": 1, "name": "Computer Science", "building": "A"},
        {"department_id": 2, "name": "Mathematics", "building": "B"},
        {"department_id": 3, "name": "Physics", "building": "C"},
        {"department_id": 4, "name": "Economics", "building": "D"},
        {"department_id": 5, "name": "Biology", "building": "E"},
        {"department_id": 6, "name": "Chemistry", "building": "F"},
        {"department_id": 7, "name": "History", "building": "G"},
        {"department_id": 8, "name": "Philology", "building": "H"},
        {"department_id": 9, "name": "Law", "building": "I"},
        {"department_id": 10, "name": "Engineering", "building": "J"},
    ]
    departments_col.insert_many(departments)


def seed_teachers(n=100):
    docs = []
    for teacher_id in range(1, n + 1):
        docs.append({
            "teacher_id": teacher_id,
            "full_name": fake.name(),
            "department_id": randint(1, 10),
            "email": f"teacher{teacher_id}@university.local",
            "position": choice(["Professor", "Associate Professor", "Lecturer", "Senior Lecturer"])
        })
    teachers_col.insert_many(docs)


def seed_courses(n=200):
    titles = [
        "Databases", "Algorithms", "Linear Algebra", "Discrete Math", "Operating Systems",
        "Computer Networks", "Machine Learning", "Statistics", "Microeconomics", "Macroeconomics",
        "Quantum Physics", "Organic Chemistry", "Genetics", "World History", "Civil Law"
    ]

    docs = []
    for course_id in range(1, n + 1):
        docs.append({
            "course_id": course_id,
            "title": f"{choice(titles)} {course_id}",
            "department_id": randint(1, 10),
            "teacher_id": randint(1, 100),
            "semester": choice(["2025-fall", "2026-spring"]),
            "credits": randint(2, 6)
        })
    courses_col.insert_many(docs)


def generate_students_batch(start_id, batch_size):
    docs = []
    for student_id in range(start_id, start_id + batch_size):
        docs.append({
            "student_id": student_id,
            "full_name": fake.name(),
            "birth_date": datetime.combine(
                fake.date_of_birth(minimum_age=17, maximum_age=25),
                datetime.min.time()
            ),
            "gender": choice(["M", "F"]),
            "department_id": randint(1, 10),
            "year": randint(1, 4),
            "email": f"student{student_id}@university.local",
            "city": fake.city()
        })
    return docs


def seed_students(total=100000, batch_size=5000):
    for start_id in range(1, total + 1, batch_size):
        batch = generate_students_batch(start_id, min(batch_size, total - start_id + 1))
        students_col.insert_many(batch)
        print(f"Inserted students: {start_id} - {start_id + len(batch) - 1}")


def seed_enrollments(total_students=100000, batch_size=5000):
    enrollment_id = 1
    for start_student in range(1, total_students + 1, batch_size):
        operations = []
        end_student = min(start_student + batch_size - 1, total_students)

        for student_id in range(start_student, end_student + 1):
            num_courses = randint(2, 4)
            course_ids = sample(range(1, 201), num_courses)
            for course_id in course_ids:
                operations.append(InsertOne({
                    "enrollment_id": enrollment_id,
                    "student_id": student_id,
                    "course_id": course_id,
                    "semester": choice(["2025-fall", "2026-spring"]),
                    "grade": randint(3, 5),
                    "status": choice(["enrolled", "completed"])
                }))
                enrollment_id += 1

        if operations:
            enrollments_col.bulk_write(operations)
        print(f"Processed enrollments for students: {start_student} - {end_student}")


def main():
    start = datetime.now()
    print("Reset collections...")
    reset_collections()

    print("Seeding departments...")
    seed_departments()

    print("Seeding teachers...")
    seed_teachers()

    print("Seeding courses...")
    seed_courses()

    print("Seeding students...")
    seed_students()

    print("Seeding enrollments...")
    seed_enrollments()

    end = datetime.now()
    print(f"Done in {end - start}")


if __name__ == "__main__":
    main()