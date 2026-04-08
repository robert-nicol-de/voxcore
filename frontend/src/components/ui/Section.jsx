export default function Section({ title, subtitle, center, children }) {
  return (
    <section className={`section ${center ? "center" : ""}`}>
      {title && <h2 className="section-title">{title}</h2>}
      {subtitle && <p className="section-subtitle">{subtitle}</p>}
      {children}
    </section>
  );
}
