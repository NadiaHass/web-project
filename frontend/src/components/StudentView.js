import React, { useState, useEffect } from 'react';
import { getEtudiants, getStudentTimetable } from '../services/api';
import './Dashboard.css';

const StudentView = () => {
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [timetable, setTimetable] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStudents();
  }, []);

  useEffect(() => {
    if (selectedStudent) {
      loadStudentTimetable(selectedStudent);
    }
  }, [selectedStudent]);

  const loadStudents = async () => {
    try {
      const response = await getEtudiants();
      setStudents(response.data);
      if (response.data.length > 0) {
        setSelectedStudent(response.data[0].id);
      }
    } catch (error) {
      console.error('Error loading students:', error);
    }
  };

  const loadStudentTimetable = async (studentId) => {
    setLoading(true);
    try {
      const response = await getStudentTimetable(studentId);
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
      <h2>Student Timetable Consultation</h2>

      <div className="card">
        <div className="form-group">
          <label>Select Student:</label>
          <select
            value={selectedStudent || ''}
            onChange={(e) => setSelectedStudent(parseInt(e.target.value))}
          >
            {students.map((student) => (
              <option key={student.id} value={student.id}>
                {student.nom} {student.prenom} ({student.matricule})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="card">
          <p>Loading timetable...</p>
        </div>
      ) : timetable ? (
        <div className="card">
          <h3>
            Timetable for {timetable.etudiant.prenom} {timetable.etudiant.nom}
          </h3>
          {timetable.timetable.length === 0 ? (
            <p>No exams scheduled for this student.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Module</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Duration</th>
                  <th>Rooms</th>
                  <th>Supervisors</th>
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
                    <td>
                      {exam.professeurs.map((p, idx) => (
                        <span key={idx}>
                          {p.nom}
                          {idx < exam.professeurs.length - 1 ? ', ' : ''}
                        </span>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : (
        <div className="card">
          <p>No timetable data available.</p>
        </div>
      )}
    </div>
  );
};

export default StudentView;
