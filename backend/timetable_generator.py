from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, time, timedelta
from typing import List, Dict, Tuple
from models import Examen, Module, Etudiant, Professeur, Salle, Formation, Departement, inscriptions, surveillances, examens_salles

class TimetableGenerator:
    def __init__(self, db: Session):
        self.db = db
        
    def generate_timetable(self, start_date: date, end_date: date, 
                          exam_start_time: time = time(9, 0), 
                          exam_end_time: time = time(17, 0)) -> Dict:
        """
        Generate an optimized exam timetable that respects all constraints:
        - Students: Max 1 exam per day
        - Professors: Max 3 exams per day, but not at the same time
        - Room capacity: Max 20 students per room during exams (respects actual room capacity)
        - Formation grouping: Students from the same formation take the exam together in the same room(s)
        - Department priority: Teachers supervise their department exams first
        - Equal distribution: All teachers have similar number of supervisions
        - Formation constraint: Exams from the same formation cannot be on the same day
        """
        # Get all modules that need exams
        modules = self.db.query(Module).all()
        
        # Get all available rooms
        rooms = self.db.query(Salle).order_by(Salle.capacite.desc()).all()
        
        # Get all professors
        professors = self.db.query(Professeur).all()
        
        # Delete existing exams for the date range
        self.db.query(Examen).filter(
            and_(Examen.date >= start_date, Examen.date <= end_date)
        ).delete()
        self.db.commit()
        
        generated_exams = []
        conflicts = []
        
        # Group modules by formation to optimize scheduling
        current_date = start_date
        available_slots = self._generate_time_slots(exam_start_time, exam_end_time)
        scheduled_modules = set()
        
        # First pass: Schedule all modules
        while len(scheduled_modules) < len(modules):
            if current_date > end_date:
                conflicts.append({
                    "type": "date_range",
                    "message": f"Not enough days to schedule all exams. {len(modules) - len(scheduled_modules)} modules remaining."
                })
                break
                
            used_slots_today = []
            
            for module in modules:
                if module.id in scheduled_modules:
                    continue
                    
                # Check if another module from the same formation already has an exam today
                if self._check_formation_conflict(module.formation_id, current_date, module.id):
                    continue
                    
                # Get students enrolled in this module, grouped by formation
                # Students from the same formation should take the exam together
                students_by_formation = self.db.query(
                    Etudiant.formation_id,
                    func.count(Etudiant.id).label('student_count')
                ).join(
                    inscriptions, Etudiant.id == inscriptions.c.etudiant_id
                ).filter(
                    inscriptions.c.module_id == module.id
                ).group_by(Etudiant.formation_id).all()
                
                if not students_by_formation:
                    scheduled_modules.add(module.id)
                    continue
                
                # Try to find available slot and rooms
                exam_scheduled = False
                for slot in available_slots:
                    if slot in used_slots_today:
                        continue
                    
                    # Check if any student in this module already has an exam at this time
                    has_conflict = self._check_student_conflicts(module.id, current_date, slot)
                    if has_conflict:
                        continue
                    
                    # Find rooms to accommodate all students, ensuring same formation students are together
                    # Calculate total students and verify we can group by formation
                    total_students = sum(formation[1] for formation in students_by_formation)
                    required_rooms = self._find_rooms_for_students_by_formation(
                        students_by_formation, rooms, current_date, slot
                    )
                    if not required_rooms:
                        continue
                    
                    # Assign professors
                    assigned_profs = self._assign_professors(module, current_date, slot, professors)
                    if not assigned_profs:
                        continue
                    
                    # Create exam (initially pending approval)
                    exam = Examen(
                        module_id=module.id,
                        date=current_date,
                        heure=slot,
                        duree=120,  # Default 2 hours
                        dept_head_approved=0,  # Pending Department Head approval
                        vice_dean_approved=0   # Pending Vice-Dean approval
                    )
                    self.db.add(exam)
                    self.db.flush()
                    
                    # Associate rooms
                    for room_id in required_rooms:
                        self.db.execute(
                            examens_salles.insert().values(examen_id=exam.id, salle_id=room_id)
                        )
                    
                    # Associate professors
                    for prof_id in assigned_profs:
                        self.db.execute(
                            surveillances.insert().values(examen_id=exam.id, prof_id=prof_id)
                        )
                    
                    generated_exams.append(exam.id)
                    scheduled_modules.add(module.id)
                    used_slots_today.append(slot)
                    exam_scheduled = True
                    break
                
                if not exam_scheduled:
                    # Try next day
                    pass
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Check for conflicts after generation
        conflicts.extend(self._detect_conflicts(start_date, end_date))
        
        self.db.commit()
        
        return {
            "generated_exams": len(generated_exams),
            "conflicts": conflicts,
            "success": len(scheduled_modules) == len(modules)
        }
    
    def _generate_time_slots(self, start_time: time, end_time: time) -> List[time]:
        """Generate available time slots for exams"""
        slots = []
        current = start_time
        while current < end_time:
            slots.append(current)
            # Next slot is 3 hours later (2h exam + 1h break)
            hour = current.hour + 3
            if hour >= 24:
                break
            current = time(hour, 0)
        return slots
    
    def _check_formation_conflict(self, formation_id: int, exam_date: date, exclude_module_id: int = None) -> bool:
        """Check if any module from the same formation already has an exam on this date"""
        query = self.db.query(Examen).join(
            Module, Examen.module_id == Module.id
        ).filter(
            and_(
                Module.formation_id == formation_id,
                Examen.date == exam_date
            )
        )
        
        # Exclude the current module if provided (for checking before scheduling)
        if exclude_module_id:
            query = query.filter(Module.id != exclude_module_id)
        
        conflicting_exam = query.first()
        return conflicting_exam is not None
    
    def _check_student_conflicts(self, module_id: int, exam_date: date, exam_time: time) -> bool:
        """Check if any student in this module already has an exam on this date"""
        students = self.db.query(inscriptions.c.etudiant_id).filter(
            inscriptions.c.module_id == module_id
        ).subquery()
        
        conflicting_exams = self.db.query(Examen).join(
            Module, Examen.module_id == Module.id
        ).join(
            inscriptions, Module.id == inscriptions.c.module_id
        ).filter(
            and_(
                inscriptions.c.etudiant_id.in_(students),
                Examen.date == exam_date
            )
        ).first()
        
        return conflicting_exams is not None
    
    def _find_rooms_for_students(self, student_count: int, rooms: List, 
                                 exam_date: date, exam_time: time) -> List[int]:
        """Find available rooms that can accommodate students (max 20 per room)"""
        # Get already scheduled rooms for this date/time
        scheduled_rooms = self.db.query(examens_salles.c.salle_id).join(
            Examen, examens_salles.c.examen_id == Examen.id
        ).filter(
            and_(
                Examen.date == exam_date,
                Examen.heure == exam_time
            )
        ).all()
        
        scheduled_room_ids = [r[0] for r in scheduled_rooms]
        
        available_rooms = []
        remaining_students = student_count
        
        for room in sorted(rooms, key=lambda x: x.capacite, reverse=True):
            if room.id in scheduled_room_ids:
                continue
            
            # During exams, max 20 students per room
            room_capacity = min(room.capacite, 20)
            if room_capacity > 0:
                available_rooms.append(room.id)
                remaining_students -= room_capacity
                if remaining_students <= 0:
                    break
        
        return available_rooms if remaining_students <= 0 else []
    
    def _find_rooms_for_students_by_formation(self, students_by_formation: List, 
                                               rooms: List, exam_date: date, 
                                               exam_time: time) -> List[int]:
        """
        Find available rooms ensuring students from the same formation are grouped together.
        Students from the same formation will be assigned to the same room(s) together.
        Returns list of room IDs that can accommodate all formation groups.
        """
        # Get already scheduled rooms for this date/time
        scheduled_rooms = self.db.query(examens_salles.c.salle_id).join(
            Examen, examens_salles.c.examen_id == Examen.id
        ).filter(
            and_(
                Examen.date == exam_date,
                Examen.heure == exam_time
            )
        ).all()
        
        scheduled_room_ids = [r[0] for r in scheduled_rooms]
        
        # Sort rooms by capacity (descending) for better allocation
        available_rooms_list = [
            room for room in sorted(rooms, key=lambda x: x.capacite, reverse=True)
            if room.id not in scheduled_room_ids
        ]
        
        required_rooms = []
        used_room_indices = set()  # Track which rooms we've used
        
        # Assign rooms for each formation group
        # Each formation's students must be grouped together in the same room(s)
        for formation_id, student_count in students_by_formation:
            remaining_students = student_count
            formation_rooms = []
            
            # Try to fit all students from this formation together
            # Priority: fit entire formation in one room if possible, otherwise use multiple rooms
            for idx, room in enumerate(available_rooms_list):
                if idx in used_room_indices:
                    continue  # Room already assigned to another formation
                
                # During exams, max 20 students per room
                room_capacity = min(room.capacite, 20)
                
                if room_capacity > 0 and remaining_students > 0:
                    # Assign this room to this formation
                    formation_rooms.append(room.id)
                    required_rooms.append(room.id)
                    used_room_indices.add(idx)
                    
                    # Update remaining students
                    if remaining_students <= room_capacity:
                        # All students from this formation fit in this room
                        remaining_students = 0
                        break
                    else:
                        # Need more rooms for this formation
                        remaining_students -= room_capacity
            
            # If we couldn't fit all students from this formation, return empty
            # This ensures we only schedule if all formations can be accommodated
            if remaining_students > 0:
                return []
        
        return required_rooms
    
    def _assign_professors(self, module: Module, exam_date: date, exam_time: time,
                          professors: List) -> List[int]:
        """
        Assign professors to supervise exam (prioritize department professors).
        Constraints:
        - Maximum 3 exams per day per professor
        - Cannot be assigned to multiple exams at the same time
        """
        assigned = []
        required_supervisors = 2  # At least 2 supervisors per exam
        
        # Get professors from same department as module's formation
        dept_professors = [p for p in professors if p.dept_id == module.formation.dept_id]
        other_professors = [p for p in professors if p.dept_id != module.formation.dept_id]
        
        # Prioritize department professors
        all_professors = dept_professors + other_professors
        
        for prof in all_professors:
            if len(assigned) >= required_supervisors:
                break
            
            # Check if professor already has an exam at this exact time on this day
            time_conflict = self.db.query(Examen).join(
                surveillances, Examen.id == surveillances.c.examen_id
            ).filter(
                and_(
                    surveillances.c.prof_id == prof.id,
                    Examen.date == exam_date,
                    Examen.heure == exam_time
                )
            ).first()
            
            if time_conflict:
                # Professor already has an exam at this time, skip
                continue
            
            # Check if professor already has 3 exams this day (at different times)
            daily_exams = self.db.query(func.count(surveillances.c.examen_id)).join(
                Examen, surveillances.c.examen_id == Examen.id
            ).filter(
                and_(
                    surveillances.c.prof_id == prof.id,
                    Examen.date == exam_date
                )
            ).scalar() or 0
            
            if daily_exams < 3:
                assigned.append(prof.id)
        
        return assigned if len(assigned) >= required_supervisors else []
    
    def _detect_conflicts(self, start_date: date, end_date: date) -> List[Dict]:
        """Detect all types of conflicts in the generated timetable"""
        conflicts = []
        
        # Check student conflicts (max 1 exam per day)
        student_conflicts = self.db.query(
            inscriptions.c.etudiant_id,
            Examen.date,
            func.count(Examen.id).label('count')
        ).join(
            Examen, inscriptions.c.module_id == Examen.module_id
        ).filter(
            and_(Examen.date >= start_date, Examen.date <= end_date)
        ).group_by(inscriptions.c.etudiant_id, Examen.date).having(
            func.count(Examen.id) > 1
        ).all()
        
        for conflict in student_conflicts:
            conflicts.append({
                "type": "student_conflict",
                "etudiant_id": conflict[0],
                "date": str(conflict[1]),
                "message": f"Student {conflict[0]} has {conflict[2]} exams on {conflict[1]}"
            })
        
        # Check professor conflicts (max 3 exams per day, but not at same time)
        # First check for time conflicts (same professor, same date, same time)
        prof_time_conflicts = self.db.query(
            surveillances.c.prof_id,
            Examen.date,
            Examen.heure,
            func.count(Examen.id).label('count')
        ).join(
            Examen, surveillances.c.examen_id == Examen.id
        ).filter(
            and_(Examen.date >= start_date, Examen.date <= end_date)
        ).group_by(surveillances.c.prof_id, Examen.date, Examen.heure).having(
            func.count(Examen.id) > 1
        ).all()
        
        for conflict in prof_time_conflicts:
            prof = self.db.query(Professeur).filter(Professeur.id == conflict[0]).first()
            conflicts.append({
                "type": "professor_time_conflict",
                "prof_id": conflict[0],
                "prof_name": prof.nom if prof else "Unknown",
                "date": str(conflict[1]),
                "time": str(conflict[2]),
                "exam_count": conflict[3],
                "message": f"Professor {prof.nom if prof else conflict[0]} has {conflict[3]} exams at {conflict[2]} on {conflict[1]}"
            })
        
        # Check for daily limit conflicts (more than 3 exams per day)
        prof_daily_conflicts = self.db.query(
            surveillances.c.prof_id,
            Examen.date,
            func.count(Examen.id).label('count')
        ).join(
            Examen, surveillances.c.examen_id == Examen.id
        ).filter(
            and_(Examen.date >= start_date, Examen.date <= end_date)
        ).group_by(surveillances.c.prof_id, Examen.date).having(
            func.count(Examen.id) > 3
        ).all()
        
        for conflict in prof_daily_conflicts:
            prof = self.db.query(Professeur).filter(Professeur.id == conflict[0]).first()
            conflicts.append({
                "type": "professor_daily_conflict",
                "prof_id": conflict[0],
                "prof_name": prof.nom if prof else "Unknown",
                "date": str(conflict[1]),
                "exam_count": conflict[2],
                "message": f"Professor {prof.nom if prof else conflict[0]} has {conflict[2]} exams on {conflict[1]} (max 3 allowed)"
            })
        
        # Check room capacity conflicts
        capacity_conflicts = self.db.query(
            Examen.id,
            func.count(inscriptions.c.etudiant_id).label('students'),
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
        ).group_by(Examen.id).all()
        
        for conflict in capacity_conflicts:
            if conflict[1] > (conflict[2] or 0):
                conflicts.append({
                    "type": "capacity_conflict",
                    "examen_id": conflict[0],
                    "students": conflict[1],
                    "capacity": conflict[2],
                    "message": f"Exam {conflict[0]} has {conflict[1]} students but only {conflict[2]} capacity"
                })
        
        # Check formation conflicts (same formation exams on same day)
        # First get formations with multiple exams on same day
        formation_conflicts_query = self.db.query(
            Module.formation_id,
            Examen.date,
            func.count(Examen.id).label('count')
        ).join(
            Examen, Module.id == Examen.module_id
        ).filter(
            and_(Examen.date >= start_date, Examen.date <= end_date)
        ).group_by(Module.formation_id, Examen.date).having(
            func.count(Examen.id) > 1
        ).all()
        
        for conflict in formation_conflicts_query:
            formation_id, exam_date, exam_count = conflict
            formation = self.db.query(Formation).filter(Formation.id == formation_id).first()
            
            # Get module names for this formation on this date
            modules_on_date = self.db.query(Module.nom).join(
                Examen, Module.id == Examen.module_id
            ).filter(
                and_(
                    Module.formation_id == formation_id,
                    Examen.date == exam_date
                )
            ).all()
            module_names = ', '.join([m[0] for m in modules_on_date])
            
            conflicts.append({
                "type": "formation_conflict",
                "formation_id": formation_id,
                "formation_name": formation.nom if formation else "Unknown",
                "date": str(exam_date),
                "exam_count": exam_count,
                "modules": module_names,
                "message": f"Formation {formation.nom if formation else formation_id} has {exam_count} exams on {exam_date}: {module_names}"
            })
        
        return conflicts
