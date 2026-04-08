
function Button({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className="btn-primary bg-[var(--accent-primary)] hover:bg-blue-500 px-6 py-3 rounded-lg shadow-lg shadow-blue-600/30 transition-all duration-200 active:scale-97"
    >
      {children}
    </button>
  );
}

export function SecondaryButton({ children, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className="btn-secondary border border-[var(--accent-primary)] hover:border-blue-500 px-6 py-3 rounded-lg transition-all duration-200 active:scale-97"
    >
      {children}
    </button>
  );
}

export default Button;
