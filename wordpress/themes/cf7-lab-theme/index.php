<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PORTFOLIO-024: WordPress Contact Form 7 → n8n → Mock CRM Integration Lab</title>
    <link rel="stylesheet" href="<?php echo get_stylesheet_uri(); ?>">
</head>
<body>
    <div class="container">
        <header>
            <span class="badge badge-success">PORTFOLIO-024 REFERENCE IMPLEMENTATION</span>
            <h1>Enterprise Form Intake & CRM Integration Lab</h1>
            <p>A tested, resilient demonstration architecture connecting WordPress Contact Form 7 to n8n and an SQLite-backed Mock CRM with authenticated webhooks, durable outbox queuing, and Mailpit notification verification.</p>
        </header>

        <div class="grid">
            <div class="card">
                <h2>Live Lead Intake Form (CF7)</h2>
                <?php
                if (shortcode_exists('contact-form-7')) {
                    echo do_shortcode('[contact-form-7 id="1" title="Lead Intake Form"]');
                } else {
                    // Fallback static demonstration form if CF7 is not yet active
                    include(dirname(__DIR__) . '/cf7-form-template.html');
                }
                ?>
            </div>

            <div class="card">
                <h2>Integration Flow Architecture</h2>
                <ul class="architecture-steps">
                    <li><span class="badge">1. Intake</span> Visitor submits Contact Form 7 with Full Name, Email, Phone, Company, Service, and Message.</li>
                    <li><span class="badge">2. Hook & UUID</span> Plugin intercepts submission, generates unique <code>submission_id</code>, and sanitizes payload.</li>
                    <li><span class="badge">3. Authenticated Webhook</span> Form data dispatched to n8n with <code>X-Webhook-Secret</code> header (5s timeout).</li>
                    <li><span class="badge">4. Durable Outbox</span> If n8n or network drops, event is queued in local outbox with exponential retries.</li>
                    <li><span class="badge">5. n8n Validation</span> n8n validates schema, normalizes email, checks idempotency key against CRM.</li>
                    <li><span class="badge">6. Mock CRM Commit</span> Lead persisted to SQLite; duplicate submissions return existing record without duplication.</li>
                    <li><span class="badge">7. Email Sandbox</span> Notification dispatched via SMTP to local Mailpit sandbox for zero external leakage.</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
