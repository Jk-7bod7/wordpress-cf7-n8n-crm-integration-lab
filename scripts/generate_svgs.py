import os

docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
os.makedirs(docs_dir, exist_ok=True)

svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 560" width="900" height="560" style="background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <defs>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="btn-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
  </defs>

  <!-- Browser Chrome Frame -->
  <rect x="20" y="20" width="860" height="520" rx="10" fill="url(#bg-grad)" stroke="#334155" stroke-width="1.5"/>
  <rect x="20" y="20" width="860" height="44" rx="10" fill="#1e293b"/>
  <circle cx="45" cy="42" r="6" fill="#ef4444"/>
  <circle cx="65" cy="42" r="6" fill="#eab308"/>
  <circle cx="85" cy="42" r="6" fill="#22c55e"/>

  <!-- URL Bar -->
  <rect x="120" y="30" width="660" height="24" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="135" y="46" fill="#94a3b8" font-size="12">http://localhost:8080/ — Enterprise Lead Capture Lab</text>

  <!-- Main Content Layout -->
  <text x="60" y="105" fill="#f8fafc" font-size="22" font-weight="700">Enterprise Data Integration Lab</text>
  <text x="60" y="130" fill="#94a3b8" font-size="13">Contact Form 7 Intake → Durable Outbox Worker → n8n Webhook Pipeline</text>

  <!-- Form Card -->
  <rect x="60" y="150" width="500" height="360" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  
  <text x="80" y="185" fill="#e2e8f0" font-size="14" font-weight="600">B2B Schedule Consultation</text>

  <!-- Form Fields -->
  <text x="80" y="215" fill="#94a3b8" font-size="11">Full Name</text>
  <rect x="80" y="225" width="210" height="32" rx="4" fill="#0f172a" stroke="#475569" stroke-width="1"/>
  <text x="92" y="246" fill="#f8fafc" font-size="12">Sarah Jenkins</text>

  <text x="310" y="215" fill="#94a3b8" font-size="11">Work Email</text>
  <rect x="310" y="225" width="230" height="32" rx="4" fill="#0f172a" stroke="#475569" stroke-width="1"/>
  <text x="322" y="246" fill="#f8fafc" font-size="12">s.jenkins@acme-corp.com</text>

  <text x="80" y="280" fill="#94a3b8" font-size="11">Company</text>
  <rect x="80" y="290" width="210" height="32" rx="4" fill="#0f172a" stroke="#475569" stroke-width="1"/>
  <text x="92" y="311" fill="#f8fafc" font-size="12">Acme Corporation</text>

  <text x="310" y="280" fill="#94a3b8" font-size="11">Phone</text>
  <rect x="310" y="290" width="230" height="32" rx="4" fill="#0f172a" stroke="#475569" stroke-width="1"/>
  <text x="322" y="311" fill="#f8fafc" font-size="12">+1-555-019-2834</text>

  <text x="80" y="345" fill="#94a3b8" font-size="11">Inquiry Details</text>
  <rect x="80" y="355" width="460" height="55" rx="4" fill="#0f172a" stroke="#475569" stroke-width="1"/>
  <text x="92" y="378" fill="#cbd5e1" font-size="11">Evaluating automated lead ingestion from web properties to SQLite CRM.</text>

  <!-- Submit Button -->
  <rect x="80" y="428" width="180" height="36" rx="6" fill="url(#btn-grad)"/>
  <text x="115" y="451" fill="#ffffff" font-size="12" font-weight="600">Submit Inquiry</text>

  <text x="280" y="451" fill="#22c55e" font-size="11" font-weight="500">&#10004; Queued via Durable Outbox (ID: 550e8400...)</text>

  <!-- Info Sidebar -->
  <rect x="580" y="150" width="280" height="360" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="600" y="185" fill="#38bdf8" font-size="13" font-weight="700">SYSTEM TELEMETRY</text>

  <rect x="600" y="205" width="240" height="65" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="612" y="226" fill="#94a3b8" font-size="10">IDEMPOTENCY KEY</text>
  <text x="612" y="246" fill="#f1f5f9" font-size="11" font-family="monospace">uuid-v4: e7b2...9f01</text>
  <text x="612" y="260" fill="#22c55e" font-size="10">Status: 200 OK (Processed)</text>

  <rect x="600" y="285" width="240" height="65" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="612" y="306" fill="#94a3b8" font-size="10">DOWNSTREAM PIPELINE</text>
  <text x="612" y="326" fill="#f1f5f9" font-size="11">n8n: :5678 (Healthy)</text>
  <text x="612" y="340" fill="#38bdf8" font-size="10">CRM: :8000 (SQLite Synchronized)</text>

  <rect x="600" y="365" width="240" height="65" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="612" y="386" fill="#94a3b8" font-size="10">SAFETY CONSTRAINTS</text>
  <text x="612" y="406" fill="#eab308" font-size="11">Synthetic Data Only</text>
  <text x="612" y="420" fill="#94a3b8" font-size="10">Loopback Bound: 127.0.0.1</text>
</svg>"""

with open(os.path.join(docs_dir, "01_landing_page_demo.svg"), "w", encoding="utf-8") as f:
    f.write(svg1)
print("Generated 01_landing_page_demo.svg")

svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" width="960" height="480" style="background:#0b1120;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <!-- Canvas Header -->
  <rect x="0" y="0" width="960" height="50" fill="#111827" stroke="#1f2937" stroke-width="1"/>
  <text x="30" y="32" fill="#ff6d5a" font-size="18" font-weight="800">n8n</text>
  <text x="75" y="32" fill="#f9fafb" font-size="14" font-weight="600">Workflow Canvas: WordPress CF7 Intake Pipeline</text>
  <rect x="820" y="12" width="110" height="28" rx="14" fill="#10b981" fill-opacity="0.2" stroke="#10b981" stroke-width="1"/>
  <circle cx="835" cy="26" r="4" fill="#10b981"/>
  <text x="846" y="30" fill="#10b981" font-size="11" font-weight="600">ACTIVE</text>

  <!-- Workflow Connectors -->
  <path d="M 170 210 L 250 210" stroke="#4b5563" stroke-width="2" stroke-dasharray="4"/>
  <path d="M 400 210 L 470 210" stroke="#4b5563" stroke-width="2" stroke-dasharray="4"/>
  <!-- Branch True -->
  <path d="M 610 180 L 670 140" stroke="#10b981" stroke-width="2"/>
  <path d="M 610 240 L 670 300" stroke="#ef4444" stroke-width="2"/>
  <path d="M 810 140 L 860 140" stroke="#3b82f6" stroke-width="2"/>

  <!-- Node 1: Webhook Trigger -->
  <g transform="translate(30, 160)">
    <rect width="140" height="100" rx="8" fill="#1f2937" stroke="#ff6d5a" stroke-width="1.5"/>
    <rect x="10" y="10" width="32" height="32" rx="6" fill="#ff6d5a" fill-opacity="0.15"/>
    <text x="26" y="32" fill="#ff6d5a" font-size="16" text-anchor="middle">&#9889;</text>
    <text x="10" y="65" fill="#f3f4f6" font-size="12" font-weight="600">CF7 Webhook</text>
    <text x="10" y="82" fill="#9ca3af" font-size="10">POST /cf7-lead</text>
  </g>

  <!-- Node 2: Auth & Normalization -->
  <g transform="translate(250, 160)">
    <rect width="150" height="100" rx="8" fill="#1f2937" stroke="#f59e0b" stroke-width="1.5"/>
    <rect x="10" y="10" width="32" height="32" rx="6" fill="#f59e0b" fill-opacity="0.15"/>
    <text x="26" y="32" fill="#f59e0b" font-size="16" text-anchor="middle">&#9881;</text>
    <text x="10" y="65" fill="#f3f4f6" font-size="12" font-weight="600">Auth &amp; Cleanse</text>
    <text x="10" y="82" fill="#9ca3af" font-size="10">X-Webhook-Secret</text>
  </g>

  <!-- Node 3: If Filter -->
  <g transform="translate(470, 160)">
    <rect width="140" height="100" rx="8" fill="#1f2937" stroke="#8b5cf6" stroke-width="1.5"/>
    <rect x="10" y="10" width="32" height="32" rx="6" fill="#8b5cf6" fill-opacity="0.15"/>
    <text x="26" y="32" fill="#8b5cf6" font-size="16" text-anchor="middle">&#9474;</text>
    <text x="10" y="65" fill="#f3f4f6" font-size="12" font-weight="600">Is Valid?</text>
    <text x="10" y="82" fill="#9ca3af" font-size="10">Authorized &amp; Valid</text>
  </g>

  <!-- Node 4: Mock CRM (True) -->
  <g transform="translate(670, 90)">
    <rect width="140" height="100" rx="8" fill="#1f2937" stroke="#3b82f6" stroke-width="1.5"/>
    <rect x="10" y="10" width="32" height="32" rx="6" fill="#3b82f6" fill-opacity="0.15"/>
    <text x="26" y="32" fill="#3b82f6" font-size="16" text-anchor="middle">&#128451;</text>
    <text x="10" y="65" fill="#f3f4f6" font-size="12" font-weight="600">Mock CRM Post</text>
    <text x="10" y="82" fill="#9ca3af" font-size="10">POST /api/leads</text>
  </g>

  <!-- Node 5: Mailpit Notification -->
  <g transform="translate(860, 90)">
    <rect width="80" height="100" rx="8" fill="#1f2937" stroke="#10b981" stroke-width="1.5"/>
    <rect x="10" y="10" width="32" height="32" rx="6" fill="#10b981" fill-opacity="0.15"/>
    <text x="26" y="32" fill="#10b981" font-size="16" text-anchor="middle">&#9993;</text>
    <text x="10" y="65" fill="#f3f4f6" font-size="11" font-weight="600">Mailpit</text>
    <text x="10" y="82" fill="#9ca3af" font-size="9">SMTP 1025</text>
  </g>

  <!-- Node 6: Error / Reject Response -->
  <g transform="translate(670, 270)">
    <rect width="140" height="80" rx="8" fill="#1f2937" stroke="#ef4444" stroke-width="1.5"/>
    <text x="15" y="35" fill="#ef4444" font-size="12" font-weight="600">Reject Response</text>
    <text x="15" y="55" fill="#9ca3af" font-size="10">401 Unauthorized / 400</text>
  </g>

  <!-- Footer Stats -->
  <rect x="30" y="410" width="900" height="45" rx="6" fill="#111827" stroke="#1f2937" stroke-width="1"/>
  <text x="50" y="438" fill="#9ca3af" font-size="11">EXECUTION INVARIANTS: <tspan fill="#10b981" font-weight="600">Idempotency Key Passed</tspan> | <tspan fill="#38bdf8" font-weight="600">PII Logging Masked</tspan> | <tspan fill="#f59e0b" font-weight="600">Retry Backoff Supported</tspan></text>
</svg>"""

with open(os.path.join(docs_dir, "02_n8n_workflow_canvas.svg"), "w", encoding="utf-8") as f:
    f.write(svg2)
print("Generated 02_n8n_workflow_canvas.svg")

svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" width="900" height="520" style="background:#18181b;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <!-- Mailpit Chrome -->
  <rect x="0" y="0" width="900" height="50" fill="#27272a" stroke="#3f3f46" stroke-width="1"/>
  <text x="30" y="32" fill="#a855f7" font-size="20" font-weight="800">Mailpit</text>
  <text x="110" y="32" fill="#71717a" font-size="14">Local Email Sandbox (127.0.0.1:8025)</text>

  <!-- Left Sidebar (Inbox) -->
  <rect x="0" y="50" width="320" height="470" fill="#202023" stroke="#3f3f46" stroke-width="1"/>
  <text x="20" y="80" fill="#a1a1aa" font-size="12" font-weight="600">INTERCEPTED MESSAGES (1)</text>

  <!-- Selected Message Item -->
  <rect x="10" y="95" width="300" height="80" rx="6" fill="#27272a" stroke="#a855f7" stroke-width="1"/>
  <text x="25" y="120" fill="#fafafa" font-size="12" font-weight="600">New Lead Captured: Sarah Jenkins</text>
  <text x="25" y="140" fill="#a1a1aa" font-size="11">From: noreply@portfolio-lab.local</text>
  <text x="25" y="160" fill="#71717a" font-size="10">ID: 550e8400-e29b-41d4-a716-446655440000</text>

  <!-- Main View (Email Details) -->
  <rect x="320" y="50" width="580" height="470" fill="#18181b"/>

  <!-- Message Header Box -->
  <rect x="345" y="75" width="530" height="95" rx="6" fill="#27272a" stroke="#3f3f46" stroke-width="1"/>
  <text x="365" y="102" fill="#fafafa" font-size="14" font-weight="600">Subject: [Lead Intake] Acme Corporation - Sarah Jenkins</text>
  <text x="365" y="125" fill="#a1a1aa" font-size="11">From: &lt;noreply@portfolio-lab.local&gt;   To: &lt;crm-intake@portfolio-lab.local&gt;</text>
  <text x="365" y="148" fill="#22c55e" font-size="10" font-weight="500">&#10004; Synthetic local email delivered via SMTP 127.0.0.1:1025 (Zero External Relay)</text>

  <!-- Message Body Box -->
  <rect x="345" y="190" width="530" height="300" rx="6" fill="#202023" stroke="#3f3f46" stroke-width="1"/>
  <text x="370" y="225" fill="#e4e4e7" font-size="13" font-weight="600">New Prospect Consultation Request</text>

  <text x="370" y="260" fill="#a1a1aa" font-size="11">Submission ID:</text>
  <text x="480" y="260" fill="#38bdf8" font-size="11" font-family="monospace">550e8400-e29b-41d4-a716-446655440000</text>

  <text x="370" y="290" fill="#a1a1aa" font-size="11">Client Name:</text>
  <text x="480" y="290" fill="#f4f4f5" font-size="11">Sarah Jenkins</text>

  <text x="370" y="320" fill="#a1a1aa" font-size="11">Company:</text>
  <text x="480" y="320" fill="#f4f4f5" font-size="11">Acme Corporation</text>

  <text x="370" y="350" fill="#a1a1aa" font-size="11">Email:</text>
  <text x="480" y="350" fill="#f4f4f5" font-size="11">s.jenkins@acme-corp.com</text>

  <text x="370" y="380" fill="#a1a1aa" font-size="11">Phone:</text>
  <text x="480" y="380" fill="#f4f4f5" font-size="11">+1-555-019-2834</text>

  <text x="370" y="410" fill="#a1a1aa" font-size="11">CRM Status:</text>
  <text x="480" y="410" fill="#22c55e" font-size="11" font-weight="600">SYNCHRONIZED (SQLite Leads Table)</text>

  <rect x="370" y="440" width="480" height="35" rx="4" fill="#27272a"/>
  <text x="385" y="462" fill="#9ca3af" font-size="10">Security Note: All test artifacts contain synthetic data only. No real PII processed.</text>
</svg>"""

with open(os.path.join(docs_dir, "03_mailpit_inbox.svg"), "w", encoding="utf-8") as f:
    f.write(svg3)
print("Generated 03_mailpit_inbox.svg")
