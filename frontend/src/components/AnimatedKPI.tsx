import React, { useEffect, useState } from "react";

const AnimatedKPI: React.FC<{ value: number; duration?: number }> = ({ value, duration = 600 }) => {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const startTime = performance.now();
    const animate = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      setDisplay(Math.floor(progress * value));
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    requestAnimationFrame(animate);
    return () => setDisplay(value);
  }, [value, duration]);
  return <span className="animated-kpi">{display}</span>;
};
export default AnimatedKPI;
