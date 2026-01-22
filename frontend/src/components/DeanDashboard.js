import React, { useState, useEffect } from 'react';
import { 
  getStatistics, 
  getConflicts, 
  getExamens, 
  getSalles,
  getPendingViceDeanApprovals,
  approveExamViceDean
} from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

const DeanDashboard = () => {
  const [statistics, setStatistics] = useState(null);
  const [conflicts, setConflicts] = useState([]);
  const [examens, setExamens] = useState([]);
  const [roomUtilization, setRoomUtilization] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const statsRes = await getStatistics();
      setStatistics(statsRes.data);

      const conflictsRes = await getConflicts();
      setConflicts(conflictsRes.data);

      const examensRes = await getExamens({ include_pending: true });
      setExamens(examensRes.data);

      // Load pending vice-dean approvals
      const approvalsRes = await getPendingViceDeanApprovals();
      setPendingApprovals(approvalsRes.data);

      // Prepare room utilization data
      if (statsRes.data.room_utilization) {
        const roomData = Object.entries(statsRes.data.room_utilization).map(([name, count]) => ({
          name,
          usage: count
        }));
        setRoomUtilization(roomData);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleApprove = async (examenId, approved) => {
    setLoading(true);
    try {
      await approveExamViceDean(examenId, approved);
      await loadData();
      alert(`Exam ${approved ? 'approved' : 'rejected'} successfully!`);
    } catch (error) {
      console.error('Error approving exam:', error);
      alert(error.response?.data?.detail || 'Error approving exam. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Calculate conflict rate per department
  const conflictRateByDept = statistics?.department_stats?.map(dept => ({
    department: dept.departement,
    conflictRate: dept.exam_count > 0 ? (conflicts.length / dept.exam_count * 100).toFixed(2) : 0
  })) || [];

  return (
    <div className="dashboard">
      <h2>Dean & Vice-Dean Dashboard - Global Strategic View</h2>

      <div className="card">
        <h3>Pending Vice-Dean Approvals ({pendingApprovals.length})</h3>
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

      {statistics && (
        <>
          <div className="card">
            <h3>Key Performance Indicators</h3>
            <div className="stats-grid">
              <div className="stat-item kpi">
                <div className="kpi-value">{statistics.total_students}</div>
                <div className="kpi-label">Total Students</div>
              </div>
              <div className="stat-item kpi">
                <div className="kpi-value">{statistics.total_professors}</div>
                <div className="kpi-label">Total Professors</div>
              </div>
              <div className="stat-item kpi">
                <div className="kpi-value">{statistics.total_exams}</div>
                <div className="kpi-label">Total Exams</div>
              </div>
              <div className="stat-item kpi">
                <div className="kpi-value">{statistics.conflict_count}</div>
                <div className="kpi-label">Active Conflicts</div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>Overall Room Occupancy</h3>
            {roomUtilization.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={roomUtilization}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="usage" fill="#8884d8" name="Exam Usage" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p>No room utilization data available.</p>
            )}
          </div>

          <div className="card">
            <h3>Conflict Rates by Department</h3>
            {conflictRateByDept.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={conflictRateByDept}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="department" />
                  <YAxis label={{ value: 'Conflict Rate %', angle: -90 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="conflictRate" fill="#82ca9d" name="Conflict Rate (%)" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p>No department conflict data available.</p>
            )}
          </div>

          <div className="card">
            <h3>Department Statistics</h3>
            <table>
              <thead>
                <tr>
                  <th>Department</th>
                  <th>Exam Count</th>
                  <th>Student Count</th>
                </tr>
              </thead>
              <tbody>
                {statistics.department_stats?.map((dept, idx) => (
                  <tr key={idx}>
                    <td>{dept.departement}</td>
                    <td>{dept.exam_count}</td>
                    <td>{dept.student_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h3>Room Utilization Details</h3>
            <table>
              <thead>
                <tr>
                  <th>Room</th>
                  <th>Usage Count</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(statistics.room_utilization || {}).map(([room, count]) => (
                  <tr key={room}>
                    <td>{room}</td>
                    <td>{count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h3>Exam Timetable Overview</h3>
            <p>Total scheduled exams: {examens.length}</p>
            {examens.length > 0 && (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {examens.slice(0, 10).map((examen) => (
                    <tr key={examen.id}>
                      <td>{examen.id}</td>
                      <td>{examen.date}</td>
                      <td>{examen.heure}</td>
                      <td>{examen.duree} min</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default DeanDashboard;
