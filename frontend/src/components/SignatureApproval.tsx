import React from "react";
import './SignatureApproval.css';

const SignatureApproval: React.FC = () => (
  <div className="signature-approval">
    <div className="approval-icon">✔</div>
    <div className="approval-title">Query Approved</div>
    <div className="approval-message">Policy checks passed<br />Safe for production</div>
  </div>
);
export default SignatureApproval;
