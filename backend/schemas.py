from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional

# Department schemas
class DepartementBase(BaseModel):
    nom: str

class DepartementCreate(DepartementBase):
    pass

class Departement(DepartementBase):
    id: int
    class Config:
        from_attributes = True

# Formation schemas
class FormationBase(BaseModel):
    nom: str
    dept_id: int
    niveau: Optional[str] = None
    nb_modules: Optional[int] = None

class FormationCreate(FormationBase):
    pass

class Formation(FormationBase):
    id: int
    class Config:
        from_attributes = True

# Module schemas
class ModuleBase(BaseModel):
    nom: str
    credits: Optional[int] = None
    formation_id: int

class ModuleCreate(ModuleBase):
    pass

class Module(ModuleBase):
    id: int
    class Config:
        from_attributes = True

# Student schemas
class EtudiantBase(BaseModel):
    matricule: str
    nom: str
    prenom: str
    formation_id: int
    promo: int

class EtudiantCreate(EtudiantBase):
    pass

class Etudiant(EtudiantBase):
    id: int
    class Config:
        from_attributes = True

# Professor schemas
class ProfesseurBase(BaseModel):
    nom: str
    dept_id: int
    specialite: Optional[str] = None

class ProfesseurCreate(ProfesseurBase):
    pass

class Professeur(ProfesseurBase):
    id: int
    class Config:
        from_attributes = True

# Building schemas
class BatimentBase(BaseModel):
    nom: str

class BatimentCreate(BatimentBase):
    pass

class Batiment(BatimentBase):
    id: int
    class Config:
        from_attributes = True

# Room schemas
class SalleBase(BaseModel):
    nom: str
    capacite: int
    type: str
    batiment_id: int

class SalleCreate(SalleBase):
    pass

class Salle(SalleBase):
    id: int
    class Config:
        from_attributes = True

# Exam schemas
class ExamenBase(BaseModel):
    module_id: int
    date: date
    heure: time
    duree: int

class ExamenCreate(ExamenBase):
    salle_ids: List[int] = []
    prof_ids: List[int] = []

class Examen(ExamenBase):
    id: int
    dept_head_approved: int = 0
    vice_dean_approved: int = 0
    class Config:
        from_attributes = True

class ExamenApprovalRequest(BaseModel):
    approved: bool  # True = approve, False = reject

# Timetable generation
class TimetableRequest(BaseModel):
    start_date: date
    end_date: date
    exam_start_time: time = time(9, 0)
    exam_end_time: time = time(17, 0)

class TimetableResponse(BaseModel):
    success: bool
    message: str
    conflicts: List[dict] = []
    generated_exams: int = 0

# Conflict detection
class ConflictInfo(BaseModel):
    type: str
    description: str
    details: dict

class StatisticsResponse(BaseModel):
    total_students: int
    total_professors: int
    total_exams: int
    room_utilization: dict
    department_stats: List[dict]
    conflict_count: int

# Authentication schemas
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int

class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    professeur_id: Optional[int] = None
    etudiant_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    professeur_id: Optional[int] = None
    etudiant_id: Optional[int] = None
    class Config:
        from_attributes = True