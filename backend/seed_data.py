from database import SessionLocal, engine, Base
from models import Departement, Formation, Module, Etudiant, Professeur, Batiment, Salle

def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Departement).count() > 0:
            print("Data already exists. Skipping seed.")
            return
        
        # Create departments
        dept_info = Departement(nom="Computer Science")
        dept_math = Departement(nom="Mathematics")
        db.add_all([dept_info, dept_math])
        db.commit()
        
        # Create formations
        formation = Formation(
            nom="License Informatique",
            dept_id=dept_info.id,
            niveau="L3",
            nb_modules=6
        )
        db.add(formation)
        db.commit()
        
        # Create professors
        prof1 = Professeur(nom="Dr. Smith", dept_id=dept_info.id, specialite="Algorithms")
        prof2 = Professeur(nom="Dr. Johnson", dept_id=dept_info.id, specialite="Databases")
        db.add_all([prof1, prof2])
        db.commit()
        
        # Create students
        student1 = Etudiant(
            matricule="2021001",
            nom="Doe",
            prenom="John",
            formation_id=formation.id,
            promo=2021
        )
        db.add(student1)
        db.commit()
        
        # Create buildings and rooms
        building = Batiment(nom="Building A")
        db.add(building)
        db.commit()
        
        salle1 = Salle(nom="A101", capacite=30, type="Amphitheater", batiment_id=building.id)
        db.add(salle1)
        db.commit()
        
        print(" Successfully seeded initial data!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
