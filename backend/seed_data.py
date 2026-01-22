from database import SessionLocal, engine, Base
from models import (
    Departement, Formation, Module, Etudiant, Professeur,
    Batiment, Salle, Examen, User,
    inscriptions, examens_salles, surveillances
)

def clear_database(db):
    """Delete all existing data from the database"""
    try:
        db.execute(surveillances.delete())
        db.execute(examens_salles.delete())
        db.execute(inscriptions.delete())
        
        db.query(Examen).delete()
        db.query(User).delete()
        
        db.query(Salle).delete()
        db.query(Batiment).delete()
        
        db.query(Etudiant).delete()
        db.query(Professeur).delete()
        
        db.query(Module).delete()
        db.query(Formation).delete()
        db.query(Departement).delete()
        
        db.commit()
        
    except Exception as e:
        db.rollback()


def seed_data():
    """Populate database with initial data"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        clear_database(db)
        
        # ==================== DEPARTMENTS ====================
        dept_cs = Departement(nom="Computer Science")
        dept_math = Departement(nom="Mathematics")
        dept_physics = Departement(nom="Physics")
        dept_engineering = Departement(nom="Engineering")
        
        db.add_all([dept_cs, dept_math, dept_physics, dept_engineering])
        db.commit()
        
        # ==================== FORMATIONS ====================
        formations = [
            Formation(nom="License Informatique L1", dept_id=dept_cs.id, niveau="L1", nb_modules=6),
            Formation(nom="License Informatique L2", dept_id=dept_cs.id, niveau="L2", nb_modules=7),
            Formation(nom="License Informatique L3", dept_id=dept_cs.id, niveau="L3", nb_modules=8),
            Formation(nom="Master Informatique M1", dept_id=dept_cs.id, niveau="M1", nb_modules=6),
            Formation(nom="Master Informatique M2", dept_id=dept_cs.id, niveau="M2", nb_modules=5),
            Formation(nom="License Mathématiques L3", dept_id=dept_math.id, niveau="L3", nb_modules=8),
        ]
        db.add_all(formations)
        db.commit()
        
        formation_l1 = formations[0]
        formation_l2 = formations[1]
        formation_l3 = formations[2]
        formation_m1 = formations[3]
        
        # ==================== PROFESSORS ====================
        professors = [
            Professeur(nom="Dr. Benali Ahmed", dept_id=dept_cs.id, specialite="Algorithms"),
            Professeur(nom="Dr. Mansouri Fatima", dept_id=dept_cs.id, specialite="Databases"),
            Professeur(nom="Dr. Khelifi Karim", dept_id=dept_cs.id, specialite="Networks"),
            Professeur(nom="Dr. Boudiaf Amina", dept_id=dept_cs.id, specialite="Web Development"),
            Professeur(nom="Dr. Saidi Mohamed", dept_id=dept_cs.id, specialite="Artificial Intelligence"),
            Professeur(nom="Dr. Meziane Leila", dept_id=dept_math.id, specialite="Statistics"),
            Professeur(nom="Dr. Hamidi Youssef", dept_id=dept_physics.id, specialite="Quantum Physics"),
            Professeur(nom="Dr. Taleb Nadia", dept_id=dept_engineering.id, specialite="Systems Engineering"),
        ]
        db.add_all(professors)
        db.commit()
        
        # ==================== STUDENTS ====================
        students = [
            Etudiant(matricule="20210001", nom="Benali", prenom="Sarah", formation_id=formation_l3.id, promo=2021),
            Etudiant(matricule="20210002", nom="Meziane", prenom="Ali", formation_id=formation_l3.id, promo=2021),
            Etudiant(matricule="20210003", nom="Boudiaf", prenom="Leila", formation_id=formation_l3.id, promo=2021),
            Etudiant(matricule="20210004", nom="Khelifi", prenom="Omar", formation_id=formation_l3.id, promo=2021),
            Etudiant(matricule="20210005", nom="Saidi", prenom="Nour", formation_id=formation_l3.id, promo=2021),
            Etudiant(matricule="20220001", nom="Amrani", prenom="Karim", formation_id=formation_m1.id, promo=2022),
            Etudiant(matricule="20220002", nom="Djelloul", prenom="Amina", formation_id=formation_m1.id, promo=2022),
            Etudiant(matricule="20220003", nom="Ferhat", prenom="Yacine", formation_id=formation_m1.id, promo=2022),
            Etudiant(matricule="20220004", nom="Hadj", prenom="Rania", formation_id=formation_l2.id, promo=2022),
            Etudiant(matricule="20220005", nom="Khaled", prenom="Sofiane", formation_id=formation_l2.id, promo=2022),
        ]
        db.add_all(students)
        db.commit()
        
        # ==================== MODULES ====================
        modules = [
            Module(nom="Algorithms & Data Structures", credits=6, formation_id=formation_l3.id),
            Module(nom="Database Systems", credits=6, formation_id=formation_l3.id),
            Module(nom="Operating Systems", credits=5, formation_id=formation_l3.id),
            Module(nom="Computer Networks", credits=5, formation_id=formation_l3.id),
            Module(nom="Software Engineering", credits=6, formation_id=formation_l3.id),
            Module(nom="Web Technologies", credits=5, formation_id=formation_l3.id),
            Module(nom="Advanced Algorithms", credits=6, formation_id=formation_m1.id),
            Module(nom="Machine Learning", credits=6, formation_id=formation_m1.id),
            Module(nom="Distributed Systems", credits=5, formation_id=formation_m1.id),
            Module(nom="Data Mining", credits=5, formation_id=formation_m1.id),
            Module(nom="Programming Fundamentals", credits=6, formation_id=formation_l2.id),
            Module(nom="Discrete Mathematics", credits=5, formation_id=formation_l2.id),
        ]
        db.add_all(modules)
        db.commit()
        
        # ==================== BUILDINGS & ROOMS ====================
        buildings = [
            Batiment(nom="Building A - Sciences"),
            Batiment(nom="Building B - Engineering"),
            Batiment(nom="Building C - Mathematics"),
        ]
        db.add_all(buildings)
        db.commit()
        
        building_a = buildings[0]
        building_b = buildings[1]
        building_c = buildings[2]
        
        rooms = [
            Salle(nom="A101", capacite=50, type="Amphitheater", batiment_id=building_a.id),
            Salle(nom="A102", capacite=30, type="Classroom", batiment_id=building_a.id),
            Salle(nom="A103", capacite=25, type="Lab", batiment_id=building_a.id),
            Salle(nom="A201", capacite=40, type="Classroom", batiment_id=building_a.id),
            Salle(nom="B101", capacite=100, type="Amphitheater", batiment_id=building_b.id),
            Salle(nom="B102", capacite=35, type="Classroom", batiment_id=building_b.id),
            Salle(nom="B201", capacite=60, type="Amphitheater", batiment_id=building_b.id),
            Salle(nom="C101", capacite=80, type="Amphitheater", batiment_id=building_c.id),
            Salle(nom="C102", capacite=30, type="Classroom", batiment_id=building_c.id),
            Salle(nom="C103", capacite=20, type="Lab", batiment_id=building_c.id),
        ]
        db.add_all(rooms)
        db.commit()
        
        # ==================== STUDENT ENROLLMENTS ====================
        l3_modules = [m for m in modules if m.formation_id == formation_l3.id]
        l3_students = [s for s in students if s.formation_id == formation_l3.id]
        for student in l3_students:
            for module in l3_modules:
                db.execute(inscriptions.insert().values(
                    etudiant_id=student.id,
                    module_id=module.id
                ))
        
        m1_modules = [m for m in modules if m.formation_id == formation_m1.id]
        m1_students = [s for s in students if s.formation_id == formation_m1.id]
        for student in m1_students:
            for module in m1_modules:
                db.execute(inscriptions.insert().values(
                    etudiant_id=student.id,
                    module_id=module.id
                ))
        
        l2_modules = [m for m in modules if m.formation_id == formation_l2.id]
        l2_students = [s for s in students if s.formation_id == formation_l2.id]
        for student in l2_students:
            for module in l2_modules:
                db.execute(inscriptions.insert().values(
                    etudiant_id=student.id,
                    module_id=module.id
                ))
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
