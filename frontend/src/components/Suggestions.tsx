export default function Suggestions({ suggestions, onClick }) {
  return (
    <div className="flex gap-2 flex-wrap">
      {suggestions.map((s, i) => (
        <button
          key={i}
          onClick={() => onClick(s)}
          className="bg-gray-200 px-3 py-1 rounded-full text-sm"
        >
          {s}
        </button>
      ))}
    </div>
  );
}
