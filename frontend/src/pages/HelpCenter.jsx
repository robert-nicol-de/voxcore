import { useState } from "react";
import "./HelpCenter.css";

export default function HelpCenter() {
  const [selectedSection, setSelectedSection] = useState("getting-started");

  const sections = {
    "getting-started": {
      title: "Getting Started",
      articles: [
        {
          id: "what-is-voxcore",
          title: "What is VoxCore?",
          content: (
            <>
              <p>
                VoxCore is the control layer between AI and your production database.
              </p>
              <p>
                Every time an AI system (like ChatGPT, Claude, or your internal AI assistant)
                generates a database query, VoxCore receives it BEFORE execution.
              </p>
              <h4>What VoxCore Does:</h4>
              <ul>
                <li>✓ Analyzes queries for safety and risk</li>
                <li>✓ Checks queries against your organization's policies</li>
                <li>✓ Blocks dangerous queries before execution</li>
                <li>✓ Logs all attempts for audit compliance</li>
              </ul>
              <h4>Why This Matters:</h4>
              <p>
                AI systems sometimes generate unsafe queries. They might:
              </p>
              <ul>
                <li>Scan entire tables without WHERE clauses</li>
                <li>Attempt to access sensitive data</li>
                <li>Run resource-intensive operations</li>
                <li>Execute destructive commands (DROP, TRUNCATE)</li>
              </ul>
              <p>
                VoxCore prevents these problems automatically.
              </p>
            </>
          ),
        },
        {
          id: "how-it-works",
          title: "How Query Protection Works",
          content: (
            <>
              <h4>The VoxCore Flow:</h4>
              <pre>
{`1. AI generates query
   ↓
2. Query sent to VoxCore
   ↓
3. VoxCore analyzes query
   ├─ Scores risk (0-100)
   ├─ Checks policies
   └─ Evaluates impact
   ↓
4. VoxCore makes decision
   ├─ ALLOWED → Query executes
   ├─ BLOCKED → Query rejected
   └─ PENDING → Requires approval
   ↓
5. Result logged to audit`}
              </pre>
              <h4>Decision Logic:</h4>
              <ul>
                <li><strong>ALLOWED:</strong> Query is safe and within policy</li>
                <li><strong>BLOCKED:</strong> Query is dangerous or violates policy</li>
                <li><strong>PENDING:</strong> Query requires approval from admin</li>
              </ul>
              <h4>All Queries Are Logged:</h4>
              <p>
                Every query attempt (allowed, blocked, or pending) is recorded with:
              </p>
              <ul>
                <li>Who executed it (user + team)</li>
                <li>What they tried to run</li>
                <li>Risk score and justification</li>
                <li>Decision and reason</li>
                <li>Timestamp</li>
              </ul>
            </>
          ),
        },
        {
          id: "first-query",
          title: "Running Your First Query",
          content: (
            <>
              <h4>Step 1: Go to Playground</h4>
              <p>Click "Playground" in the main navigation.</p>
              <h4>Step 2: Enter or Paste a Query</h4>
              <p>
                Type a SQL query or paste one from your AI assistant. Example:
              </p>
              <pre>{`SELECT * FROM users WHERE created_at > NOW() - INTERVAL 7 DAYS`}</pre>
              <h4>Step 3: Submit</h4>
              <p>Click "Execute Query" and wait for analysis.</p>
              <h4>Step 4: Review Decision</h4>
              <p>
                VoxCore shows:
              </p>
              <ul>
                <li><strong>Risk Score:</strong> 0-100 (low to dangerous)</li>
                <li><strong>Decision:</strong> ALLOWED, BLOCKED, or PENDING</li>
                <li><strong>Reason:</strong> Why this decision was made</li>
              </ul>
              <h4>If BLOCKED:</h4>
              <ul>
                <li>Review the reason</li>
                <li>Modify the query to be safer</li>
                <li>Try again</li>
              </ul>
              <h4>If PENDING:</h4>
              <ul>
                <li>An admin will review and approve/reject</li>
                <li>You'll be notified of the decision</li>
              </ul>
            </>
          ),
        },
      ],
    },
    "risk-scoring": {
      title: "Understanding Risk",
      articles: [
        {
          id: "risk-score",
          title: "What is a Risk Score?",
          content: (
            <>
              <p>
                Every query gets a <strong>Risk Score</strong> from 0-100.
              </p>
              <h4>Risk Levels:</h4>
              <ul>
                <li><strong>0-30 (LOW):</strong> Safe queries with WHERE, LIMIT, and specific columns</li>
                <li><strong>30-70 (MEDIUM):</strong> Queries with some concerns (large LIMIT, multiple joins)</li>
                <li><strong>70-100 (HIGH):</strong> Dangerous queries (full table scans, no restrictions)</li>
              </ul>
              <h4>Examples:</h4>
              <p>
                <strong>LOW (Score: 15)</strong>
              </p>
              <pre>
{`SELECT id, name FROM users 
WHERE created_at > NOW() - INTERVAL 7 DAYS
LIMIT 50`}
              </pre>
              <p>
                <strong>MEDIUM (Score: 45)</strong>
              </p>
              <pre>
{`SELECT * FROM orders
JOIN customers ON orders.customer_id = customers.id
WHERE date > NOW() - INTERVAL 30 DAYS`}
              </pre>
              <p>
                <strong>HIGH (Score: 85)</strong>
              </p>
              <pre>
{`SELECT * FROM users`}
              </pre>
            </>
          ),
        },
        {
          id: "scoring-factors",
          title: "How Scoring Works",
          content: (
            <>
              <h4>VoxCore scores queries on multiple factors:</h4>
              <table className="help-table">
                <thead>
                  <tr>
                    <th>Factor</th>
                    <th>Risk Increase</th>
                    <th>Why?</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>No WHERE clause</td>
                    <td>+20</td>
                    <td>Full table scan, unpredictable impact</td>
                  </tr>
                  <tr>
                    <td>SELECT *</td>
                    <td>+10</td>
                    <td>Returns all columns, may expose sensitive data</td>
                  </tr>
                  <tr>
                    <td>Large LIMIT</td>
                    <td>+15</td>
                    <td>Returns many rows, uses memory</td>
                  </tr>
                  <tr>
                    <td>Multiple JOINs (3+)</td>
                    <td>+15</td>
                    <td>Complex queries, hard to predict performance</td>
                  </tr>
                  <tr>
                    <td>CROSS JOIN</td>
                    <td>+25</td>
                    <td>Cartesian product, can be huge</td>
                  </tr>
                  <tr>
                    <td>Destructive (DROP, TRUNCATE, DELETE)</td>
                    <td>+50</td>
                    <td>Can permanently destroy data</td>
                  </tr>
                </tbody>
              </table>
              <h4>Smart Scoring:</h4>
              <p>
                VoxCore combines these factors intelligently. A query with no WHERE
                clause but explicit LIMIT 10 is lower risk than one with WHERE but
                LIMIT 1000000.
              </p>
            </>
          ),
        },
        {
          id: "common-factors",
          title: "Common Risk Factors",
          content: (
            <>
              <h4>🔴 Factors That Increase Risk:</h4>
              <ul>
                <li><strong>No WHERE clause:</strong> Scans entire table</li>
                <li><strong>SELECT *:</strong> Returns all columns</li>
                <li><strong>Large LIMIT (1000+):</strong> Returns many rows</li>
                <li><strong>Multiple JOINs:</strong> Complex cartesian products</li>
                <li><strong>CROSS JOIN:</strong> Cartesian product (can be huge)</li>
                <li><strong>Destructive operations:</strong> DROP, TRUNCATE, DELETE</li>
                <li><strong>Slow queries:</strong> Operations that take minutes</li>
              </ul>
              <h4>🟢 Factors That Reduce Risk:</h4>
              <ul>
                <li><strong>Specific WHERE:</strong> Filters to few rows</li>
                <li><strong>Explicit columns:</strong> SELECT col1, col2 (not *)</li>
                <li><strong>Small LIMIT:</strong> LIMIT 50 or less</li>
                <li><strong>Simple queries:</strong> Single table or few joins</li>
                <li><strong>READ-ONLY:</strong> SELECT only (no modifications)</li>
                <li><strong>Fast queries:</strong> Returns in milliseconds</li>
              </ul>
            </>
          ),
        },
      ],
    },
    "decisions": {
      title: "Query Decisions",
      articles: [
        {
          id: "blocked-queries",
          title: "Blocked Queries",
          content: (
            <>
              <p>
                A query is <strong>BLOCKED</strong> when it violates your organization's
                policies or exceeds acceptable risk.
              </p>
              <h4>Common Reasons for Blocking:</h4>
              <ul>
                <li><strong>Policy Violation:</strong> Violates a rule set by your admin</li>
                <li><strong>High Risk Score:</strong> Risk score exceeds threshold</li>
                <li><strong>Destructive Operation:</strong> Would modify or delete data</li>
                <li><strong>Sensitive Access:</strong> Tries to access protected columns</li>
              </ul>
              <h4>What You Can Do:</h4>
              <ol>
                <li>Read the blocking reason carefully</li>
                <li>Modify your query to address the issue</li>
                <li>Common fixes:
                  <ul>
                    <li>Add a WHERE clause to limit rows</li>
                    <li>Specify columns instead of SELECT *</li>
                    <li>Add a LIMIT clause</li>
                    <li>Simplify JOINs</li>
                  </ul>
                </li>
                <li>Try the modified query</li>
              </ol>
              <h4>Request Approval:</h4>
              <p>
                If you believe the query is safe, you can request approval from an admin.
                They can review and approve dangerous queries if needed.
              </p>
            </>
          ),
        },
        {
          id: "allowed-queries",
          title: "Allowed Queries",
          content: (
            <>
              <p>
                A query is <strong>ALLOWED</strong> when it's safe and within policy.
              </p>
              <h4>What This Means:</h4>
              <ul>
                <li>✓ Risk score is below threshold</li>
                <li>✓ No policy violations</li>
                <li>✓ Query will execute safely</li>
                <li>✓ Results will be returned immediately</li>
              </ul>
              <h4>The Query Executes:</h4>
              <p>
                Your query runs against the database and returns results. You can see:
              </p>
              <ul>
                <li>Data returned by the query</li>
                <li>Query execution time</li>
                <li>Risk assessment (why it was safe)</li>
              </ul>
              <h4>All Allowed Queries Are Logged:</h4>
              <p>
                Even allowed queries are recorded in the audit log with timestamp,
                user, and details for compliance.
              </p>
            </>
          ),
        },
        {
          id: "pending-approval",
          title: "Pending Approval",
          content: (
            <>
              <p>
                A query is <strong>PENDING APPROVAL</strong> when it's risky enough
                that an admin must review it before execution.
              </p>
              <h4>What Happens:</h4>
              <ol>
                <li>You submit a query</li>
                <li>VoxCore analyzes it</li>
                <li>Decision: PENDING (requires human review)</li>
                <li>Admin receives notification</li>
                <li>Admin reviews and approves or rejects</li>
                <li>You're notified of the decision</li>
              </ol>
              <h4>Why Pending?</h4>
              <p>
                Pending queries usually have:
              </p>
              <ul>
                <li>High risk score but no policy violations</li>
                <li>Unusual access patterns</li>
                <li>Large data operations</li>
                <li>Access to sensitive tables</li>
              </ul>
              <h4>You're Not Blocked, Just Waiting:</h4>
              <p>
                Pending approval doesn't mean "no." It means your admin needs to
                review for context. Many pending queries are approved.
              </p>
            </>
          ),
        },
      ],
    },
    "policies": {
      title: "Policies",
      articles: [
        {
          id: "what-are-policies",
          title: "What are Policies?",
          content: (
            <>
              <p>
                <strong>Policies</strong> are organization-specific rules that define
                what queries are allowed.
              </p>
              <h4>Example Policy:</h4>
              <p>
                "No full table scans on the users table"
              </p>
              <h4>How Policies Work:</h4>
              <ol>
                <li>Admin creates a policy</li>
                <li>Admin sets a rule (e.g., "Require WHERE clause")</li>
                <li>Admin chooses action (BLOCK or REQUIRE_APPROVAL)</li>
                <li>Policy applies to all users in organization</li>
                <li>VoxCore checks every query against policies</li>
              </ol>
              <h4>Why Policies?</h4>
              <ul>
                <li>Enforce organizational standards</li>
                <li>Protect sensitive data</li>
                <li>Ensure compliance</li>
                <li>Prevent expensive queries</li>
              </ul>
            </>
          ),
        },
        {
          id: "create-policy",
          title: "How to Create Policies",
          content: (
            <>
              <p>
                <strong>Admins only.</strong> Only organization administrators can
                create and manage policies.
              </p>
              <h4>Steps:</h4>
              <ol>
                <li>Go to Settings → Policies</li>
                <li>Click "New Policy"</li>
                <li>Enter policy name (e.g., "No Full Scans")</li>
                <li>Choose rule type (see examples below)</li>
                <li>Set condition (depends on rule type)</li>
                <li>Choose action:
                  <ul>
                    <li>BLOCK: Reject the query</li>
                    <li>REQUIRE_APPROVAL: Send to admin for review</li>
                  </ul>
                </li>
                <li>Click "Create Policy"</li>
              </ol>
              <h4>Policy Takes Effect Immediately:</h4>
              <p>
                All future queries are checked against the new policy.
              </p>
            </>
          ),
        },
        {
          id: "policy-examples",
          title: "Policy Examples",
          content: (
            <>
              <h4>Example 1: No Full Table Scans</h4>
              <ul>
                <li><strong>Name:</strong> "No Full Scans on users"</li>
                <li><strong>Rule Type:</strong> no_full_scan</li>
                <li><strong>Condition:</strong> (empty)</li>
                <li><strong>Action:</strong> BLOCK</li>
                <li><strong>Effect:</strong> Any SELECT without WHERE is blocked</li>
              </ul>
              <h4>Example 2: Maximum Joins</h4>
              <ul>
                <li><strong>Name:</strong> "Max 3 JOINs"</li>
                <li><strong>Rule Type:</strong> max_joins</li>
                <li><strong>Condition:</strong> <code>{'{ "max": 3 }'}</code></li>
                <li><strong>Action:</strong> REQUIRE_APPROVAL</li>
                <li><strong>Effect:</strong> Queries with 4+ JOINs require approval</li>
              </ul>
              <h4>Example 3: Row Limits</h4>
              <ul>
                <li><strong>Name:</strong> "Max 1000 rows"</li>
                <li><strong>Rule Type:</strong> max_rows</li>
                <li><strong>Condition:</strong> <code>{'{ "max_limit": 1000 }'}</code></li>
                <li><strong>Action:</strong> BLOCK</li>
                <li><strong>Effect:</strong> LIMIT greater than 1000 is blocked</li>
              </ul>
              <h4>Example 4: No Destructive Operations</h4>
              <ul>
                <li><strong>Name:</strong> "Block DELETE"</li>
                <li><strong>Rule Type:</strong> destructive_check</li>
                <li><strong>Condition:</strong> (empty)</li>
                <li><strong>Action:</strong> BLOCK</li>
                <li><strong>Effect:</strong> DROP, TRUNCATE, DELETE all blocked</li>
              </ul>
            </>
          ),
        },
      ],
    },
    "audit": {
      title: "Audit Logs",
      articles: [
        {
          id: "what-is-logged",
          title: "What is Logged?",
          content: (
            <>
              <p>
                Every query attempt is recorded to the audit log, whether ALLOWED,
                BLOCKED, or PENDING.
              </p>
              <h4>Information Logged:</h4>
              <ul>
                <li><strong>Timestamp:</strong> When the query was attempted</li>
                <li><strong>User:</strong> Who executed the query</li>
                <li><strong>Organization:</strong> Which team/org</li>
                <li><strong>Query:</strong> The SQL that was executed (or attempted)</li>
                <li><strong>Risk Score:</strong> VoxCore's risk assessment</li>
                <li><strong>Decision:</strong> ALLOWED, BLOCKED, or PENDING</li>
                <li><strong>Reason:</strong> Why that decision was made</li>
                <li><strong>Policies Violated:</strong> Which policies (if any) were violated</li>
              </ul>
              <h4>Complete Audit Trail:</h4>
              <p>
                The audit log is immutable (cannot be changed or deleted). This is
                critical for compliance and security.
              </p>
            </>
          ),
        },
        {
          id: "read-logs",
          title: "How to Read Logs",
          content: (
            <>
              <h4>Access Logs:</h4>
              <p>
                Go to "Audit" in the main navigation. You'll see all queries.
              </p>
              <h4>Understanding Each Entry:</h4>
              <p>
                <strong>Example Log Entry:</strong>
              </p>
              <pre>
{`Timestamp: 2025-04-03 14:30:45 UTC
User: alice@company.com
Organization: ACME Corp
Query: SELECT * FROM users WHERE created_at > NOW() - INTERVAL 7 DAYS
Risk Score: 35%
Decision: ALLOWED
Reason: Query has WHERE clause and reasonable risk score
Policies Violated: None`}
              </pre>
              <h4>Filter and Search:</h4>
              <ul>
                <li><strong>By User:</strong> See all queries from a person</li>
                <li><strong>By Decision:</strong> Show only BLOCKED or PENDING</li>
                <li><strong>By Date:</strong> Filter to a time range</li>
                <li><strong>By Table:</strong> Show queries affecting specific table</li>
              </ul>
              <h4>Export Logs:</h4>
              <p>
                Click "Export" to download logs as CSV for external reporting.
              </p>
            </>
          ),
        },
        {
          id: "compliance",
          title: "Compliance Use",
          content: (
            <>
              <p>
                Audit logs help meet compliance requirements (SOC2, HIPAA, GDPR, etc).
              </p>
              <h4>Common Compliance Questions:</h4>
              <p>
                <strong>Q: Who accessed sensitive data?</strong>
              </p>
              <p>
                A: Filter logs to show queries on sensitive tables, see users and
                timestamps.
              </p>
              <p>
                <strong>Q: Were any dangerous operations attempted?</strong>
              </p>
              <p>
                A: Filter to show BLOCKED queries. See what was blocked and why.
              </p>
              <p>
                <strong>Q: What data did each user access?</strong>
              </p>
              <p>
                A: Filter by user, see all their queries and what they accessed.
              </p>
              <p>
                <strong>Q: Is there a complete audit trail?</strong>
              </p>
              <p>
                A: Yes, immutable log of all attempts with full context.
              </p>
              <h4>Reports:</h4>
              <p>
                Generate standard reports for auditors:
              </p>
              <ul>
                <li>"All queries from [date] to [date]"</li>
                <li>"All BLOCKED queries"</li>
                <li>"All queries by [user]"</li>
                <li>"Data accessed on [table]"</li>
              </ul>
            </>
          ),
        },
      ],
    },
  };

  const currentSection = sections[selectedSection];
  const currentArticle = selectedSection
    ? currentSection.articles[0]
    : null;

  const [selectedArticle, setSelectedArticle] = useState(
    currentArticle?.id || "what-is-voxcore"
  );

  const article = currentSection.articles.find((a) => a.id === selectedArticle);

  return (
    <div className="help-center">
      <div className="help-container">
        {/* Sidebar */}
        <div className="help-sidebar">
          <h3 className="help-sidebar-title">Help Center</h3>
          <nav className="help-nav">
            {Object.entries(sections).map(([key, section]) => (
              <div key={key}>
                <button
                  className={`help-section-button ${selectedSection === key ? "active" : ""}`}
                  onClick={() => {
                    setSelectedSection(key);
                    setSelectedArticle(section.articles[0].id);
                  }}
                >
                  {section.title}
                </button>
                {selectedSection === key && (
                  <div className="help-articles">
                    {section.articles.map((article) => (
                      <button
                        key={article.id}
                        className={`help-article-button ${selectedArticle === article.id ? "active" : ""}`}
                        onClick={() => setSelectedArticle(article.id)}
                      >
                        {article.title}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div className="help-content">
          {article && (
            <>
              <h2 className="help-article-title">{article.title}</h2>
              <div className="help-article-body">{article.content}</div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
