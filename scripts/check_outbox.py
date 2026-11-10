import os
import subprocess

docker_bin = r'C:\Users\om192\AppData\Local\Programs\DockerDesktop\resources\bin'
env = os.environ.copy()
env['PATH'] = f'{docker_bin};' + env['PATH']
repo_dir = r'C:\Users\om192\Downloads\11_AI_Freelancer\case-studies\automation\wordpress-cf7-n8n-mock-crm-lab'
docker_exe = os.path.join(docker_bin, 'docker.exe')

cmd = [
    docker_exe, 'compose', 'exec', 'wordpress',
    'wp', 'eval',
    '''global $wpdb;
    $table = $wpdb->prefix . "cf7_n8n_outbox";
    $rows = $wpdb->get_results("SELECT * FROM $table");
    echo "Outbox count: " . count($rows) . "\\n";
    foreach($rows as $r) {
        echo "ID: " . $r->id . " | SubID: " . $r->submission_id . " | Status: " . $r->status . " | Retries: " . $r->retry_count . " | Err: " . $r->last_error . "\\n";
        echo "Payload: " . $r->payload . "\\n";
    }
    ''',
    '--allow-root'
]
res = subprocess.run(cmd, cwd=repo_dir, env=env, capture_output=True, text=True)
print(res.stdout)
print(res.stderr)
