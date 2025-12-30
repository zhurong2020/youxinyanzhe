/**
 * WordPress Pagination Scroll Fix
 *
 * When navigating to paginated pages (/page/2/, /page/3/, etc.),
 * automatically scrolls to the posts list section instead of page top.
 *
 * Deploy to: /var/www/html/wp-content/themes/[your-theme]/assets/js/
 * Or enqueue via functions.php or WPCode plugin
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        // Check if current page is a paginated page
        const isPaginatedPage = window.location.pathname.match(/\/page\/\d+\/?$/);

        if (!isPaginatedPage) {
            return; // Not a paginated page, do nothing
        }

        // Find the posts list container (try multiple selectors)
        const postsSection =
            document.querySelector('.wp-block-post-template') ||
            document.querySelector('.wp-block-query') ||
            document.querySelector('[class*="posts-list"]') ||
            document.querySelector('#posts-section') ||
            document.querySelector('main ul.is-flex-container');

        if (!postsSection) {
            console.log('Pagination scroll fix: Posts section not found');
            return;
        }

        // Calculate scroll position with offset for fixed headers
        const headerOffset = 80; // Adjust based on your header height
        const elementPosition = postsSection.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        // Smooth scroll to posts section
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });

        console.log('Pagination scroll fix: Scrolled to posts section');
    });
})();
