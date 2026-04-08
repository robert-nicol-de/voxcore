export default function Card({ title, description, highlight = false }) {
  return (
    <div className={`
      p-8
      rounded-xl
      border border-white/10
      bg-white/[0.02]
      backdrop-blur-sm
      hover:bg-white/[0.06]
      hover:shadow-[0_0_30px_rgba(59,130,246,0.15)]
      hover:-translate-y-1
      transition-all duration-300
      ${highlight ? "ring-1 ring-blue-500/40" : ""}
    `}>
      <h3 className="text-lg font-semibold mb-2">
        {title}
      </h3>
      <p className="text-white/60 text-sm">
        {description}
      </p>
    </div>
  );
}
