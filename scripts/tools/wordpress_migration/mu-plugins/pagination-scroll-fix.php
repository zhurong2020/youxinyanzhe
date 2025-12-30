<?php
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
}, 99);
