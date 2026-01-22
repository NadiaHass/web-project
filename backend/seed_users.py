"""
Script to seed the database with example users.
Run this after setting up the database and seeding data.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, UserRole, Professeur, Etudiant


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt directly, handling version compatibility."""
    try:
        import bcrypt
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    except (ImportError, AttributeError):
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.hash(password)
        except Exception as e:
            print(f"Warning: Using fallback hashing due to: {e}")
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()


def seed_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Users already exist ({existing_users} users found). Skipping seed.")
            return
        
        password = "password123"
        password_hash = get_password_hash(password)
        
        users_created = 0
        
        # 1. Admin user
        admin = User(username="admin", password_hash=password_hash, role=UserRole.ADMIN)
        db.add(admin)
        users_created += 1
        print(" Created admin user")
        
        # 2. Dean user
        dean = User(username="dean", password_hash=password_hash, role=UserRole.DEAN)
        db.add(dean)
        users_created += 1
        print(" Created dean user")
        
        # 3. Department Head user
        dept_head = User(username="depthead", password_hash=password_hash, role=UserRole.DEPT_HEAD)
        db.add(dept_head)
        users_created += 1
        print(" Created depthead user")
        
        # Commit first 3 users
        db.commit()
        
        # 4. Professor users - Check if professors exist
        profs = db.query(Professeur).limit(5).all()
        print(f"Found {len(profs)} professors in database")
        
        if len(profs) == 0:
            print("  WARNING: No professors found. Skipping professor user creation.")
            print("   Make sure seed_data.py runs before seed_users.py")
        else:
            for i, prof in enumerate(profs, 1):
                try:
                    prof_user = User(
                        username=f"prof{i}",
                        password_hash=password_hash,
                        role=UserRole.PROFESSOR,
                        professeur_id=prof.id
                    )
                    db.add(prof_user)
                    users_created += 1
                    print(f" Created prof{i} user (linked to professor: {prof.nom})")
                except Exception as e:
                    print(f" Failed to create prof{i}: {e}")
            db.commit()
        
        # 5. Student users - Check if students exist
        students = db.query(Etudiant).limit(5).all()
        print(f"Found {len(students)} students in database")
        
        if len(students) == 0:
            print("  WARNING: No students found. Skipping student user creation.")
            print("   Make sure seed_data.py runs before seed_users.py")
        else:
            for i, student in enumerate(students, 1):
                try:
                    student_user = User(
                        username=f"student{i}",
                        password_hash=password_hash,
                        role=UserRole.STUDENT,
                        etudiant_id=student.id
                    )
                    db.add(student_user)
                    users_created += 1
                    print(f" Created student{i} user (linked to: {student.prenom} {student.nom})")
                except Exception as e:
                    print(f" Failed to create student{i}: {e}")
            db.commit()
        
        print(f"\n Successfully seeded {users_created} users!")
        print("\n Login credentials (password for all: password123):")
        print("   • admin - Administrator")
        print("   • dean - Dean")
        print("   • depthead - Department Head")
        if len(profs) > 0:
            print(f"   • prof1 to prof{len(profs)} - Professors")
        if len(students) > 0:
            print(f"   • student1 to student{len(students)} - Students")
        
    except Exception as e:
        db.rollback()
        print(f" Error seeding users: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
