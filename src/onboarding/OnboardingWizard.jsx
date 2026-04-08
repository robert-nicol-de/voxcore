import { useState } from "react";
import StepWelcome from "./StepWelcome";
import StepConnector from "./StepConnector";
import StepTest from "./StepTest";
import StepFirstQuery from "./StepFirstQuery";

export default function OnboardingWizard() {
  const [step, setStep] = useState(0);
  const [connector, setConnector] = useState(null);

  const steps = [
    <StepWelcome next={() => setStep(1)} />,
    <StepConnector setConnector={setConnector} next={() => setStep(2)} />,
    <StepTest connector={connector} next={() => setStep(3)} />,
    <StepFirstQuery connector={connector} />,
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 text-white">
      <div className="w-[600px] bg-gray-900 p-6 rounded-2xl shadow-lg">
        {steps[step]}
      </div>
    </div>
  );
}
