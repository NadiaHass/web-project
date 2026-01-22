import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/auth';
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);
    
    if (result.success) {
      // Redirect based on role
      const role = result.role;
      switch (role) {
        case 'admin':
          navigate('/admin');
          break;
        case 'dean':
          navigate('/dean');
          break;
        case 'dept_head':
          navigate('/dept-head');
          break;
        case 'professor':
          navigate('/professor');
          break;
        case 'student':
          navigate('/student');
          break;
        default:
          navigate('/');
      }
    } else {
      setError(result.error || 'Login failed. Please check your credentials.');
    }
    setLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Exam Timetable Platform</h1>
        <h2>Login</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        <div className="login-info">
          <p><strong>Example accounts:</strong></p>
          <ul>
            <li>admin / password123 (Admin)</li>
            <li>dean / password123 (Dean)</li>
            <li>depthead / password123 (Department Head)</li>
            <li>prof1 / password123 (Professor)</li>
            <li>student1 / password123 (Student)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Login;
