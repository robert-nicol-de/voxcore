import React from 'react';
import { GovernanceDashboard } from '../screens/GovernanceDashboard';

export default function Dashboard() {
  return <GovernanceDashboard onAskQuestion={() => { window.location.href = '/app'; }} />;
}
