import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import Login from './components/Login';
import AdminDashboard from './components/AdminDashboard';
import DeanDashboard from './components/DeanDashboard';
import DeptHeadDashboard from './components/DeptHeadDashboard';
import StudentView from './components/StudentView';
import ProfessorView from './components/ProfessorView';
import ProtectedRoute from './components/ProtectedRoute';
import { logout, getUserRole, isAuthenticated, setAuthToken, getAuthToken } from './services/auth';

function Navbar() {
  const navigate = useNavigate();
  const userRole = getUserRole();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="container">
        <h1 className="navbar-brand">Exam Timetable Platform</h1>
        <div className="navbar-links">
          <span className="user-role">Role: {userRole}</span>
          <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
      </div>
    </nav>
  );
}

function AppLayout() {
  const location = useLocation();
  const userRole = getUserRole();

  // Redirect to appropriate dashboard based on role
  useEffect(() => {
    if (location.pathname === '/') {
      // This will be handled by the Routes below
    }
  }, [location]);

  return (
    <>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/admin" element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dean" element={
            <ProtectedRoute allowedRoles={['dean']}>
              <DeanDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dept-head" element={
            <ProtectedRoute allowedRoles={['dept_head']}>
              <DeptHeadDashboard />
            </ProtectedRoute>
          } />
          <Route path="/student" element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentView />
            </ProtectedRoute>
          } />
          <Route path="/professor" element={
            <ProtectedRoute allowedRoles={['professor']}>
              <ProfessorView />
            </ProtectedRoute>
          } />
          <Route path="/" element={
            <Navigate to={userRole === 'admin' ? '/admin' : 
                        userRole === 'dean' ? '/dean' : 
                        userRole === 'dept_head' ? '/dept-head' : 
                        userRole === 'professor' ? '/professor' : 
                        userRole === 'student' ? '/student' : '/login'} replace />
          } />
        </Routes>
      </div>
    </>
  );
}

function App() {
  // Initialize auth token on app load
  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      setAuthToken(token);
    }
  }, []);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
