from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime


client = MongoClient("mongodb://localhost:27017")
db = client["university"]

students = db["students"]
enrollments = db["enrollments"]


def add_student():
    try:
        student_id = int(input("student_id: "))
        full_name = input("full_name: ")
        birth_date_str = input("birth_date (YYYY-MM-DD): ")
        gender = input("gender (M/F): ")
        department_id = int(input("department_id: "))
        year = int(input("year: "))
        email = input("email: ")
        city = input("city: ")

        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")

        doc = {
            "student_id": student_id,
            "full_name": full_name,
            "birth_date": birth_date,
            "gender": gender,
            "department_id": department_id,
            "year": year,
            "email": email,
            "city": city
        }

        result = students.insert_one(doc)
        print(f"Student added with _id: {result.inserted_id}")
    except ValueError:
        print("Invalid input format.")
    except PyMongoError as e:
        print(f"Database error: {e}")


def find_student():
    try:
        student_id = int(input("student_id: "))
        student = students.find_one(
            {"student_id": student_id},
            {"_id": 0}
        )
        if student:
            print(student)
        else:
            print("Student not found.")
    except ValueError:
        print("student_id must be a number.")
    except PyMongoError as e:
        print(f"Database error: {e}")


def update_student_email():
    try:
        student_id = int(input("student_id: "))
        new_email = input("new email: ")

        result = students.update_one(
            {"student_id": student_id},
            {"$set": {"email": new_email}}
        )

        if result.matched_count:
            print("Email updated.")
        else:
            print("Student not found.")
    except ValueError:
        print("student_id must be a number.")
    except PyMongoError as e:
        print(f"Database error: {e}")


def delete_student():
    try:
        student_id = int(input("student_id: "))

        student_result = students.delete_one({"student_id": student_id})
        enrollment_result = enrollments.delete_many({"student_id": student_id})

        if student_result.deleted_count:
            print(f"Student deleted. Related enrollments deleted: {enrollment_result.deleted_count}")
        else:
            print("Student not found.")
    except ValueError:
        print("student_id must be a number.")
    except PyMongoError as e:
        print(f"Database error: {e}")


def show_student_enrollments():
    try:
        student_id = int(input("student_id: "))
        docs = list(enrollments.find({"student_id": student_id}, {"_id": 0}))

        if docs:
            for doc in docs:
                print(doc)
        else:
            print("No enrollments found.")
    except ValueError:
        print("student_id must be a number.")
    except PyMongoError as e:
        print(f"Database error: {e}")


def menu():
    while True:
        print("\n=== University DB Menu ===")
        print("1. Add student")
        print("2. Find student by student_id")
        print("3. Update student email")
        print("4. Delete student")
        print("5. Show student enrollments")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            find_student()
        elif choice == "3":
            update_student_email()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            show_student_enrollments()
        elif choice == "0":
            print("Bye.")
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    menu()