export default function Footer() {
  return (
    <footer style={{ padding: 20, background: "#101828", color: "#fff", textAlign: "center" }}>
      <span>© {new Date().getFullYear()} VoxCore</span>
    </footer>
  );
}
