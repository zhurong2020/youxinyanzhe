#!/bin/bash
# Deploy pagination scroll fix to WordPress site
# Usage: ./deploy_pagination_fix.sh

set -e

# Configuration
VPS_HOST="arong-vps"
WP_PATH="/var/www/arong.eu.org/public_html"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JS_FILE="pagination_scroll_fix.js"

echo "=== WordPress Pagination Scroll Fix Deployment ==="
echo ""

# Method 1: Add inline script via wp-config (recommended for simplicity)
echo "Deploying pagination scroll fix..."

# Create a PHP snippet that will enqueue our script
SNIPPET_CONTENT='<?php
/**
 * Pagination Scroll Fix
 * Automatically scrolls to posts list on paginated pages
 */
add_action("wp_footer", function() {
?>
<script>
(function() {
    "use strict";
    document.addEventListener("DOMContentLoaded", function() {
        if (!window.location.pathname.match(/\/page\/\d+\/?$/)) return;
        var postsSection = document.querySelector(".wp-block-post-template") ||
            document.querySelector(".wp-block-query") ||
            document.querySelector("main ul.is-flex-container");
        if (!postsSection) return;
        var headerOffset = 80;
        var offsetPosition = postsSection.getBoundingClientRect().top + window.pageYOffset - headerOffset;
        window.scrollTo({ top: offsetPosition, behavior: "smooth" });
    });
})();
</script>
<?php
}, 99);'

# Save the snippet locally first
echo "$SNIPPET_CONTENT" > "$SCRIPT_DIR/pagination-scroll-fix.php"

# Upload to WordPress mu-plugins directory (auto-loaded)
echo "Uploading to VPS..."
ssh "$VPS_HOST" "sudo mkdir -p $WP_PATH/wp-content/mu-plugins"
scp "$SCRIPT_DIR/pagination-scroll-fix.php" "$VPS_HOST:/tmp/"
ssh "$VPS_HOST" "sudo mv /tmp/pagination-scroll-fix.php $WP_PATH/wp-content/mu-plugins/ && sudo chown www-data:www-data $WP_PATH/wp-content/mu-plugins/pagination-scroll-fix.php"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "The pagination scroll fix has been deployed to:"
echo "  $WP_PATH/wp-content/mu-plugins/pagination-scroll-fix.php"
echo ""
echo "This is a 'must-use' plugin that loads automatically."
echo ""
echo "Test by visiting: https://www.arong.eu.org/page/2/"
echo "The page should now auto-scroll to the posts list section."
echo ""
echo "To remove: ssh $VPS_HOST 'sudo rm $WP_PATH/wp-content/mu-plugins/pagination-scroll-fix.php'"
