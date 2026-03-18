from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor
import time
import random


client = MongoClient("mongodb://localhost:27017")
db = client["university"]

students = db["students"]
enrollments = db["enrollments"]


NUM_REQUESTS = 5000
NUM_THREADS = 20


def find_student():
    student_id = random.randint(1, 100000)
    students.find_one({"student_id": student_id})


def get_enrollments():
    student_id = random.randint(1, 100000)
    list(enrollments.find({"student_id": student_id}))


def insert_student(i):
    students.insert_one({
        "student_id": 2000000 + i,
        "full_name": f"Test User {i}",
        "birth_date": time.time(),
        "gender": "M",
        "department_id": 1,
        "year": 1,
        "email": f"test{i}@mail.com",
        "city": "TestCity"
    })


def run_test(func, label):
    start = time.time()

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        list(executor.map(func, range(NUM_REQUESTS)))

    end = time.time()

    duration = end - start
    rps = NUM_REQUESTS / duration

    print(f"\n=== {label} ===")
    print(f"Total time: {duration:.2f} sec")
    print(f"Throughput: {rps:.2f} ops/sec")


if __name__ == "__main__":
    run_test(lambda _: find_student(), "Find student by student_id")
    run_test(lambda _: get_enrollments(), "Get enrollments by student_id")
    run_test(insert_student, "Insert students")