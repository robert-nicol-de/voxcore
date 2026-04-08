export default function StepConnector({ setConnector, next }) {
  return (
    <>
      <h2 className="text-xl mb-4">Connect your data</h2>

      <select
        onChange={(e) => setConnector(e.target.value)}
        className="w-full p-2 bg-gray-800 rounded-lg"
      >
        <option value="postgres">Postgres</option>
        <option value="sqlserver">SQL Server</option>
        <option value="file">CSV</option>
      </select>

      <button onClick={next} className="mt-4 bg-neon-green px-4 py-2 rounded">
        Continue
      </button>
    </>
  );
}
