export default function DrilldownModal({ data, onClose }) {
  if (!data) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div className="bg-white p-6 rounded-xl w-96">
        <h2 className="text-lg font-bold mb-2">
          {data.label}
        </h2>
        <p>Value: {data.value}</p>
        <button onClick={onClose} className="mt-4">
          Close
        </button>
      </div>
    </div>
  );
}
