import React from "react";
import "./LearningSignal.css";

interface LearningSignalProps {
  subtle?: boolean;
}

const LearningSignal: React.FC<LearningSignalProps> = ({ subtle = true }) => (
  <div className={`learning-signal${subtle ? " subtle" : ""}`}>
    🧠 Based on past queries
  </div>
);

export default LearningSignal;
