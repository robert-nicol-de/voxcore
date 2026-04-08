export default function Footer() {
  return (
    <footer style={{ background: "#0a1120", borderTop: "1px solid #1e293b", color: "#fff", padding: "56px 0 0 0" }}>
      <div className="footer-grid" style={{ maxWidth: 1200, margin: "auto", display: "grid", gridTemplateColumns: "1fr repeat(4, 1fr)", gap: 32, marginBottom: 40, marginTop: 40 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
            <img
              src="/assets/logo-icon.png"
              alt="VoxCore"
              style={{ width: 40, height: 40 }}
            />
            <div>
              <div style={{ fontWeight: 700, fontSize: 16 }}>VoxCore</div>
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>Governance Layer</div>
            </div>
          </div>
          <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.6 }}>
            Enterprise AI governance and intelligence layer for secure data access.
          </p>
        </div>
        <div>
          <h4 style={{ fontWeight: 700, marginBottom: 12 }}>PRODUCT</h4>
          <p>App</p>
          <p>Pricing</p>
          <p>Features</p>
        </div>
        <div>
          <h4 style={{ fontWeight: 700, marginBottom: 12 }}>COMPANY</h4>
          <p>About</p>
          <p>Blog</p>
          <p>Careers</p>
        </div>
        <div>
          <h4 style={{ fontWeight: 700, marginBottom: 12 }}>RESOURCES</h4>
          <p>Documentation</p>
          <p>API Docs</p>
          <p>Support</p>
        </div>
        <div>
          <h4 style={{ fontWeight: 700, marginBottom: 12 }}>LEGAL</h4>
          <p>Privacy</p>
          <p>Terms</p>
          <p>Security</p>
        </div>
      </div>
      <div style={{ textAlign: "center", color: "#64748b", marginBottom: 16 }}>
        © 2026 VoxCore. All rights reserved.
      </div>
      <div style={{ textAlign: "right", color: "#64748b", fontSize: 14, maxWidth: 1200, margin: "0 auto 0 auto", paddingBottom: 16 }}>
        Secure AI for Data Access
      </div>
    </footer>
  );
}
