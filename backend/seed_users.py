"""
Script to seed the database with example users.
Run this after setting up the database.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, UserRole, Professeur, Etudiant

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt directly, handling version compatibility."""
    try:
        import bcrypt
        # Ensure password is bytes and not longer than 72 bytes
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    except (ImportError, AttributeError):
        # Fallback to passlib if bcrypt has issues
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.hash(password)
        except Exception as e:
            # Last resort: use a simple hash (NOT SECURE, but works for seeding)
            print(f"Warning: Using fallback hashing due to: {e}")
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()

def seed_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if users already exist
        if db.query(User).count() > 0:
            print("Users already exist. Skipping seed.")
            return
        
        # Hash password directly using bcrypt
        password = "password123"
        password_hash = get_password_hash(password)
        
        # Admin user
        admin = User(
            username="admin",
            password_hash=password_hash,
            role=UserRole.ADMIN
        )
        db.add(admin)
        
        # Dean user
        dean = User(
            username="dean",
            password_hash=password_hash,
            role=UserRole.DEAN
        )
        db.add(dean)
        
        # Department Head user
        dept_head = User(
            username="depthead",
            password_hash=password_hash,
            role=UserRole.DEPT_HEAD
        )
        db.add(dept_head)
        
        # Professor users (link to first 3 professors)
        profs = db.query(Professeur).limit(3).all()
        for i, prof in enumerate(profs, 1):
            prof_user = User(
                username=f"prof{i}",
                password_hash=password_hash,
                role=UserRole.PROFESSOR,
                professeur_id=prof.id
            )
            db.add(prof_user)
        
        # Student users (link to first 3 students)
        students = db.query(Etudiant).limit(3).all()
        for i, student in enumerate(students, 1):
            student_user = User(
                username=f"student{i}",
                password_hash=password_hash,
                role=UserRole.STUDENT,
                etudiant_id=student.id
            )
            db.add(student_user)
        
        db.commit()
        print("Successfully seeded users!")
        print("\nExample login credentials:")
        print("Username: admin, Password: password123 (Role: Admin)")
        print("Username: dean, Password: password123 (Role: Dean)")
        print("Username: depthead, Password: password123 (Role: Department Head)")
        print("Username: prof1, Password: password123 (Role: Professor)")
        print("Username: student1, Password: password123 (Role: Student)")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
