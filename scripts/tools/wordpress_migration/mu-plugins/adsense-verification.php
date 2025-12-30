<?php
/**
 * Plugin Name: Google AdSense Verification
 * Description: Adds Google AdSense verification code to the site header
 * Version: 1.0
 */

// Add AdSense code to <head>
add_action("wp_head", "add_adsense_code", 1);

function add_adsense_code() {
    echo "\n<!-- Google AdSense -->\n";
    echo "<script async src=\"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3677908378517538\" crossorigin=\"anonymous\"></script>\n";
    echo "<!-- End Google AdSense -->\n";
}
