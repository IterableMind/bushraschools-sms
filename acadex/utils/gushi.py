from faker import Faker
import random
from ..models import Student, db, SchoolBranch  # Adjust imports if needed

def generate_random_students(num_students):
    fake = Faker()
    added = 0  # Track number of successfully added students

    while added < num_students:
        adm_no = str(random.randint(25000, 50000))

        # Ensure adm_no is unique
        if Student.query.filter_by(adm_no=adm_no).first():
            continue

        branches = SchoolBranch.query.all()
        if not branches:
            print("No school branches found.")
            return

        branch = random.choice(branches)

        # Determine allowed grades based on branch name
        if branch.name == 'Bushra High School':
            allowed_grades = ["Grade 8", "Grade 9", "Form 2", "Form 3"]
        elif 'Academy' in branch.name:
            allowed_grades = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6", "Grade 7"]
        elif branch.name == 'Khyrat':
            allowed_grades = [
                "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
                "Grade 7", "Grade 8", "Grade 9", "Form 2", "Form 3"
            ]
        else:
            allowed_grades = [  # Default if other branches are there (you can adjust this)
                "Grade 1", "Grade 2", "Grade 3", "Grade 4",
                "Grade 5", "Grade 6", "Grade 7", "Grade 8",
                "Grade 9", "Form 2", "Form 3", "Form 4"
            ]

        # Pick a random grade from allowed ones
        grade = random.choice(allowed_grades)
        gender = random.choice(["Male", "Female"])

        stream = None
        if 'Academy' in branch.name and grade in ["Grade 4", "Grade 5"]:
            stream = random.choice(["West", "East"])

        parent_name = fake.name()
        contact_phone = fake.phone_number()
        health_info = fake.sentence() if random.random() > 0.5 else None

        student = Student(
            fullname=fake.name(),
            grade=grade,
            adm_no=adm_no,
            gender=gender,
            stream=stream,
            parent_name=parent_name,
            contact_phone=contact_phone,
            health_info=health_info,
            branch=branch
        )

        db.session.add(student)
        added += 1

    db.session.commit()
    db.session.close()
    print(f"{num_students} students added successfully.")
