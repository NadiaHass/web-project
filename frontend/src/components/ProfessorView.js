import React, { useState, useEffect } from 'react';
import { getProfesseurs, getProfessorTimetable } from '../services/api';
import './Dashboard.css';

const ProfessorView = () => {
  const [professors, setProfessors] = useState([]);
  const [selectedProfessor, setSelectedProfessor] = useState(null);
  const [timetable, setTimetable] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProfessors();
  }, []);

  useEffect(() => {
    if (selectedProfessor) {
      loadProfessorTimetable(selectedProfessor);
    }
  }, [selectedProfessor]);

  const loadProfessors = async () => {
    try {
      const response = await getProfesseurs();
      setProfessors(response.data);
      if (response.data.length > 0) {
        setSelectedProfessor(response.data[0].id);
      }
    } catch (error) {
      console.error('Error loading professors:', error);
    }
  };

  const loadProfessorTimetable = async (profId) => {
    setLoading(true);
    try {
      const response = await getProfessorTimetable(profId);
      setTimetable(response.data);
    } catch (error) {
      console.error('Error loading timetable:', error);
      setTimetable(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <h2>Professor Supervision Assignment</h2>

      <div className="card">
        <div className="form-group">
          <label>Select Professor:</label>
          <select
            value={selectedProfessor || ''}
            onChange={(e) => setSelectedProfessor(parseInt(e.target.value))}
          >
            {professors.map((prof) => (
              <option key={prof.id} value={prof.id}>
                {prof.nom} ({prof.specialite})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="card">
          <p>Loading assignments...</p>
        </div>
      ) : timetable ? (
        <div className="card">
          <h3>
            Supervision Assignments for {timetable.professeur.nom}
          </h3>
          <p>
            Total assignments: <strong>{timetable.timetable.length}</strong>
          </p>
          {timetable.timetable.length === 0 ? (
            <p>No exam supervision assignments for this professor.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Module</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Duration</th>
                  <th>Assigned Rooms</th>
                </tr>
              </thead>
              <tbody>
                {timetable.timetable.map((exam) => (
                  <tr key={exam.examen_id}>
                    <td>{exam.module}</td>
                    <td>{exam.date}</td>
                    <td>{exam.heure}</td>
                    <td>{exam.duree} min</td>
                    <td>
                      {exam.salles.map((s, idx) => (
                        <span key={idx}>
                          {s.nom} ({s.batiment})
                          {idx < exam.salles.length - 1 ? ', ' : ''}
                        </span>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* Group by date to show daily load */}
          <div className="card" style={{ marginTop: '20px' }}>
            <h3>Daily Supervision Load</h3>
            {(() => {
              const byDate = {};
              timetable.timetable.forEach(exam => {
                if (!byDate[exam.date]) {
                  byDate[exam.date] = [];
                }
                byDate[exam.date].push(exam);
              });

              return (
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Number of Exams</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(byDate).map(([date, exams]) => (
                      <tr key={date}>
                        <td>{date}</td>
                        <td>{exams.length}</td>
                        <td>
                          {exams.length > 3 ? (
                            <span className="error">⚠️ Exceeds max (3/day)</span>
                          ) : exams.length === 3 ? (
                            <span className="conflict">⚡ At maximum (3/day)</span>
                          ) : (
                            <span className="success">✓ OK</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              );
            })()}
          </div>
        </div>
      ) : (
        <div className="card">
          <p>No timetable data available.</p>
        </div>
      )}
    </div>
  );
};

export default ProfessorView;
