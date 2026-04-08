export default function Button({ children }) {
  return (
    <button
      className="
      bg-blue-600 
      hover:bg-blue-500 
      text-white 
      px-6 py-3 
      rounded-xl 
      font-medium 
      transition-all duration-300 
      hover:shadow-[0_0_20px_rgba(59,130,246,0.4)]
    ">
      {children}
    </button>
  );
}

export function SecondaryButton({ children }) {
  return (
    <button
      className="
      bg-gray-700 
      hover:bg-gray-600 
      text-white 
      px-6 py-3 
      rounded-xl 
      font-medium 
      transition-all duration-300 
      hover:shadow-[0_0_20px_rgba(107,114,128,0.4)]
    ">
      {children}
    </button>
  );
}
