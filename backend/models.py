from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum

# User roles enum
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DEAN = "dean"
    DEPT_HEAD = "dept_head"
    PROFESSOR = "professor"
    STUDENT = "student"

# User model for authentication
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    # Optional: link to specific entity (professor or student)
    professeur_id = Column(Integer, ForeignKey("professeurs.id"), nullable=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=True)

# Association tables
inscriptions = Table(
    'inscriptions',
    Base.metadata,
    Column('etudiant_id', Integer, ForeignKey('etudiants.id'), primary_key=True),
    Column('module_id', Integer, ForeignKey('modules.id'), primary_key=True)
)

examens_salles = Table(
    'examens_salles',
    Base.metadata,
    Column('examen_id', Integer, ForeignKey('examens.id'), primary_key=True),
    Column('salle_id', Integer, ForeignKey('salles.id'), primary_key=True)
)

surveillances = Table(
    'surveillances',
    Base.metadata,
    Column('examen_id', Integer, ForeignKey('examens.id'), primary_key=True),
    Column('prof_id', Integer, ForeignKey('professeurs.id'), primary_key=True)
)

class Departement(Base):
    __tablename__ = "departements"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    
    formations = relationship("Formation", back_populates="departement")
    professeurs = relationship("Professeur", back_populates="departement")

class Formation(Base):
    __tablename__ = "formations"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(150), nullable=False)
    dept_id = Column(Integer, ForeignKey("departements.id"))
    niveau = Column(String(10))
    nb_modules = Column(Integer)
    
    departement = relationship("Departement", back_populates="formations")
    modules = relationship("Module", back_populates="formation")
    etudiants = relationship("Etudiant", back_populates="formation")

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(150))
    credits = Column(Integer)
    formation_id = Column(Integer, ForeignKey("formations.id"))
    
    formation = relationship("Formation", back_populates="modules")
    examens = relationship("Examen", back_populates="module")
    etudiants = relationship("Etudiant", secondary=inscriptions, back_populates="modules")

class Etudiant(Base):
    __tablename__ = "etudiants"
    id = Column(Integer, primary_key=True, index=True)
    matricule = Column(String(20), unique=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    formation_id = Column(Integer, ForeignKey("formations.id"))
    promo = Column(Integer)
    
    formation = relationship("Formation", back_populates="etudiants")
    modules = relationship("Module", secondary=inscriptions, back_populates="etudiants")

class Professeur(Base):
    __tablename__ = "professeurs"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    dept_id = Column(Integer, ForeignKey("departements.id"))
    specialite = Column(String(100))
    
    departement = relationship("Departement", back_populates="professeurs")
    examens = relationship("Examen", secondary=surveillances, back_populates="professeurs")

class Batiment(Base):
    __tablename__ = "batiments"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    
    salles = relationship("Salle", back_populates="batiment")

class Salle(Base):
    __tablename__ = "salles"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50))
    capacite = Column(Integer)
    type = Column(String(20))
    batiment_id = Column(Integer, ForeignKey("batiments.id"))
    
    batiment = relationship("Batiment", back_populates="salles")
    examens = relationship("Examen", secondary=examens_salles, back_populates="salles")

class Examen(Base):
    __tablename__ = "examens"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    date = Column(Date)
    heure = Column(Time)
    duree = Column(Integer)
    dept_head_approved = Column(Integer, default=0)  # 0 = pending, 1 = approved, -1 = rejected
    vice_dean_approved = Column(Integer, default=0)  # 0 = pending, 1 = approved, -1 = rejected
    
    module = relationship("Module", back_populates="examens")
    salles = relationship("Salle", secondary=examens_salles, back_populates="examens")
    professeurs = relationship("Professeur", secondary=surveillances, back_populates="examens")
