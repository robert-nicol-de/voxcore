export default function StepFirstQuery({ connector }) {
  const run = async () => {
    const res = await fetch("/api/connectors/query", {
      method: "POST",
      body: JSON.stringify({
        connector_type: connector,
        query: "SELECT TOP 10 * FROM your_table",
      }),
    });

    const data = await res.json();
    console.log(data);
  };

  return (
    <>
      <h2>Your first insight</h2>
      <button onClick={run}>Run Sample Query</button>
    </>
  );
}
