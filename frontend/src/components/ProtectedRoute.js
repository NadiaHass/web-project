import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated, getUserRole } from '../services/auth';

function ProtectedRoute({ children, allowedRoles = [] }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  const userRole = getUserRole();
  if (allowedRoles.length > 0 && !allowedRoles.includes(userRole)) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
