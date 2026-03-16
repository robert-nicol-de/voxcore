import React from "react";

const TrustBar: React.FC = () => (
  <section className="trust-bar">
    <div className="trust-bar-content">
      <span className="trust-bar-title">Trusted by data teams building AI-powered systems</span>
      <div className="trust-logos">
        <span className="logo-placeholder">PostgreSQL</span>
        <span className="logo-placeholder">Snowflake</span>
        <span className="logo-placeholder">BigQuery</span>
        <span className="logo-placeholder">Databricks</span>
        <span className="logo-placeholder">AWS</span>
        <span className="logo-placeholder">Azure</span>
      </div>
    </div>
  </section>
);

export default TrustBar;
