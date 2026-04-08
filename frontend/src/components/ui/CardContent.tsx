export default function CardContent({ children, className = "" }: any) {
  return (
    <div className={`card-content ${className}`.trim()}>
      {children}
    </div>
  );
}
