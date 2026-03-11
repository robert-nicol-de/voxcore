/**
 * Health Monitor Service
 * Continuously monitors backend health and database connection status
 */

import { apiUrl } from '../lib/api';

let healthCheckInterval: ReturnType<typeof setInterval> | null = null;
let isBackendHealthy = true;
let isDatabaseConnected = false;

export const startHealthMonitoring = () => {
  if (healthCheckInterval) return; // Already running

  const checkHealth = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

      // Check backend health
      const response = await fetch(apiUrl('/health'), {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        handleBackendDown();
        return;
      }

      // Backend is healthy - now check database connection
      if (!isBackendHealthy) {
        console.log('[Health Monitor] Backend recovered');
        isBackendHealthy = true;
      }

      // Check database connection
      await checkDatabaseConnection();
    } catch (error) {
      handleBackendDown();
    }
  };

  const checkDatabaseConnection = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

      const response = await fetch(apiUrl('/api/v1/connection/test'), {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        handleDatabaseDown();
        return;
      }

      const data = await response.json();

      if (data.status === 'connected') {
        if (!isDatabaseConnected) {
          console.log('[Health Monitor] Database connected');
          isDatabaseConnected = true;
        }
        // Update localStorage to reflect connected status
        localStorage.setItem('dbConnectionStatus', 'connected');
        window.dispatchEvent(new Event('connectionStatusChanged'));
      } else {
        handleDatabaseDown();
      }
    } catch (error) {
      handleDatabaseDown();
    }
  };

  const handleBackendDown = () => {
    if (isBackendHealthy) {
      console.log('[Health Monitor] Backend is down - clearing connection');
      isBackendHealthy = false;
      isDatabaseConnected = false;

      // Clear connection data from localStorage
      localStorage.removeItem('selectedDatabase');
      localStorage.removeItem('dbHost');
      localStorage.removeItem('dbDatabase');
      localStorage.removeItem('dbSchema');
      localStorage.removeItem('dbPort');
      localStorage.removeItem('dbUsername');
      localStorage.removeItem('dbConnectionStatus');

      // Dispatch event to notify components
      window.dispatchEvent(
        new CustomEvent('backendDown', {
          detail: { timestamp: new Date().toISOString() },
        })
      );

      // Force UI update
      window.dispatchEvent(new Event('connectionStatusChanged'));
    }
  };

  const handleDatabaseDown = () => {
    if (isDatabaseConnected) {
      console.log('[Health Monitor] Database connection lost');
      isDatabaseConnected = false;
      localStorage.setItem('dbConnectionStatus', 'disconnected');
      window.dispatchEvent(new Event('connectionStatusChanged'));
    }
  };

  // Check immediately
  checkHealth();

  // Then check every 3 seconds
  healthCheckInterval = setInterval(checkHealth, 3000);

  console.log('[Health Monitor] Started monitoring backend health');
};

export const stopHealthMonitoring = () => {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
    healthCheckInterval = null;
    console.log('[Health Monitor] Stopped monitoring');
  }
};

export const isHealthy = () => isBackendHealthy;
export const isDatabaseHealthy = () => isDatabaseConnected;
