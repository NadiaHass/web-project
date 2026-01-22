import React, { useState, useEffect } from 'react';
import { generateTimetable, getConflicts, getExamens, getModules, getSalles, getProfesseurs, getStatistics } from '../services/api';
import './Dashboard.css';

const AdminDashboard = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [conflicts, setConflicts] = useState([]);
  const [examens, setExamens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [statistics, setStatistics] = useState(null);

  useEffect(() => {
    loadExamens();
    loadConflicts();
    loadStatistics();
  }, []);

  const loadExamens = async () => {
    try {
      const response = await getExamens();
      setExamens(response.data);
    } catch (error) {
      console.error('Error loading exams:', error);
    }
  };

  const loadConflicts = async () => {
    try {
      const response = await getConflicts();
      setConflicts(response.data);
    } catch (error) {
      console.error('Error loading conflicts:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  const handleGenerateTimetable = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await generateTimetable({
        start_date: startDate,
        end_date: endDate,
        exam_start_time: '09:00',
        exam_end_time: '17:00'
      });

      if (response.data.success) {
        setMessage(`Success! Generated ${response.data.generated_exams} exams.`);
      } else {
        setMessage(`Generation completed with ${response.data.conflicts.length} conflicts.`);
      }

      // Reload exams and conflicts
      await loadExamens();
      await loadConflicts();
      await loadStatistics();

      // Show conflicts if any
      if (response.data.conflicts && response.data.conflicts.length > 0) {
        setConflicts(response.data.conflicts);
      }
    } catch (error) {
      setMessage('Error generating timetable: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const conflictGroups = {
    student_conflict: conflicts.filter(c => c.type === 'student_conflict'),
    professor_conflict: conflicts.filter(c => c.type === 'professor_conflict'),
    capacity_conflict: conflicts.filter(c => c.type === 'capacity_conflict')
  };

  return (
    <div className="dashboard">
      <h2>Administrator Dashboard - Exam Planning Service</h2>

      <div className="card">
        <h3>Generate Exam Timetable</h3>
        <form onSubmit={handleGenerateTimetable}>
          <div className="form-group">
            <label>Start Date:</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>End Date:</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Timetable'}
          </button>
        </form>
        {message && (
          <div className={message.includes('Success') ? 'success' : 'error'}>
            {message}
          </div>
        )}
      </div>

      <div className="card">
        <h3>Conflict Detection ({conflicts.length} conflicts found)</h3>
        {conflicts.length === 0 ? (
          <p>No conflicts detected.</p>
        ) : (
          <div>
            {conflictGroups.student_conflict.length > 0 && (
              <div>
                <h4>Student Conflicts ({conflictGroups.student_conflict.length})</h4>
                {conflictGroups.student_conflict.map((conflict, idx) => (
                  <div key={idx} className="conflict">
                    <strong>{conflict.description}</strong>
                    <pre>{JSON.stringify(conflict.details, null, 2)}</pre>
                  </div>
                ))}
              </div>
            )}
            {conflictGroups.professor_conflict.length > 0 && (
              <div>
                <h4>Professor Conflicts ({conflictGroups.professor_conflict.length})</h4>
                {conflictGroups.professor_conflict.map((conflict, idx) => (
                  <div key={idx} className="conflict">
                    <strong>{conflict.description}</strong>
                    <pre>{JSON.stringify(conflict.details, null, 2)}</pre>
                  </div>
                ))}
              </div>
            )}
            {conflictGroups.capacity_conflict.length > 0 && (
              <div>
                <h4>Capacity Conflicts ({conflictGroups.capacity_conflict.length})</h4>
                {conflictGroups.capacity_conflict.map((conflict, idx) => (
                  <div key={idx} className="conflict">
                    <strong>{conflict.description}</strong>
                    <pre>{JSON.stringify(conflict.details, null, 2)}</pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="card">
        <h3>Generated Exams ({examens.length})</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Module</th>
              <th>Date</th>
              <th>Time</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            {examens.map((examen) => (
              <tr key={examen.id}>
                <td>{examen.id}</td>
                <td>{examen.module_id}</td>
                <td>{examen.date}</td>
                <td>{examen.heure}</td>
                <td>{examen.duree} min</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {statistics && (
        <div className="card">
          <h3>Resource Statistics</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <strong>Total Students:</strong> {statistics.total_students}
            </div>
            <div className="stat-item">
              <strong>Total Professors:</strong> {statistics.total_professors}
            </div>
            <div className="stat-item">
              <strong>Total Exams:</strong> {statistics.total_exams}
            </div>
            <div className="stat-item">
              <strong>Conflicts:</strong> {statistics.conflict_count}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
