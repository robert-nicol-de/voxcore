// TimelinePanel.jsx
// Displays the VoxCore Data Intelligence Timeline as a scrollable feed
import React, { useEffect, useState } from 'react';

export default function TimelinePanel({ days, entity, metric }) {
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {
    let url = '/api/timeline';
    const params = [];
    if (days) params.push(`days=${days}`);
    if (entity) params.push(`entity=${entity}`);
    if (metric) params.push(`metric=${metric}`);
    if (params.length) url += '?' + params.join('&');
    fetch(url).then(r => r.json()).then(d => setTimeline(d.timeline || []));
  }, [days, entity, metric]);

  return (
    <div className="timeline-panel">
      <h3>🕒 Data Intelligence Timeline</h3>
      <ul className="timeline-feed">
        {timeline.map((event, idx) => (
          <li key={idx} className={`timeline-event ${event.type || ''}`}>
            <div className="timeline-date">{event.detected_at || event.timestamp}</div>
            <div className="timeline-type">{event.type && event.type.replace('_', ' ')}</div>
            <div className="timeline-desc">
              {event.description || event.insight || `${event.metric || ''} ${event.change || ''} ${event.entity || ''}`}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
