import os
import subprocess

docker_bin = r'C:\Users\om192\AppData\Local\Programs\DockerDesktop\resources\bin'
env = os.environ.copy()
env['PATH'] = f'{docker_bin};' + env['PATH']
repo_dir = r'C:\Users\om192\Downloads\11_AI_Freelancer\case-studies\automation\wordpress-cf7-n8n-mock-crm-lab'
docker_exe = os.path.join(docker_bin, 'docker.exe')

def run_wp(*args):
    cmd = [docker_exe, 'compose', 'exec', 'wordpress', 'wp'] + list(args) + ['--allow-root']
    res = subprocess.run(cmd, cwd=repo_dir, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running wp {' '.join(args)}: {res.stderr}")
    else:
        print(f"WP: {res.stdout.strip()}")
    return res

# 1. Read cf7-form-template.html
form_template_path = os.path.join(repo_dir, 'wordpress', 'cf7-form-template.html')
with open(form_template_path, 'r', encoding='utf-8') as f:
    form_content = f.read()

# 2. Update post 4 meta _form
# Contact Form 7 stores form markup in postmeta _form
run_wp('post', 'meta', 'update', '4', '_form', form_content)

# 3. Create or update static front page
res = run_wp('post', 'list', '--post_type=page', '--name=lead-intake-demo', '--field=ID')
page_id = res.stdout.strip()
if not page_id:
    res = run_wp('post', 'create', '--post_type=page', '--post_title=Lead Intake Demo', '--post_name=lead-intake-demo', '--post_status=publish', '--post_content=[contact-form-7 id="4" title="Contact form 1"]', '--porcelain')
    page_id = res.stdout.strip()

print(f"Landing page ID: {page_id}")
run_wp('option', 'update', 'show_on_front', 'page')
run_wp('option', 'update', 'page_on_front', page_id)

# 4. Trigger plugin table activation
php_code = """
global $wpdb;
$table_name = $wpdb->prefix . 'cf7_n8n_outbox';
$charset_collate = $wpdb->get_charset_collate();
$sql = "CREATE TABLE IF NOT EXISTS $table_name (
    id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    submission_id VARCHAR(128) NOT NULL,
    payload LONGTEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    retry_count INT(11) NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_submission_id (submission_id),
    KEY idx_status (status)
) $charset_collate;";
require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
dbDelta($sql);
echo 'Outbox table ensured. ';
"""
run_wp('eval', php_code)
print("WordPress CF7 setup completed successfully.")
