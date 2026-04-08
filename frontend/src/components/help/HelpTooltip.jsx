import { useState } from "react";
import "./HelpTooltip.css";

export default function HelpTooltip({ title, content, position = "top" }) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="help-tooltip-container">
      <button
        className="help-icon"
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        onClick={() => setVisible(!visible)}
        title={title}
        aria-label={`Help: ${title}`}
      >
        ?
      </button>

      {visible && (
        <div className={`help-tooltip help-tooltip-${position}`}>
          {title && <div className="tooltip-title">{title}</div>}
          <div className="tooltip-content">{content}</div>
          <div className="tooltip-arrow" />
        </div>
      )}
    </div>
  );
}
