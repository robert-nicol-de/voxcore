export default function StepTest({ connector, next }) {
  const test = async () => {
    await fetch("/api/connectors/test", {
      method: "POST",
      body: JSON.stringify({ connector_type: connector }),
    });

    next();
  };

  return (
    <>
      <h2>Test Connection</h2>
      <button onClick={test}>Test</button>
    </>
  );
}
