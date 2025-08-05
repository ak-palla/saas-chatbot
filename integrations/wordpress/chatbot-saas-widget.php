<?php
/**
 * Plugin Name: Chatbot SaaS Widget
 * Plugin URI: https://github.com/your-org/chatbot-saas-widget
 * Description: Easily integrate AI-powered chatbots into your WordPress site with voice support and advanced customization.
 * Version: 1.0.0
 * Author: Chatbot SaaS Team
 * Author URI: https://yourchatbot.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: chatbot-saas-widget
 * Domain Path: /languages
 * Requires at least: 5.0
 * Tested up to: 6.4
 * Requires PHP: 7.4
 * Network: false
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('CHATBOT_SAAS_VERSION', '1.0.0');
define('CHATBOT_SAAS_PLUGIN_URL', plugin_dir_url(__FILE__));
define('CHATBOT_SAAS_PLUGIN_PATH', plugin_dir_path(__FILE__));

class ChatbotSaaSWidget {
    
    private $options;
    
    public function __construct() {
        add_action('init', array($this, 'init'));
    }
    
    public function init() {
        // Load plugin text domain
        load_plugin_textdomain('chatbot-saas-widget', false, dirname(plugin_basename(__FILE__)) . '/languages');
        
        // Initialize admin
        if (is_admin()) {
            add_action('admin_menu', array($this, 'add_admin_menu'));
            add_action('admin_init', array($this, 'admin_init'));
            add_action('admin_enqueue_scripts', array($this, 'admin_enqueue_scripts'));
        }
        
        // Initialize frontend
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_footer', array($this, 'render_widget'));
        
        // Add shortcode support
        add_shortcode('chatbot_widget', array($this, 'shortcode_handler'));
        
        // Add Gutenberg block support
        add_action('init', array($this, 'register_gutenberg_block'));
        
        // AJAX handlers
        add_action('wp_ajax_chatbot_test_connection', array($this, 'test_connection'));
        add_action('wp_ajax_chatbot_save_settings', array($this, 'save_settings'));
        
        // Get options
        $this->options = get_option('chatbot_saas_options', array());
    }
    
    public function add_admin_menu() {
        add_options_page(
            __('Chatbot SaaS Widget', 'chatbot-saas-widget'),
            __('Chatbot Widget', 'chatbot-saas-widget'),
            'manage_options',
            'chatbot-saas-widget',
            array($this, 'admin_page')
        );
    }
    
    public function admin_init() {
        register_setting('chatbot_saas_group', 'chatbot_saas_options', array($this, 'sanitize_options'));
        
        // General Settings Section
        add_settings_section(
            'chatbot_saas_general',
            __('General Settings', 'chatbot-saas-widget'),
            array($this, 'general_section_callback'),
            'chatbot-saas-widget'
        );
        
        // Chatbot ID Field
        add_settings_field(
            'chatbot_id',
            __('Chatbot ID', 'chatbot-saas-widget'),
            array($this, 'chatbot_id_callback'),
            'chatbot-saas-widget',
            'chatbot_saas_general'
        );
        
        // API URL Field
        add_settings_field(
            'api_url',
            __('API URL', 'chatbot-saas-widget'),
            array($this, 'api_url_callback'),
            'chatbot-saas-widget',
            'chatbot_saas_general'
        );
        
        // Appearance Settings Section
        add_settings_section(
            'chatbot_saas_appearance',
            __('Appearance Settings', 'chatbot-saas-widget'),
            array($this, 'appearance_section_callback'),
            'chatbot-saas-widget'
        );
        
        // Theme Field
        add_settings_field(
            'theme',
            __('Theme', 'chatbot-saas-widget'),
            array($this, 'theme_callback'),
            'chatbot-saas-widget',
            'chatbot_saas_appearance'
        );
        
        // Position Field
        add_settings_field(
            'position',
            __('Position', 'chatbot-saas-widget'),
            array($this, 'position_callback'),
            'chatbot-saas-widget',
            'chatbot_saas_appearance'
        );
        
        // Primary Color Field
        add_settings_field(
            'primary_color',
            __('Primary Color', 'chatbot-saas-widget'),
            array($this, 'primary_color_callback'),
            'chatbot-saas-widget',
            'chatbot_saas_appearance'
        );
        
        // Behavior Settings Section
        add_settings_section(
            'chatbot_saas_behavior',
            __('Behavior Settings', 'chatbot-saas-widget'),
            array($this, 'behavior_section_callback'),
            'chatbot-saas-widget'
        );
        
        // Enable Voice Field
        add_settings_field(
            'enable_voice',
            __('Enable Voice', 'chatbot-saas-widget'),
            array($this, 'enable_voice_callback'),
            'chatbot-saas-widget',
            'chatbot_saas_behavior'
        );
        
        // Auto Open Field
        add_settings_field(
            'auto_open',
            __('Auto Open', 'chatbot-saas-widget'),
            array($this, 'auto_open_callback'),
            'chatbot-saas-widget',
            'chatbot_saas_behavior'
        );
    }
    
    public function admin_enqueue_scripts($hook) {
        if ($hook !== 'settings_page_chatbot-saas-widget') {
            return;
        }
        
        wp_enqueue_script('wp-color-picker');
        wp_enqueue_style('wp-color-picker');
        
        wp_enqueue_script(
            'chatbot-saas-admin',
            CHATBOT_SAAS_PLUGIN_URL . 'assets/admin.js',
            array('jquery', 'wp-color-picker'),
            CHATBOT_SAAS_VERSION,
            true
        );
        
        wp_enqueue_style(
            'chatbot-saas-admin',
            CHATBOT_SAAS_PLUGIN_URL . 'assets/admin.css',
            array(),
            CHATBOT_SAAS_VERSION
        );
        
        wp_localize_script('chatbot-saas-admin', 'chatbot_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('chatbot_saas_nonce')
        ));
    }
    
    public function enqueue_scripts() {
        if (!$this->should_load_widget()) {
            return;
        }
        
        $chatbot_id = isset($this->options['chatbot_id']) ? $this->options['chatbot_id'] : '';
        $api_url = isset($this->options['api_url']) ? $this->options['api_url'] : 'https://api.yourchatbot.com';
        
        if (empty($chatbot_id)) {
            return;
        }
        
        // Enqueue widget script
        wp_enqueue_script(
            'chatbot-saas-widget',
            $api_url . '/widget/embed.js',
            array(),
            CHATBOT_SAAS_VERSION,
            true
        );
        
        // Add widget configuration
        $config = $this->get_widget_config();
        wp_add_inline_script('chatbot-saas-widget', 
            'window.chatbotSaaSConfig = ' . json_encode($config) . ';', 
            'before'
        );
    }
    
    public function render_widget() {
        if (!$this->should_load_widget()) {
            return;
        }
        
        $chatbot_id = isset($this->options['chatbot_id']) ? $this->options['chatbot_id'] : '';
        if (empty($chatbot_id)) {
            return;
        }
        
        $config = $this->get_widget_config();
        
        echo '<script>';
        echo 'if (typeof ChatbotSaaS !== "undefined") {';
        echo 'ChatbotSaaS.init(' . json_encode($config) . ');';
        echo '}';
        echo '</script>';
    }
    
    private function should_load_widget() {
        // Don't load on admin pages
        if (is_admin()) {
            return false;
        }
        
        // Check if widget is enabled
        $enabled = isset($this->options['enabled']) ? $this->options['enabled'] : true;
        if (!$enabled) {
            return false;
        }
        
        // Check page restrictions
        $restricted_pages = isset($this->options['restricted_pages']) ? $this->options['restricted_pages'] : array();
        if (!empty($restricted_pages) && is_page($restricted_pages)) {
            return false;
        }
        
        return true;
    }
    
    private function get_widget_config() {
        $defaults = array(
            'chatbotId' => '',
            'baseUrl' => 'https://api.yourchatbot.com',
            'theme' => 'light',
            'position' => 'bottom-right',
            'primaryColor' => '#3b82f6',
            'enableVoice' => false,
            'autoOpen' => false,
            'showAvatar' => true,
            'maxWidth' => 400,
            'maxHeight' => 600
        );
        
        $config = array_merge($defaults, array(
            'chatbotId' => isset($this->options['chatbot_id']) ? $this->options['chatbot_id'] : '',
            'baseUrl' => isset($this->options['api_url']) ? $this->options['api_url'] : $defaults['baseUrl'],
            'theme' => isset($this->options['theme']) ? $this->options['theme'] : $defaults['theme'],
            'position' => isset($this->options['position']) ? $this->options['position'] : $defaults['position'],
            'primaryColor' => isset($this->options['primary_color']) ? $this->options['primary_color'] : $defaults['primaryColor'],
            'enableVoice' => isset($this->options['enable_voice']) ? (bool)$this->options['enable_voice'] : $defaults['enableVoice'],
            'autoOpen' => isset($this->options['auto_open']) ? (bool)$this->options['auto_open'] : $defaults['autoOpen']
        ));
        
        return $config;
    }
    
    public function shortcode_handler($atts) {
        $atts = shortcode_atts(array(
            'id' => isset($this->options['chatbot_id']) ? $this->options['chatbot_id'] : '',
            'theme' => 'light',
            'position' => 'bottom-right',
            'color' => '#3b82f6'
        ), $atts, 'chatbot_widget');
        
        if (empty($atts['id'])) {
            return '<p>' . __('Chatbot ID is required.', 'chatbot-saas-widget') . '</p>';
        }
        
        $config = array(
            'chatbotId' => $atts['id'],
            'baseUrl' => isset($this->options['api_url']) ? $this->options['api_url'] : 'https://api.yourchatbot.com',
            'theme' => $atts['theme'],
            'position' => $atts['position'],
            'primaryColor' => $atts['color']
        );
        
        $script_id = 'chatbot-widget-' . uniqid();
        
        ob_start();
        ?>
        <div id="<?php echo esc_attr($script_id); ?>"></div>
        <script>
        (function() {
            if (typeof ChatbotSaaS !== 'undefined') {
                ChatbotSaaS.init(<?php echo json_encode($config); ?>);
            } else {
                console.warn('Chatbot SaaS widget script not loaded');
            }
        })();
        </script>
        <?php
        return ob_get_clean();
    }
    
    public function register_gutenberg_block() {
        if (!function_exists('register_block_type')) {
            return;
        }
        
        wp_register_script(
            'chatbot-saas-block',
            CHATBOT_SAAS_PLUGIN_URL . 'assets/block.js',
            array('wp-blocks', 'wp-element', 'wp-editor'),
            CHATBOT_SAAS_VERSION
        );
        
        register_block_type('chatbot-saas/widget', array(
            'editor_script' => 'chatbot-saas-block',
            'render_callback' => array($this, 'render_gutenberg_block')
        ));
    }
    
    public function render_gutenberg_block($attributes) {
        return $this->shortcode_handler($attributes);
    }
    
    public function admin_page() {
        ?>
        <div class="wrap">
            <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
            
            <div class="chatbot-saas-admin-header">
                <h2><?php _e('Configure your AI chatbot widget', 'chatbot-saas-widget'); ?></h2>
                <p><?php _e('Add an intelligent chatbot to your WordPress site with voice support and advanced customization options.', 'chatbot-saas-widget'); ?></p>
            </div>
            
            <form method="post" action="options.php">
                <?php
                settings_fields('chatbot_saas_group');
                do_settings_sections('chatbot-saas-widget');
                submit_button();
                ?>
            </form>
            
            <div class="chatbot-saas-admin-sidebar">
                <div class="postbox">
                    <h3 class="hndle"><?php _e('Quick Actions', 'chatbot-saas-widget'); ?></h3>
                    <div class="inside">
                        <p>
                            <button type="button" id="test-connection" class="button button-secondary">
                                <?php _e('Test Connection', 'chatbot-saas-widget'); ?>
                            </button>
                        </p>
                        <p>
                            <a href="https://yourchatbot.com/dashboard" target="_blank" class="button button-primary">
                                <?php _e('Manage Chatbots', 'chatbot-saas-widget'); ?>
                            </a>
                        </p>
                    </div>
                </div>
                
                <div class="postbox">
                    <h3 class="hndle"><?php _e('Support', 'chatbot-saas-widget'); ?></h3>
                    <div class="inside">
                        <p><?php _e('Need help? Check out our documentation or contact support.', 'chatbot-saas-widget'); ?></p>
                        <p>
                            <a href="https://docs.yourchatbot.com" target="_blank">
                                <?php _e('Documentation', 'chatbot-saas-widget'); ?>
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
        <?php
    }
    
    // Settings field callbacks
    public function general_section_callback() {
        echo '<p>' . __('Configure the basic settings for your chatbot widget.', 'chatbot-saas-widget') . '</p>';
    }
    
    public function chatbot_id_callback() {
        $value = isset($this->options['chatbot_id']) ? $this->options['chatbot_id'] : '';
        echo '<input type="text" id="chatbot_id" name="chatbot_saas_options[chatbot_id]" value="' . esc_attr($value) . '" class="regular-text" />';
        echo '<p class="description">' . __('Enter your chatbot ID from the dashboard.', 'chatbot-saas-widget') . '</p>';
    }
    
    public function api_url_callback() {
        $value = isset($this->options['api_url']) ? $this->options['api_url'] : 'https://api.yourchatbot.com';
        echo '<input type="url" id="api_url" name="chatbot_saas_options[api_url]" value="' . esc_attr($value) . '" class="regular-text" />';
        echo '<p class="description">' . __('API URL for your chatbot service.', 'chatbot-saas-widget') . '</p>';
    }
    
    public function appearance_section_callback() {
        echo '<p>' . __('Customize the appearance of your chatbot widget.', 'chatbot-saas-widget') . '</p>';
    }
    
    public function theme_callback() {
        $value = isset($this->options['theme']) ? $this->options['theme'] : 'light';
        $options = array(
            'light' => __('Light', 'chatbot-saas-widget'),
            'dark' => __('Dark', 'chatbot-saas-widget'),
            'auto' => __('Auto', 'chatbot-saas-widget')
        );
        
        echo '<select id="theme" name="chatbot_saas_options[theme]">';
        foreach ($options as $key => $label) {
            echo '<option value="' . esc_attr($key) . '"' . selected($value, $key, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select>';
    }
    
    public function position_callback() {
        $value = isset($this->options['position']) ? $this->options['position'] : 'bottom-right';
        $options = array(
            'bottom-right' => __('Bottom Right', 'chatbot-saas-widget'),
            'bottom-left' => __('Bottom Left', 'chatbot-saas-widget'),
            'top-right' => __('Top Right', 'chatbot-saas-widget'),
            'top-left' => __('Top Left', 'chatbot-saas-widget')
        );
        
        echo '<select id="position" name="chatbot_saas_options[position]">';
        foreach ($options as $key => $label) {
            echo '<option value="' . esc_attr($key) . '"' . selected($value, $key, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select>';
    }
    
    public function primary_color_callback() {
        $value = isset($this->options['primary_color']) ? $this->options['primary_color'] : '#3b82f6';
        echo '<input type="text" id="primary_color" name="chatbot_saas_options[primary_color]" value="' . esc_attr($value) . '" class="color-picker" />';
    }
    
    public function behavior_section_callback() {
        echo '<p>' . __('Configure how your chatbot behaves.', 'chatbot-saas-widget') . '</p>';
    }
    
    public function enable_voice_callback() {
        $value = isset($this->options['enable_voice']) ? $this->options['enable_voice'] : false;
        echo '<input type="checkbox" id="enable_voice" name="chatbot_saas_options[enable_voice]" value="1"' . checked($value, true, false) . ' />';
        echo '<label for="enable_voice">' . __('Enable voice chat functionality', 'chatbot-saas-widget') . '</label>';
    }
    
    public function auto_open_callback() {
        $value = isset($this->options['auto_open']) ? $this->options['auto_open'] : false;
        echo '<input type="checkbox" id="auto_open" name="chatbot_saas_options[auto_open]" value="1"' . checked($value, true, false) . ' />';
        echo '<label for="auto_open">' . __('Automatically open widget on page load', 'chatbot-saas-widget') . '</label>';
    }
    
    public function sanitize_options($input) {
        $sanitized = array();
        
        if (isset($input['chatbot_id'])) {
            $sanitized['chatbot_id'] = sanitize_text_field($input['chatbot_id']);
        }
        
        if (isset($input['api_url'])) {
            $sanitized['api_url'] = esc_url_raw($input['api_url']);
        }
        
        if (isset($input['theme'])) {
            $allowed_themes = array('light', 'dark', 'auto');
            $sanitized['theme'] = in_array($input['theme'], $allowed_themes) ? $input['theme'] : 'light';
        }
        
        if (isset($input['position'])) {
            $allowed_positions = array('bottom-right', 'bottom-left', 'top-right', 'top-left');
            $sanitized['position'] = in_array($input['position'], $allowed_positions) ? $input['position'] : 'bottom-right';
        }
        
        if (isset($input['primary_color'])) {
            $sanitized['primary_color'] = sanitize_hex_color($input['primary_color']);
        }
        
        if (isset($input['enable_voice'])) {
            $sanitized['enable_voice'] = (bool)$input['enable_voice'];
        }
        
        if (isset($input['auto_open'])) {
            $sanitized['auto_open'] = (bool)$input['auto_open'];
        }
        
        return $sanitized;
    }
    
    public function test_connection() {
        check_ajax_referer('chatbot_saas_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Insufficient permissions', 'chatbot-saas-widget'));
        }
        
        $chatbot_id = sanitize_text_field($_POST['chatbot_id']);
        $api_url = esc_url_raw($_POST['api_url']);
        
        if (empty($chatbot_id) || empty($api_url)) {
            wp_send_json_error(__('Chatbot ID and API URL are required.', 'chatbot-saas-widget'));
        }
        
        // Test API connection
        $test_url = rtrim($api_url, '/') . '/api/v1/widgets/public/' . $chatbot_id . '/config';
        $response = wp_remote_get($test_url, array('timeout' => 10));
        
        if (is_wp_error($response)) {
            wp_send_json_error(__('Connection failed: ', 'chatbot-saas-widget') . $response->get_error_message());
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code === 200) {
            wp_send_json_success(__('Connection successful!', 'chatbot-saas-widget'));
        } else {
            wp_send_json_error(__('Connection failed with status: ', 'chatbot-saas-widget') . $status_code);
        }
    }
}

// Initialize the plugin
new ChatbotSaaSWidget();

// Activation hook
register_activation_hook(__FILE__, function() {
    // Set default options
    $default_options = array(
        'api_url' => 'https://api.yourchatbot.com',
        'theme' => 'light',
        'position' => 'bottom-right',
        'primary_color' => '#3b82f6',
        'enable_voice' => false,
        'auto_open' => false
    );
    
    add_option('chatbot_saas_options', $default_options);
});

// Deactivation hook
register_deactivation_hook(__FILE__, function() {
    // Clean up if needed
});

// Uninstall hook
register_uninstall_hook(__FILE__, function() {
    // Remove options
    delete_option('chatbot_saas_options');
});
?>
