import axios from 'axios';
import { getAuthToken } from './auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('userRole');
      localStorage.removeItem('userId');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Departments
export const getDepartements = () => api.get('/api/departements');
export const createDepartement = (data) => api.post('/api/departements', data);

// Formations
export const getFormations = (deptId) => 
  api.get('/api/formations', { params: deptId ? { dept_id: deptId } : {} });
export const createFormation = (data) => api.post('/api/formations', data);

// Modules
export const getModules = (formationId) => 
  api.get('/api/modules', { params: formationId ? { formation_id: formationId } : {} });
export const createModule = (data) => api.post('/api/modules', data);

// Students
export const getEtudiants = (formationId) => 
  api.get('/api/etudiants', { params: formationId ? { formation_id: formationId } : {} });
export const createEtudiant = (data) => api.post('/api/etudiants', data);
export const getStudentTimetable = (studentId) => api.get(`/api/etudiants/${studentId}/timetable`);

// Professors
export const getProfesseurs = (deptId) => 
  api.get('/api/professeurs', { params: deptId ? { dept_id: deptId } : {} });
export const createProfesseur = (data) => api.post('/api/professeurs', data);
export const getProfessorTimetable = (profId) => api.get(`/api/professeurs/${profId}/timetable`);

// Buildings
export const getBatiments = () => api.get('/api/batiments');
export const createBatiment = (data) => api.post('/api/batiments', data);

// Rooms
export const getSalles = (batimentId) => 
  api.get('/api/salles', { params: batimentId ? { batiment_id: batimentId } : {} });
export const createSalle = (data) => api.post('/api/salles', data);

// Exams
export const getExamens = (params = {}) => api.get('/api/examens', { params });
export const createExamen = (data) => api.post('/api/examens', data);
export const deleteExamen = (id) => api.delete(`/api/examens/${id}`);

// Exam Approvals
export const getPendingDeptHeadApprovals = () => api.get('/api/examens/pending/dept-head');
export const getPendingViceDeanApprovals = () => api.get('/api/examens/pending/vice-dean');
export const approveExamDeptHead = (examenId, approved) => 
  api.post(`/api/examens/${examenId}/approve/dept-head`, { approved });
export const approveExamViceDean = (examenId, approved) => 
  api.post(`/api/examens/${examenId}/approve/vice-dean`, { approved });

// Timetable Generation
export const generateTimetable = (data) => api.post('/api/timetable/generate', data);

// Conflicts
export const getConflicts = (startDate, endDate) => 
  api.get('/api/conflicts', { 
    params: { 
      start_date: startDate, 
      end_date: endDate 
    } 
  });

// Statistics
export const getStatistics = () => api.get('/api/statistics');

// Authentication
export const loginUser = (username, password) => 
  api.post('/api/auth/login', { username, password });

export const getCurrentUser = () => api.get('/api/auth/me');

export default api;
