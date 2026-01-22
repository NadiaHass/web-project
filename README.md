# Exam Timetable Optimization Platform

A full-stack application for optimizing university exam timetables with automatic generation, conflict detection, and resource optimization.

## Features

### Core Functionality
- **Automatic Timetable Generation**: Generates optimized exam schedules respecting all constraints
- **Conflict Detection**: Identifies student, professor, and capacity conflicts
- **Resource Optimization**: Efficient allocation of rooms and professors
- **Multi-actor Dashboard**: Different views for Dean, Administrator, Department Head, Students, and Professors

### Constraints Enforced
- Students: Maximum 1 exam per day
- Professors: Maximum 3 exams per day
- Rooms: Respect real capacity (max 20 students per room during exams)
- Department Priority: Teachers supervise their department exams first
- Equal Distribution: All teachers have similar number of supervisions

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React.js
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy

## Project Structure

```
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database connection
│   ├── timetable_generator.py  # Timetable optimization algorithm
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── AdminDashboard.js
│   │   │   ├── DeanDashboard.js
│   │   │   ├── DeptHeadDashboard.js
│   │   │   ├── StudentView.js
│   │   │   └── ProfessorView.js
│   │   ├── services/
│   │   │   └── api.js          # API service layer
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── script.sql                  # Database schema
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up database:
```bash
# Create PostgreSQL database
createdb exam_db

# Run the SQL script
psql -d exam_db -f ../script.sql

# Seed example users (run from backend directory)
python seed_users.py
```

5. Create `.env` file:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/exam_db
SECRET_KEY=your-secret-key-here
```

6. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Authentication

The application uses JWT-based authentication. All users share the same default password: `password123`

### Example Accounts
- **Admin**: `admin` / `password123`
- **Dean**: `dean` / `password123`
- **Department Head**: `depthead` / `password123`
- **Professor**: `prof1` / `password123`
- **Student**: `student1` / `password123`

### Authentication Endpoints
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/register` - Register new user (optional)
- `GET /api/auth/me` - Get current user info

## API Endpoints

### Timetable Generation
- `POST /api/timetable/generate` - Generate optimized timetable (Admin only)

### Exams
- `GET /api/examens` - List all exams
- `POST /api/examens` - Create exam
- `DELETE /api/examens/{id}` - Delete exam

### Conflicts
- `GET /api/conflicts` - Detect all conflicts

### Statistics
- `GET /api/statistics` - Get global statistics

### Student/Professor Views
- `GET /api/etudiants/{id}/timetable` - Get student timetable
- `GET /api/professeurs/{id}/timetable` - Get professor assignments

See `backend/main.py` for complete API documentation.

## User Roles & Features

### Administrator (Exam Planning Service)
- Generate automatic timetables
- Detect and resolve conflicts
- Resource optimization

### Dean & Vice-Dean
- Global strategic view
- Overall room occupancy
- Conflict rates per department
- Academic KPIs

### Department Head
- Department validation
- Statistics per department
- Conflicts per training program

### Students
- Personalized timetable consultation
- Filter by department/training program
- View exam locations and times

### Professors
- View supervision assignments
- Check daily load (max 3 exams/day)
- See assigned rooms

## Timetable Generation Algorithm

The generator uses a constraint-based approach:

1. **Module Scheduling**: Groups modules by formation to optimize scheduling
2. **Slot Assignment**: Finds available time slots (2h exam + 1h break)
3. **Room Allocation**: Assigns rooms based on student count and capacity (max 20/room)
4. **Professor Assignment**: Prioritizes department professors, ensures max 3/day
5. **Conflict Checking**: Validates all constraints after generation

## Performance

The system is designed to generate optimal schedules in **less than 45 seconds** for datasets with ~130,000 registrations.

## License

This project is for educational purposes.
