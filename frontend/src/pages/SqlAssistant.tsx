import React from 'react';
import Chat from '../components/Chat';

export default function SqlAssistant() {
  return <Chat onBackToDashboard={() => { window.location.href = '/app/dashboard'; }} isPreviewMode={false} />;
}
