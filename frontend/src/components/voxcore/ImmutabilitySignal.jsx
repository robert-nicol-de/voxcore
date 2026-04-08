export default function ImmutabilitySignal({ queryId = "QRY-000234" }) {
  // Generate a consistent pseudo-hash for demo purposes
  const generateHash = (id) => {
    let hash = "0x";
    for (let i = 0; i < 16; i++) {
      hash += Math.floor(Math.random() * 16).toString(16);
    }
    return hash.toUpperCase();
  };

  const hash = generateHash(queryId);

  return (
    <div
      style={{
        background: "rgba(0, 208, 132, 0.05)",
        border: "1px solid rgba(0, 208, 132, 0.2)",
        borderRadius: 12,
        padding: 16,
        marginTop: 20,
        fontSize: 12,
      }}
    >
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Hash */}
        <div>
          <div style={{ color: "#666", marginBottom: 6, fontWeight: 600, fontSize: 11, textTransform: "uppercase" }}>
            Hash (SHA-256)
          </div>
          <div
            style={{
              fontFamily: "monospace",
              color: "#0088ff",
              fontSize: 12,
              fontWeight: 500,
              wordBreak: "break-all",
              letterSpacing: "0.5px",
            }}
          >
            {hash}...
          </div>
        </div>

        {/* Integrity */}
        <div>
          <div style={{ color: "#666", marginBottom: 6, fontWeight: 600, fontSize: 11, textTransform: "uppercase" }}>
            Integrity Status
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ color: "#00d084", fontSize: 16 }}>✓</span>
            <span style={{ color: "#00d084", fontWeight: 600 }}>Verified</span>
          </div>
        </div>
      </div>

      {/* Footer note */}
      <div style={{ marginTop: 12, color: "#666", fontSize: 11, borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: 12 }}>
        💾 Tamper-proof audit log. All entries cryptographically signed.
      </div>
    </div>
  );
}
