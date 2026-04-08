import { useState, useEffect } from "react";
import "./OnboardingModal.css";

export default function OnboardingModal({ onComplete }) {
  const [step, setStep] = useState(1);
  const [environment, setEnvironment] = useState("dev");
  const [dataType, setDataType] = useState("analytics");
  const [hasShown, setHasShown] = useState(false);

  // Check if onboarding has been dismissed
  useEffect(() => {
    const dismissed = localStorage.getItem("voxcore_onboarding_dismissed");
    if (dismissed) {
      setHasShown(true);
    }
  }, []);

  const handleDismiss = () => {
    localStorage.setItem("voxcore_onboarding_dismissed", "true");
    localStorage.setItem("voxcore_environment", environment);
    localStorage.setItem("voxcore_data_type", dataType);
    setHasShown(true);
    if (onComplete) onComplete();
  };

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    }
  };

  const handleStartDemo = () => {
    handleDismiss();
  };

  if (hasShown) {
    return null;
  }

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-modal">
        {/* Close button */}
        <button
          className="onboarding-close"
          onClick={handleDismiss}
          aria-label="Close onboarding"
        >
          ✕
        </button>

        {/* Progress indicator */}
        <div className="onboarding-progress">
          <div className={`progress-dot ${step >= 1 ? "active" : ""}`} />
          <div className={`progress-dot ${step >= 2 ? "active" : ""}`} />
          <div className={`progress-dot ${step >= 3 ? "active" : ""}`} />
        </div>

        {/* Step 1: Positioning */}
        {step === 1 && (
          <div className="onboarding-step-1">
            <div className="onboarding-icon">🛡️</div>
            <h2>Welcome to VoxCore</h2>
            <p className="onboarding-tagline">
              The control layer between AI and your production database
            </p>
            <p className="onboarding-description">
              VoxCore protects your database from unsafe AI-generated queries.
              <br />
              <br />
              Every query is analyzed for risk, checked against policies, and
              blocked before it can damage your data.
            </p>
            <button className="onboarding-cta" onClick={handleNext}>
              👉 Start with a live demo
            </button>
          </div>
        )}

        {/* Step 2: Context Setup */}
        {step === 2 && (
          <div className="onboarding-step-2">
            <h2>Personalize Your Setup</h2>
            <p className="onboarding-subtitle">
              Tell us about your environment so we can show relevant examples
            </p>

            {/* Environment selector */}
            <div className="setup-section">
              <label>Your Environment</label>
              <div className="radio-group">
                <label className={`radio-option ${environment === "dev" ? "selected" : ""}`}>
                  <input
                    type="radio"
                    value="dev"
                    checked={environment === "dev"}
                    onChange={(e) => setEnvironment(e.target.value)}
                  />
                  <span>Development</span>
                </label>
                <label className={`radio-option ${environment === "staging" ? "selected" : ""}`}>
                  <input
                    type="radio"
                    value="staging"
                    checked={environment === "staging"}
                    onChange={(e) => setEnvironment(e.target.value)}
                  />
                  <span>Staging</span>
                </label>
                <label className={`radio-option ${environment === "prod" ? "selected" : ""}`}>
                  <input
                    type="radio"
                    value="prod"
                    checked={environment === "prod"}
                    onChange={(e) => setEnvironment(e.target.value)}
                  />
                  <span>Production</span>
                </label>
              </div>
            </div>

            {/* Data type selector */}
            <div className="setup-section">
              <label>Primary Data Type</label>
              <div className="radio-group">
                <label className={`radio-option ${dataType === "analytics" ? "selected" : ""}`}>
                  <input
                    type="radio"
                    value="analytics"
                    checked={dataType === "analytics"}
                    onChange={(e) => setDataType(e.target.value)}
                  />
                  <span>Analytics & Reporting</span>
                </label>
                <label className={`radio-option ${dataType === "customer" ? "selected" : ""}`}>
                  <input
                    type="radio"
                    value="customer"
                    checked={dataType === "customer"}
                    onChange={(e) => setDataType(e.target.value)}
                  />
                  <span>Customer Data</span>
                </label>
                <label className={`radio-option ${dataType === "financial" ? "selected" : ""}`}>
                  <input
                    type="radio"
                    value="financial"
                    checked={dataType === "financial"}
                    onChange={(e) => setDataType(e.target.value)}
                  />
                  <span>Financial Data</span>
                </label>
              </div>
            </div>

            <button className="onboarding-cta" onClick={handleNext}>
              👉 Continue
            </button>
          </div>
        )}

        {/* Step 3: Ready State */}
        {step === 3 && (
          <div className="onboarding-step-3">
            <div className="ready-icon">✨</div>
            <h2>You're Ready</h2>
            <p className="onboarding-description">
              Watch how VoxCore automatically blocks an unsafe query, then try it
              yourself.
            </p>

            <div className="ready-checklist">
              <div className="check-item">
                <span className="check-mark">✓</span>
                <span>Environment: {environment.charAt(0).toUpperCase() + environment.slice(1)}</span>
              </div>
              <div className="check-item">
                <span className="check-mark">✓</span>
                <span>
                  Data Type:{" "}
                  {dataType === "analytics"
                    ? "Analytics & Reporting"
                    : dataType === "customer"
                    ? "Customer Data"
                    : "Financial Data"}
                </span>
              </div>
              <div className="check-item">
                <span className="check-mark">✓</span>
                <span>Demo query ready</span>
              </div>
            </div>

            <button className="onboarding-cta onboarding-cta-large" onClick={handleStartDemo}>
              👉 Run Demo Query
            </button>

            <p className="onboarding-skip-text">
              You can always revisit this in Settings → Help & Onboarding
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
