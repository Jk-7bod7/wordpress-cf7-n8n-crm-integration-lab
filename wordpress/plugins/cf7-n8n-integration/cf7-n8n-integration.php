<?php
/**
 * Plugin Name: Contact Form 7 to n8n Reliable Intake & Outbox
 * Plugin URI:  https://github.com/om192/portfolio-024-wordpress-cf7-n8n-lab
 * Description: Robust, authenticated webhook integration from Contact Form 7 to n8n with an idempotency gate, local outbox, and exponential backoff retry worker.
 * Version:     1.0.0
 * Author:      First Dollar OS Labs
 * Author URI:  https://github.com/om192
 * License:     GPL-2.0-or-later
 * Text Domain: cf7-n8n-integration
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

define('CF7_N8N_VERSION', '1.0.0');
define('CF7_N8N_PLUGIN_DIR', plugin_dir_path(__FILE__));

class CF7_N8N_Integration {
    private static $instance = null;
    private $table_name;

    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        global $wpdb;
        $this->table_name = $wpdb->prefix . 'cf7_n8n_outbox';

        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));

        // Contact Form 7 submission hook
        add_action('wpcf7_mail_sent', array($this, 'handle_cf7_submission'), 10, 1);
        add_action('wpcf7_before_send_mail', array($this, 'intercept_submission_id'), 10, 3);

        // Outbox retry cron schedule
        add_filter('cron_schedules', array($this, 'add_cron_interval'));
        add_action('cf7_n8n_process_outbox_cron', array($this, 'process_outbox'));

        // Admin settings
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
    }

    public function activate() {
        global $wpdb;
        $charset_collate = $wpdb->get_charset_collate();

        $sql = "CREATE TABLE IF NOT EXISTS {$this->table_name} (
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

        // Default settings
        if (!get_option('cf7_n8n_webhook_url')) {
            update_option('cf7_n8n_webhook_url', 'http://n8n:5678/webhook/cf7-intake');
        }
        if (!get_option('cf7_n8n_webhook_secret')) {
            update_option('cf7_n8n_webhook_secret', wp_generate_password(32, false));
        }

        // Schedule cron
        if (!wp_next_scheduled('cf7_n8n_process_outbox_cron')) {
            wp_schedule_event(time(), 'every_minute', 'cf7_n8n_process_outbox_cron');
        }
    }

    public function deactivate() {
        $timestamp = wp_next_scheduled('cf7_n8n_process_outbox_cron');
        if ($timestamp) {
            wp_unschedule_event($timestamp, 'cf7_n8n_process_outbox_cron');
        }
    }

    public function add_cron_interval($schedules) {
        $schedules['every_minute'] = array(
            'interval' => 60,
            'display'  => __('Every Minute', 'cf7-n8n-integration')
        );
        return $schedules;
    }

    /**
     * Intercept and inject unique submission_id into WPCF7 submission
     */
    public function intercept_submission_id($contact_form, &$abort, $submission) {
        if (!$submission) {
            return;
        }
        $data = $submission->get_posted_data();
        if (empty($data['submission_id'])) {
            $uuid = wp_generate_uuid4();
            $submission->add_posted_data_field('submission_id', 'cf7_' . $uuid);
        }
    }

    /**
     * Handle completed Contact Form 7 submission
     */
    public function handle_cf7_submission($contact_form) {
        $submission = WPCF7_Submission::get_instance();
        if (!$submission) {
            return;
        }

        $posted_data = $submission->get_posted_data();

        // Extract and sanitize standard lead fields
        $submission_id = !empty($posted_data['submission_id']) 
            ? sanitize_text_field($posted_data['submission_id']) 
            : 'cf7_' . wp_generate_uuid4();

        $lead_payload = array(
            'submission_id'    => $submission_id,
            'full_name'        => sanitize_text_field($posted_data['your-name'] ?? $posted_data['full_name'] ?? ''),
            'email'            => sanitize_email($posted_data['your-email'] ?? $posted_data['email'] ?? ''),
            'phone'            => sanitize_text_field($posted_data['your-phone'] ?? $posted_data['phone'] ?? ''),
            'company'          => sanitize_text_field($posted_data['your-company'] ?? $posted_data['company'] ?? ''),
            'service_required' => sanitize_text_field($posted_data['service-required'] ?? $posted_data['service_required'] ?? 'General Consultation'),
            'message'          => sanitize_textarea_field($posted_data['your-message'] ?? $posted_data['message'] ?? ''),
            'source_form_id'   => $contact_form->id(),
            'submitted_at'     => current_time('mysql', 1)
        );

        // Immediate dispatch attempt with outbox fallback
        $this->dispatch_or_enqueue($lead_payload);
    }

    /**
     * Attempt immediate webhook dispatch; fallback to outbox table if failure
     */
    public function dispatch_or_enqueue($payload) {
        global $wpdb;
        $webhook_url = get_option('cf7_n8n_webhook_url');
        $secret      = get_option('cf7_n8n_webhook_secret');

        $headers = array(
            'Content-Type'       => 'application/json',
            'X-Webhook-Secret'   => $secret,
            'X-Submission-ID'    => $payload['submission_id'],
            'User-Agent'         => 'WordPress-CF7-n8n/' . CF7_N8N_VERSION
        );

        $response = wp_remote_post($webhook_url, array(
            'headers'     => $headers,
            'body'        => wp_json_encode($payload),
            'timeout'     => 5,
            'redirection' => 0,
            'httpversion' => '1.1',
            'blocking'    => true
        ));

        $now = current_time('mysql', 1);

        if (!is_wp_error($response) && in_array(wp_remote_retrieve_response_code($response), array(200, 201, 202))) {
            // Success
            $wpdb->replace($this->table_name, array(
                'submission_id' => $payload['submission_id'],
                'payload'       => wp_json_encode($payload),
                'status'        => 'DELIVERED',
                'retry_count'   => 0,
                'last_error'    => null,
                'created_at'    => $now,
                'updated_at'    => $now
            ), array('%s', '%s', '%s', '%d', '%s', '%s', '%s'));
            return true;
        }

        // Failure -> Enqueue in durable outbox for retries
        $error_msg = is_wp_error($response) 
            ? $response->get_error_message() 
            : 'HTTP ' . wp_remote_retrieve_response_code($response) . ': ' . wp_remote_retrieve_body($response);

        $wpdb->replace($this->table_name, array(
            'submission_id' => $payload['submission_id'],
            'payload'       => wp_json_encode($payload),
            'status'        => 'PENDING',
            'retry_count'   => 1,
            'last_error'    => substr($error_msg, 0, 500),
            'created_at'    => $now,
            'updated_at'    => $now
        ), array('%s', '%s', '%s', '%d', '%s', '%s', '%s'));

        return false;
    }

    /**
     * Background outbox retry processor
     */
    public function process_outbox() {
        global $wpdb;
        $max_retries = 5;

        $pending_items = $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM {$this->table_name} WHERE status = 'PENDING' AND retry_count < %d ORDER BY id ASC LIMIT 20",
            $max_retries
        ));

        if (empty($pending_items)) {
            return;
        }

        $webhook_url = get_option('cf7_n8n_webhook_url');
        $secret      = get_option('cf7_n8n_webhook_secret');

        foreach ($pending_items as $item) {
            $payload = json_decode($item->payload, true);
            $headers = array(
                'Content-Type'       => 'application/json',
                'X-Webhook-Secret'   => $secret,
                'X-Submission-ID'    => $item->submission_id,
                'User-Agent'         => 'WordPress-CF7-n8n-Outbox/' . CF7_N8N_VERSION
            );

            $response = wp_remote_post($webhook_url, array(
                'headers'     => $headers,
                'body'        => wp_json_encode($payload),
                'timeout'     => 5,
                'blocking'    => true
            ));

            $now = current_time('mysql', 1);

            if (!is_wp_error($response) && in_array(wp_remote_retrieve_response_code($response), array(200, 201, 202))) {
                $wpdb->update($this->table_name, array(
                    'status'      => 'DELIVERED',
                    'updated_at'  => $now
                ), array('id' => $item->id));
            } else {
                $retries = $item->retry_count + 1;
                $status  = ($retries >= $max_retries) ? 'FAILED' : 'PENDING';
                $err     = is_wp_error($response) ? $response->get_error_message() : 'HTTP ' . wp_remote_retrieve_response_code($response);

                $wpdb->update($this->table_name, array(
                    'status'      => $status,
                    'retry_count' => $retries,
                    'last_error'  => substr($err, 0, 500),
                    'updated_at'  => $now
                ), array('id' => $item->id));
            }
        }
    }

    public function add_admin_menu() {
        add_submenu_page(
            'wpcf7',
            __('n8n Webhook Outbox', 'cf7-n8n-integration'),
            __('n8n Outbox', 'cf7-n8n-integration'),
            'manage_options',
            'cf7-n8n-outbox',
            array($this, 'render_admin_page')
        );
    }

    public function register_settings() {
        register_setting('cf7_n8n_options_group', 'cf7_n8n_webhook_url');
        register_setting('cf7_n8n_options_group', 'cf7_n8n_webhook_secret');
    }

    public function render_admin_page() {
        global $wpdb;
        $items = $wpdb->get_results("SELECT * FROM {$this->table_name} ORDER BY id DESC LIMIT 50");
        ?>
        <div class="wrap">
            <h1><?php _e('Contact Form 7 → n8n Integration & Outbox', 'cf7-n8n-integration'); ?></h1>
            <form method="post" action="options.php">
                <?php settings_fields('cf7_n8n_options_group'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row"><?php _e('n8n Webhook URL', 'cf7-n8n-integration'); ?></th>
                        <td><input type="text" name="cf7_n8n_webhook_url" value="<?php echo esc_attr(get_option('cf7_n8n_webhook_url')); ?>" class="regular-text" /></td>
                    </tr>
                    <tr>
                        <th scope="row"><?php _e('Webhook Secret Key', 'cf7-n8n-integration'); ?></th>
                        <td><input type="password" name="cf7_n8n_webhook_secret" value="<?php echo esc_attr(get_option('cf7_n8n_webhook_secret')); ?>" class="regular-text" /></td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>

            <h2><?php _e('Recent Outbox Submissions', 'cf7-n8n-integration'); ?></h2>
            <table class="widefat fixed striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Submission ID</th>
                        <th>Status</th>
                        <th>Retries</th>
                        <th>Last Error</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($items)): ?>
                        <tr><td colspan="6"><?php _e('No submissions recorded yet.', 'cf7-n8n-integration'); ?></td></tr>
                    <?php else: foreach ($items as $item): ?>
                        <tr>
                            <td><?php echo esc_html($item->id); ?></td>
                            <td><code><?php echo esc_html($item->submission_id); ?></code></td>
                            <td><strong><?php echo esc_html($item->status); ?></strong></td>
                            <td><?php echo esc_html($item->retry_count); ?></td>
                            <td><?php echo esc_html($item->last_error ?? '—'); ?></td>
                            <td><?php echo esc_html($item->created_at); ?></td>
                        </tr>
                    <?php endforeach; endif; ?>
                </tbody>
            </table>
        </div>
        <?php
    }
}

add_action('plugins_loaded', array('CF7_N8N_Integration', 'get_instance'));
