# Step-by-Step Setup Guide

## Prerequisites

Before starting, make sure you have:
- **Python 3.8+** installed (`python --version`)
- **Node.js 14+** installed (`node --version`)
- **PostgreSQL** installed and running
- **npm** or **yarn** installed

## Step 1: Database Setup

### 1.1 Create PostgreSQL Database

Open a terminal/command prompt and run:

```bash
# Create the database
createdb exam_db

# Or using psql:
psql -U postgres
CREATE DATABASE exam_db;
\q
```

### 1.2 Run the SQL Script

```bash
# From the project root directory
psql -U postgres -d exam_db -f script.sql
```

Or if you're using a different PostgreSQL user:
```bash
psql -U your_username -d exam_db -f script.sql
```

This will create all tables, indexes, and insert sample data.

**Important**: After running the SQL script, you need to seed the users:
```bash
cd backend
python seed_users.py
```

This will create example user accounts with the password `password123`.

## Step 2: Backend Setup

### 2.1 Navigate to Backend Directory

```bash
cd backend
```

### 2.2 Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 2.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Configure Database Connection

Create a `.env` file in the `backend` directory:

```bash
# Windows
type nul > .env

# Linux/Mac
touch .env
```

Edit `.env` and add:
```
DATABASE_URL=postgresql://username:password@localhost:5432/exam_db
SECRET_KEY=your-secret-key-here-change-this
```

**Replace:**
- `username` with your PostgreSQL username (often `postgres`)
- `password` with your PostgreSQL password
- `your-secret-key-here-change-this` with any random string

**Example:**
```
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/exam_db
SECRET_KEY=super-secret-key-12345
```

### 2.5 Seed Example Users

After setting up the database, create example user accounts:

```bash
python seed_users.py
```

This creates the following accounts (all with password `password123`):
- `admin` - Administrator
- `dean` - Dean
- `depthead` - Department Head
- `prof1`, `prof2`, `prof3` - Professors
- `student1`, `student2`, `student3` - Students

### 2.6 Run the Backend Server

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is running!** Keep this terminal window open.

You can test it by visiting: http://localhost:8000/docs (FastAPI automatic documentation)

## Step 3: Frontend Setup

### 3.1 Open a New Terminal Window

Keep the backend running, and open a new terminal/command prompt.

### 3.2 Navigate to Frontend Directory

```bash
cd frontend
```

### 3.3 Install Node Dependencies

```bash
npm install
```

This may take a few minutes. Wait for it to complete.

### 3.4 Run the Frontend

```bash
npm start
```

This will:
- Start the React development server
- Automatically open your browser to `http://localhost:3000`
- If it doesn't open automatically, navigate to that URL

✅ **Frontend is running!**

## Step 4: Using the Application

### Access the Application

1. Open your browser to: **http://localhost:3000**
2. You'll be redirected to the login page
3. Login with one of the example accounts:
   - **Admin**: `admin` / `password123`
   - **Dean**: `dean` / `password123`
   - **Department Head**: `depthead` / `password123`
   - **Professor**: `prof1` / `password123`
   - **Student**: `student1` / `password123`
4. After login, you'll be redirected to your role-specific dashboard

### Test the Timetable Generator

1. Click **"Admin"** in the navigation
2. Enter a start date and end date (e.g., 2026-01-15 to 2026-01-20)
3. Click **"Generate Timetable"**
4. Wait for the generation to complete (should be fast with sample data)
5. View the generated exams and any conflicts

### View Different Dashboards

- **Dean**: See global statistics and KPIs
- **Dept Head**: View department-specific data
- **Student**: View student timetables (select from dropdown)
- **Professor**: View professor supervision assignments

## Troubleshooting

### Database Connection Error

If you get: `could not connect to server`

1. Check PostgreSQL is running:
   ```bash
   # Windows
   services.msc (look for PostgreSQL service)
   
   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. Check your `.env` file has correct credentials

3. Test connection manually:
   ```bash
   psql -U postgres -d exam_db
   ```

### Port Already in Use

If port 8000 is busy:
```bash
uvicorn main:app --reload --port 8001
```
Then update `frontend/src/services/api.js` to use port 8001.

If port 3000 is busy:
- React will ask if you want to use a different port (type 'y')
- Or kill the process using port 3000

### Module Not Found (Frontend)

If you see import errors:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Module Not Found (Backend)

If you see Python import errors:
```bash
cd backend
# Make sure venv is activated (you should see (venv))
pip install -r requirements.txt
```

### CORS Errors

The backend is configured to accept requests from `localhost:3000` and `localhost:5173`. If you're using a different port, update `backend/main.py`:

```python
allow_origins=["http://localhost:3000", "http://localhost:YOUR_PORT"]
```

## Quick Command Reference

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

**To Stop:**
- Press `Ctrl+C` in each terminal window

## Next Steps

1. **Add more data**: Use the SQL script or API to add more students, professors, modules
2. **Test constraints**: Try generating timetables with conflicting schedules
3. **View statistics**: Check the Dean dashboard for KPIs and charts
4. **Customize**: Modify the generation algorithm in `backend/timetable_generator.py`

## Need Help?

- Backend API docs: http://localhost:8000/docs
- Check console logs in browser (F12)
- Check terminal output for errors
