# Troubleshooting Guide — WordPress Contact Form 7 → n8n CRM Integration Lab

**Project:** WordPress Contact Form 7 → n8n CRM Integration Lab  

---

## 1. Docker Desktop Installation & Windows Elevation

### Issue:
Running the Docker Desktop installer or `wsl --install` fails with `The requested operation requires elevation` (Exit Code 1) or hangs.

### Cause:
On Windows 11, installing Docker Desktop and enabling the WSL 2 backend requires elevated Administrator privileges to install system drivers, register the `com.docker.service` Windows Service, and configure virtual network adapters.

### Resolution:
1. **Interactive Elevated Installation:**  
   Open PowerShell as **Administrator** (`Run as Administrator`) and execute:
   ```powershell
   wsl --install --no-distribution
   winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
   ```
   Reboot Windows when prompted.
2. **Alternative Host Runner (No Admin Required):**  
   If running in a non-elevated environment, use the native host runner described in [SETUP.md](SETUP.md#method-b-native-host-execution-no-docker-required) to run Python, Mailpit, and the acceptance tests natively.

---

## 2. Port Binding Conflicts

### Issue:
`Bind for 127.0.0.1:8080 failed: port is already allocated` or similar for ports `5678`, `8000`, `8025`, `1025`.

### Diagnostic Command:
```powershell
Get-NetTCPConnection -LocalPort 8080, 5678, 8000, 8025, 1025 -State Listen | Format-Table -AutoSize
```

### Resolution:
1. Identify the process ID (`OwningProcess`) holding the port. (Note: On Windows gaming machines, **Steam** (`steamwebhelper.exe`) frequently binds to `127.0.0.1:8080` for CEF remote debugging).
2. Either terminate the conflicting process or change the host port mapping in `.env`:
   ```bash
   WP_PORT=8088
   CRM_PORT=8001
   ```

---

## 3. Webhook Dispatch Returns HTTP 401 Unauthorized

### Issue:
WordPress outbox logs show: `HTTP 401: Unauthorized: Invalid or missing X-Webhook-Secret header`.

### Resolution:
1. Ensure the secret configured in the WordPress plugin matches the `WEBHOOK_SECRET` environment variable in n8n.
2. In WordPress Admin, navigate to **Contact > n8n Outbox** and verify the **Webhook Secret Key** field.

---

## 4. Contact Form 7 Shows Submission Error

### Issue:
Submitting the form results in an error message with a red or orange border.

### Resolution:
1. **Orange border:** Contact Form 7 spam filter or reCAPTCHA rejection. Check that required fields are filled out.
2. **Red border:** Mail server or webhook failure. Inspect the WordPress outbox table (`wp_cf7_n8n_outbox`) in the admin panel to view the exact error message and verify whether the event was safely enqueued for retry.
