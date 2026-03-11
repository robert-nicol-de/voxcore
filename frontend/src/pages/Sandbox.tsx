import React from 'react';
import { DevSpace } from './DevSpace';

export default function Sandbox() {
  const token = localStorage.getItem('voxcore_token') || '';
  return <DevSpace token={token} />;
}
