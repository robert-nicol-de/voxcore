import { useNavigate } from "react-router-dom";

interface CTAProps {
  heading: string;
  description?: string;
  primaryText: string;
  secondaryText?: string;
  onPrimary?: () => void;
  onSecondary?: () => void;
  className?: string;
}

export default function CTA({
  heading,
  description,
  primaryText,
  secondaryText,
  onPrimary,
  onSecondary,
  className = "",
}: CTAProps) {
  const navigate = useNavigate();

  return (
    <div className={`bg-gradient-to-r from-blue-600/10 to-purple-600/10 border border-white/10 rounded-2xl p-12 text-center ${className}`}>
      <h2 className="text-3xl font-bold mb-2">{heading}</h2>
      {description && <p className="text-gray-400 mb-6 max-w-xl mx-auto">{description}</p>}
      
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={onPrimary || (() => navigate("/app"))}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-8 py-3 rounded-lg transition shadow-lg shadow-blue-500/20"
        >
          {primaryText}
        </button>
        {secondaryText && (
          <button
            onClick={onSecondary}
            className="border border-white/20 hover:border-white/40 text-white font-medium px-8 py-3 rounded-lg transition"
          >
            {secondaryText}
          </button>
        )}
      </div>
    </div>
  );
}
