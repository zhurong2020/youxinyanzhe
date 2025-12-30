<?php
/**
 * WordPress安全增强 (简化版)
 *
 * 使用方法:
 * 复制到 /var/www/zhurong.link/public_html/wp-content/mu-plugins/
 *
 * @package arong.eu.org
 * @since 1.0.0
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

/**
 * 1. 移除WordPress版本号
 * 防止暴露版本信息给潜在攻击者
 */
remove_action('wp_head', 'wp_generator');

// 移除RSS中的版本号
add_filter('the_generator', '__return_empty_string');

/**
 * 2. 禁用详细登录错误提示
 * 防止暴力破解时获取用户名信息
 */
add_filter('login_errors', function() {
    return '登录信息有误,请检查用户名和密码后重试。';
});

/**
 * 3. 禁用文件编辑器
 * 防止后台被入侵后直接修改主题/插件文件
 */
if (!defined('DISALLOW_FILE_EDIT')) {
    define('DISALLOW_FILE_EDIT', true);
}

/**
 * 4. 添加安全响应头
 */
function arong_add_security_headers() {
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: SAMEORIGIN');
    header('X-XSS-Protection: 1; mode=block');
    header('Referrer-Policy: strict-origin-when-cross-origin');
}
add_action('send_headers', 'arong_add_security_headers');

// 记录激活时间
add_action('init', function() {
    if (!get_option('arong_security_activated')) {
        update_option('arong_security_activated', current_time('mysql'));
        error_log('[arong.eu.org] Security enhancements (simple) activated at ' . current_time('mysql'));
    }
}, 1);
