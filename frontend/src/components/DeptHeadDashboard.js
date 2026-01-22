import React, { useState, useEffect } from 'react';
import { 
  getDepartements, 
  getFormations, 
  getExamens, 
  getConflicts, 
  getStatistics,
  getPendingDeptHeadApprovals,
  approveExamDeptHead
} from '../services/api';
import './Dashboard.css';

const DeptHeadDashboard = () => {
  const [departements, setDepartements] = useState([]);
  const [selectedDept, setSelectedDept] = useState(null);
  const [formations, setFormations] = useState([]);
  const [examens, setExamens] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [stats, setStats] = useState(null);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDepartements();
    loadPendingApprovals();
  }, []);

  useEffect(() => {
    if (selectedDept) {
      loadDepartmentData(selectedDept);
    }
  }, [selectedDept]);

  const loadDepartements = async () => {
    try {
      const response = await getDepartements();
      setDepartements(response.data);
      if (response.data.length > 0) {
        setSelectedDept(response.data[0].id);
      }
    } catch (error) {
      console.error('Error loading departments:', error);
    }
  };

  const loadDepartmentData = async (deptId) => {
    try {
      const formationsRes = await getFormations(deptId);
      setFormations(formationsRes.data);

      const examensRes = await getExamens();
      // Filter exams by department modules
      const allExamens = examensRes.data;
      setExamens(allExamens); // Simplified - in real app, filter by dept

      const conflictsRes = await getConflicts();
      setConflicts(conflictsRes.data);

      const statsRes = await getStatistics();
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading department data:', error);
    }
  };

  const loadPendingApprovals = async () => {
    try {
      const response = await getPendingDeptHeadApprovals();
      setPendingApprovals(response.data);
    } catch (error) {
      console.error('Error loading pending approvals:', error);
    }
  };

  const handleApprove = async (examenId, approved) => {
    setLoading(true);
    try {
      await approveExamDeptHead(examenId, approved);
      await loadPendingApprovals();
      await loadDepartmentData(selectedDept);
      alert(`Exam ${approved ? 'approved' : 'rejected'} successfully!`);
    } catch (error) {
      console.error('Error approving exam:', error);
      alert('Error approving exam. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getApprovalStatus = (examen) => {
    if (examen.dept_head_approved === 1 && examen.vice_dean_approved === 1) {
      return { text: 'Fully Approved', class: 'approved' };
    } else if (examen.dept_head_approved === 1) {
      return { text: 'Pending Vice-Dean', class: 'pending-vice-dean' };
    } else if (examen.dept_head_approved === -1) {
      return { text: 'Rejected', class: 'rejected' };
    } else {
      return { text: 'Pending Approval', class: 'pending' };
    }
  };

  const deptConflicts = conflicts.filter(c => {
    // Filter conflicts related to this department
    // This is simplified - in a real app, you'd check module/formation relationships
    return true;
  });

  return (
    <div className="dashboard">
      <h2>Department Head Dashboard</h2>

      <div className="card">
        <div className="form-group">
          <label>Select Department:</label>
          <select
            value={selectedDept || ''}
            onChange={(e) => setSelectedDept(parseInt(e.target.value))}
          >
            {departements.map((dept) => (
              <option key={dept.id} value={dept.id}>
                {dept.nom}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        <h3>Pending Approvals ({pendingApprovals.length})</h3>
        {pendingApprovals.length === 0 ? (
          <p>No exams pending your approval.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Module ID</th>
                <th>Date</th>
                <th>Time</th>
                <th>Duration</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pendingApprovals.map((examen) => (
                <tr key={examen.id}>
                  <td>{examen.id}</td>
                  <td>{examen.module_id}</td>
                  <td>{examen.date}</td>
                  <td>{examen.heure}</td>
                  <td>{examen.duree} min</td>
                  <td>
                    <button 
                      onClick={() => handleApprove(examen.id, true)}
                      disabled={loading}
                      className="btn-approve"
                    >
                      Approve
                    </button>
                    <button 
                      onClick={() => handleApprove(examen.id, false)}
                      disabled={loading}
                      className="btn-reject"
                    >
                      Reject
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {selectedDept && (
        <>
          <div className="card">
            <h3>Department Training Programs</h3>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Level</th>
                  <th>Modules</th>
                </tr>
              </thead>
              <tbody>
                {formations.map((formation) => (
                  <tr key={formation.id}>
                    <td>{formation.id}</td>
                    <td>{formation.nom}</td>
                    <td>{formation.niveau}</td>
                    <td>{formation.nb_modules}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h3>Conflicts per Training Program</h3>
            {deptConflicts.length === 0 ? (
              <p>No conflicts detected for this department.</p>
            ) : (
              <div>
                <p>Total conflicts: {deptConflicts.length}</p>
                {deptConflicts.slice(0, 10).map((conflict, idx) => (
                  <div key={idx} className="conflict">
                    <strong>{conflict.description}</strong>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <h3>Department Statistics</h3>
            {stats && stats.department_stats && (
              <div>
                {stats.department_stats
                  .filter(dept => {
                    // Match selected department
                    const deptName = departements.find(d => d.id === selectedDept)?.nom;
                    return dept.departement === deptName;
                  })
                  .map((dept, idx) => (
                    <div key={idx} className="stats-grid">
                      <div className="stat-item">
                        <strong>Exam Count:</strong> {dept.exam_count}
                      </div>
                      <div className="stat-item">
                        <strong>Student Count:</strong> {dept.student_count}
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>

          <div className="card">
            <h3>Department Exams ({examens.length})</h3>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Module ID</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Duration</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {examens.map((examen) => {
                  const status = getApprovalStatus(examen);
                  return (
                    <tr key={examen.id}>
                      <td>{examen.id}</td>
                      <td>{examen.module_id}</td>
                      <td>{examen.date}</td>
                      <td>{examen.heure}</td>
                      <td>{examen.duree} min</td>
                      <td>
                        <span className={`status-badge ${status.class}`}>
                          {status.text}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default DeptHeadDashboard;
