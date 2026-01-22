from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, time, timedelta
from typing import List

from database import get_db, engine, Base
from models import (
    Departement, Formation, Module, Etudiant, Professeur,
    Batiment, Salle, Examen, inscriptions, surveillances, examens_salles,
    User, UserRole
)
from schemas import (
    Departement as DepartementSchema, DepartementCreate,
    Formation as FormationSchema, FormationCreate,
    Module as ModuleSchema, ModuleCreate,
    Etudiant as EtudiantSchema, EtudiantCreate,
    Professeur as ProfesseurSchema, ProfesseurCreate,
    Batiment as BatimentSchema, BatimentCreate,
    Salle as SalleSchema, SalleCreate,
    Examen as ExamenSchema, ExamenCreate, ExamenApprovalRequest,
    TimetableRequest, TimetableResponse, StatisticsResponse, ConflictInfo,
    UserLogin, Token, UserCreate, UserResponse
)
from timetable_generator import TimetableGenerator
from auth import (
    authenticate_user, create_access_token, get_current_user,
    get_password_hash, require_role, ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Exam Timetable Optimization Platform")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# ==================== AUTHENTICATION ====================
@app.post("/api/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value,
        "user_id": user.id
    }

@app.post("/api/auth/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Validate role
    try:
        role = UserRole(user_data.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        role=role,
        professeur_id=user_data.professeur_id,
        etudiant_id=user_data.etudiant_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# ==================== DEPARTMENTS ====================
@app.get("/api/departements", response_model=List[DepartementSchema])
def get_departements(db: Session = Depends(get_db)):
    return db.query(Departement).all()

@app.post("/api/departements", response_model=DepartementSchema)
def create_departement(departement: DepartementCreate, db: Session = Depends(get_db)):
    db_departement = Departement(**departement.dict())
    db.add(db_departement)
    db.commit()
    db.refresh(db_departement)
    return db_departement

# ==================== FORMATIONS ====================
@app.get("/api/formations", response_model=List[FormationSchema])
def get_formations(dept_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Formation)
    if dept_id:
        query = query.filter(Formation.dept_id == dept_id)
    return query.all()

@app.post("/api/formations", response_model=FormationSchema)
def create_formation(formation: FormationCreate, db: Session = Depends(get_db)):
    db_formation = Formation(**formation.dict())
    db.add(db_formation)
    db.commit()
    db.refresh(db_formation)
    return db_formation

# ==================== MODULES ====================
@app.get("/api/modules", response_model=List[ModuleSchema])
def get_modules(formation_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Module)
    if formation_id:
        query = query.filter(Module.formation_id == formation_id)
    return query.all()

@app.post("/api/modules", response_model=ModuleSchema)
def create_module(module: ModuleCreate, db: Session = Depends(get_db)):
    db_module = Module(**module.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

# ==================== STUDENTS ====================
@app.get("/api/etudiants", response_model=List[EtudiantSchema])
def get_etudiants(formation_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Etudiant)
    if formation_id:
        query = query.filter(Etudiant.formation_id == formation_id)
    return query.all()

@app.post("/api/etudiants", response_model=EtudiantSchema)
def create_etudiant(etudiant: EtudiantCreate, db: Session = Depends(get_db)):
    db_etudiant = Etudiant(**etudiant.dict())
    db.add(db_etudiant)
    db.commit()
    db.refresh(db_etudiant)
    return db_etudiant

# ==================== PROFESSORS ====================
@app.get("/api/professeurs", response_model=List[ProfesseurSchema])
def get_professeurs(dept_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Professeur)
    if dept_id:
        query = query.filter(Professeur.dept_id == dept_id)
    return query.all()

@app.post("/api/professeurs", response_model=ProfesseurSchema)
def create_professeur(professeur: ProfesseurCreate, db: Session = Depends(get_db)):
    db_professeur = Professeur(**professeur.dict())
    db.add(db_professeur)
    db.commit()
    db.refresh(db_professeur)
    return db_professeur

# ==================== BUILDINGS ====================
@app.get("/api/batiments", response_model=List[BatimentSchema])
def get_batiments(db: Session = Depends(get_db)):
    return db.query(Batiment).all()

@app.post("/api/batiments", response_model=BatimentSchema)
def create_batiment(batiment: BatimentCreate, db: Session = Depends(get_db)):
    db_batiment = Batiment(**batiment.dict())
    db.add(db_batiment)
    db.commit()
    db.refresh(db_batiment)
    return db_batiment

# ==================== ROOMS ====================
@app.get("/api/salles", response_model=List[SalleSchema])
def get_salles(batiment_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Salle)
    if batiment_id:
        query = query.filter(Salle.batiment_id == batiment_id)
    return query.all()

@app.post("/api/salles", response_model=SalleSchema)
def create_salle(salle: SalleCreate, db: Session = Depends(get_db)):
    db_salle = Salle(**salle.dict())
    db.add(db_salle)
    db.commit()
    db.refresh(db_salle)
    return db_salle

# ==================== EXAMS ====================
@app.get("/api/examens", response_model=List[ExamenSchema])
def get_examens(
    module_id: int = None, 
    start_date: date = None, 
    end_date: date = None,
    include_pending: bool = False,  # For admins/dept heads/deans to see all
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Examen)
    if module_id:
        query = query.filter(Examen.module_id == module_id)
    if start_date:
        query = query.filter(Examen.date >= start_date)
    if end_date:
        query = query.filter(Examen.date <= end_date)
    
    # Filter by approval status based on user role
    # Only show fully approved exams to students and professors
    if current_user.role in [UserRole.STUDENT, UserRole.PROFESSOR]:
        query = query.filter(
            and_(
                Examen.dept_head_approved == 1,
                Examen.vice_dean_approved == 1
            )
        )
    elif not include_pending and current_user.role == UserRole.DEPT_HEAD:
        # Department heads see exams waiting for their approval or already approved
        query = query.filter(Examen.dept_head_approved >= 0)
    
    return query.all()

@app.get("/api/examens/{examen_id}", response_model=ExamenSchema)
def get_examen(examen_id: int, db: Session = Depends(get_db)):
    examen = db.query(Examen).filter(Examen.id == examen_id).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen not found")
    return examen

@app.post("/api/examens", response_model=ExamenSchema)
def create_examen(examen: ExamenCreate, db: Session = Depends(get_db)):
    db_examen = Examen(
        module_id=examen.module_id,
        date=examen.date,
        heure=examen.heure,
        duree=examen.duree
    )
    db.add(db_examen)
    db.flush()
    
    # Associate rooms
    for salle_id in examen.salle_ids:
        db.execute(examens_salles.insert().values(examen_id=db_examen.id, salle_id=salle_id))
    
    # Associate professors
    for prof_id in examen.prof_ids:
        db.execute(surveillances.insert().values(examen_id=db_examen.id, prof_id=prof_id))
    
    db.commit()
    db.refresh(db_examen)
    return db_examen

@app.delete("/api/examens/{examen_id}")
def delete_examen(examen_id: int, db: Session = Depends(get_db)):
    examen = db.query(Examen).filter(Examen.id == examen_id).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen not found")
    db.delete(examen)
    db.commit()
    return {"message": "Examen deleted successfully"}

# ==================== TIMETABLE GENERATION ====================
@app.post("/api/timetable/generate", response_model=TimetableResponse)
def generate_timetable(
    request: TimetableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    generator = TimetableGenerator(db)
    result = generator.generate_timetable(
        start_date=request.start_date,
        end_date=request.end_date,
        exam_start_time=request.exam_start_time,
        exam_end_time=request.exam_end_time
    )
    
    return TimetableResponse(
        success=result["success"],
        message=f"Generated {result['generated_exams']} exams" if result["success"] else "Generation completed with conflicts",
        conflicts=result["conflicts"],
        generated_exams=result["generated_exams"]
    )

# ==================== CONFLICT DETECTION ====================
@app.get("/api/conflicts", response_model=List[ConflictInfo])
def get_conflicts(start_date: date = None, end_date: date = None, db: Session = Depends(get_db)):
    conflicts = []
    
    if not start_date or not end_date:
        # Get date range from existing exams
        dates = db.query(func.min(Examen.date), func.max(Examen.date)).first()
        if dates[0] and dates[1]:
            start_date = dates[0]
            end_date = dates[1]
        else:
            return []
    
    # Student conflicts
    student_conflicts = db.query(
        Etudiant.id, Etudiant.nom, Etudiant.prenom, Examen.date, func.count(Examen.id).label('count')
    ).join(
        inscriptions, Etudiant.id == inscriptions.c.etudiant_id
    ).join(
        Examen, inscriptions.c.module_id == Examen.module_id
    ).filter(
        and_(Examen.date >= start_date, Examen.date <= end_date)
    ).group_by(Etudiant.id, Etudiant.nom, Etudiant.prenom, Examen.date).having(
        func.count(Examen.id) > 1
    ).all()
    
    for conflict in student_conflicts:
        conflicts.append(ConflictInfo(
            type="student_conflict",
            description=f"Student {conflict[1]} {conflict[2]} has {conflict[4]} exams on {conflict[3]}",
            details={
                "etudiant_id": conflict[0],
                "nom": conflict[1],
                "prenom": conflict[2],
                "date": str(conflict[3]),
                "exam_count": conflict[4]
            }
        ))
    
    # Professor conflicts
    prof_conflicts = db.query(
        Professeur.id, Professeur.nom, Examen.date, func.count(Examen.id).label('count')
    ).join(
        surveillances, Professeur.id == surveillances.c.prof_id
    ).join(
        Examen, surveillances.c.examen_id == Examen.id
    ).filter(
        and_(Examen.date >= start_date, Examen.date <= end_date)
    ).group_by(Professeur.id, Professeur.nom, Examen.date).having(
        func.count(Examen.id) > 3
    ).all()
    
    for conflict in prof_conflicts:
        conflicts.append(ConflictInfo(
            type="professor_conflict",
            description=f"Professor {conflict[1]} has {conflict[3]} exams on {conflict[2]}",
            details={
                "prof_id": conflict[0],
                "nom": conflict[1],
                "date": str(conflict[2]),
                "exam_count": conflict[3]
            }
        ))
    
    # Room capacity conflicts
    capacity_conflicts = db.query(
        Examen.id, Module.nom, func.count(inscriptions.c.etudiant_id).label('students'),
        func.sum(func.least(Salle.capacite, 20)).label('capacity')
    ).join(
        examens_salles, Examen.id == examens_salles.c.examen_id
    ).join(
        Salle, examens_salles.c.salle_id == Salle.id
    ).join(
        Module, Examen.module_id == Module.id
    ).join(
        inscriptions, Module.id == inscriptions.c.module_id
    ).filter(
        and_(Examen.date >= start_date, Examen.date <= end_date)
    ).group_by(Examen.id, Module.nom).all()
    
    for conflict in capacity_conflicts:
        capacity = conflict[3] or 0
        if conflict[2] > capacity:
            conflicts.append(ConflictInfo(
                type="capacity_conflict",
                description=f"Exam {conflict[1]} has {conflict[2]} students but only {capacity} capacity",
                details={
                    "examen_id": conflict[0],
                    "module": conflict[1],
                    "students": conflict[2],
                    "capacity": capacity
                }
            ))
    
    return conflicts

# ==================== STATISTICS ====================
@app.get("/api/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    total_students = db.query(func.count(Etudiant.id)).scalar()
    total_professors = db.query(func.count(Professeur.id)).scalar()
    total_exams = db.query(func.count(Examen.id)).scalar()
    
    # Room utilization
    room_usage = db.query(
        Salle.nom, func.count(Examen.id).label('usage_count')
    ).join(
        examens_salles, Salle.id == examens_salles.c.salle_id
    ).join(
        Examen, examens_salles.c.examen_id == Examen.id
    ).group_by(Salle.id, Salle.nom).all()
    
    room_utilization = {room[0]: room[1] for room in room_usage}
    
    # Department statistics
    dept_stats = db.query(
        Departement.nom, func.count(Examen.id).label('exam_count'),
        func.count(func.distinct(Etudiant.id)).label('student_count')
    ).join(
        Formation, Departement.id == Formation.dept_id
    ).join(
        Module, Formation.id == Module.formation_id
    ).join(
        Examen, Module.id == Examen.module_id
    ).outerjoin(
        Etudiant, Formation.id == Etudiant.formation_id
    ).group_by(Departement.id, Departement.nom).all()
    
    department_stats = [
        {"departement": stat[0], "exam_count": stat[1], "student_count": stat[2]}
        for stat in dept_stats
    ]
    
    # Conflict count
    conflict_count = len(get_conflicts(db=db))
    
    return StatisticsResponse(
        total_students=total_students or 0,
        total_professors=total_professors or 0,
        total_exams=total_exams or 0,
        room_utilization=room_utilization,
        department_stats=department_stats,
        conflict_count=conflict_count
    )

# ==================== EXAM APPROVAL ====================
@app.post("/api/examens/{examen_id}/approve/dept-head")
def approve_exam_dept_head(
    examen_id: int,
    approval: ExamenApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DEPT_HEAD, UserRole.ADMIN]))
):
    """Department Head approves or rejects an exam"""
    examen = db.query(Examen).filter(Examen.id == examen_id).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen not found")
    
    examen.dept_head_approved = 1 if approval.approved else -1
    db.commit()
    db.refresh(examen)
    return {"message": f"Exam {'approved' if approval.approved else 'rejected'} by Department Head", "examen": examen}

@app.post("/api/examens/{examen_id}/approve/vice-dean")
def approve_exam_vice_dean(
    examen_id: int,
    approval: ExamenApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DEAN, UserRole.ADMIN]))
):
    """Vice-Dean approves or rejects an exam (only if already approved by Dept Head)"""
    examen = db.query(Examen).filter(Examen.id == examen_id).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen not found")
    
    if examen.dept_head_approved != 1:
        raise HTTPException(
            status_code=400, 
            detail="Exam must be approved by Department Head before Vice-Dean approval"
        )
    
    examen.vice_dean_approved = 1 if approval.approved else -1
    db.commit()
    db.refresh(examen)
    return {"message": f"Exam {'approved' if approval.approved else 'rejected'} by Vice-Dean", "examen": examen}

@app.get("/api/examens/pending/dept-head")
def get_pending_dept_head_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DEPT_HEAD, UserRole.ADMIN]))
):
    """Get exams pending Department Head approval"""
    exams = db.query(Examen).filter(Examen.dept_head_approved == 0).all()
    return exams

@app.get("/api/examens/pending/vice-dean")
def get_pending_vice_dean_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DEAN, UserRole.ADMIN]))
):
    """Get exams pending Vice-Dean approval (already approved by Dept Head)"""
    exams = db.query(Examen).filter(
        and_(
            Examen.dept_head_approved == 1,
            Examen.vice_dean_approved == 0
        )
    ).all()
    return exams

# ==================== STUDENT TIMETABLE ====================
@app.get("/api/etudiants/{etudiant_id}/timetable")
def get_student_timetable(etudiant_id: int, db: Session = Depends(get_db)):
    student = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all exams for modules the student is enrolled in
    # Only show fully approved exams (both dept head and vice-dean approved)
    exams = db.query(Examen).join(
        Module, Examen.module_id == Module.id
    ).join(
        inscriptions, Module.id == inscriptions.c.module_id
    ).filter(
        and_(
            inscriptions.c.etudiant_id == etudiant_id,
            Examen.dept_head_approved == 1,
            Examen.vice_dean_approved == 1
        )
    ).order_by(Examen.date, Examen.heure).all()
    
    # Get rooms and professors for each exam
    timetable = []
    for exam in exams:
        rooms = db.query(Salle).join(
            examens_salles, Salle.id == examens_salles.c.salle_id
        ).filter(examens_salles.c.examen_id == exam.id).all()
        
        professors = db.query(Professeur).join(
            surveillances, Professeur.id == surveillances.c.prof_id
        ).filter(surveillances.c.examen_id == exam.id).all()
        
        timetable.append({
            "examen_id": exam.id,
            "module": exam.module.nom,
            "date": str(exam.date),
            "heure": str(exam.heure),
            "duree": exam.duree,
            "salles": [{"id": s.id, "nom": s.nom, "batiment": s.batiment.nom} for s in rooms],
            "professeurs": [{"id": p.id, "nom": p.nom} for p in professors]
        })
    
    return {"etudiant": {"id": student.id, "nom": student.nom, "prenom": student.prenom}, "timetable": timetable}

# ==================== PROFESSOR TIMETABLE ====================
@app.get("/api/professeurs/{prof_id}/timetable")
def get_professor_timetable(prof_id: int, db: Session = Depends(get_db)):
    professor = db.query(Professeur).filter(Professeur.id == prof_id).first()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    # Only show fully approved exams (both dept head and vice-dean approved)
    exams = db.query(Examen).join(
        surveillances, Examen.id == surveillances.c.examen_id
    ).filter(
        and_(
            surveillances.c.prof_id == prof_id,
            Examen.dept_head_approved == 1,
            Examen.vice_dean_approved == 1
        )
    ).order_by(Examen.date, Examen.heure).all()
    
    timetable = []
    for exam in exams:
        rooms = db.query(Salle).join(
            examens_salles, Salle.id == examens_salles.c.salle_id
        ).filter(examens_salles.c.examen_id == exam.id).all()
        
        timetable.append({
            "examen_id": exam.id,
            "module": exam.module.nom,
            "date": str(exam.date),
            "heure": str(exam.heure),
            "duree": exam.duree,
            "salles": [{"id": s.id, "nom": s.nom, "batiment": s.batiment.nom} for s in rooms]
        })
    
    return {"professeur": {"id": professor.id, "nom": professor.nom}, "timetable": timetable}

@app.get("/")
def root():
    return {"message": "Exam Timetable Optimization Platform API"}
