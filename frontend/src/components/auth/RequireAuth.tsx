import React from 'react';
import { Navigate } from 'react-router-dom';

type Props = {
  children: React.ReactNode;
};

export default function RequireAuth({ children }: Props) {
  const token = localStorage.getItem('vox_token') || localStorage.getItem('voxcore_token');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
