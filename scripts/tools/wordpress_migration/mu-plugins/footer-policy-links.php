<?php
/**
 * Plugin Name: Footer Policy Links
 * Description: Adds Privacy Policy and Terms of Service links to the footer
 * Version: 1.0
 */

// Add policy links to footer
add_action("wp_footer", "add_footer_policy_links", 100);

function add_footer_policy_links() {
    ?>
    <style>
        .footer-policy-links {
            text-align: center;
            padding: 20px 0;
            border-top: 1px solid #e5e7eb;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
        .footer-policy-links a {
            color: #666;
            text-decoration: none;
            margin: 0 15px;
        }
        .footer-policy-links a:hover {
            color: #333;
            text-decoration: underline;
        }
        .footer-policy-links .separator {
            color: #ccc;
        }
    </style>
    <div class="footer-policy-links">
        <a href="/privacy-policy/">隐私政策</a>
        <span class="separator">|</span>
        <a href="/terms-of-service/">服务条款</a>
        <span class="separator">|</span>
        <span>© <?php echo date("Y"); ?> arong.eu.org</span>
    </div>
    <?php
}
