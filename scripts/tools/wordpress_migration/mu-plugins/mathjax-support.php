<?php
/**
 * Plugin Name: MathJax Support
 * Description: Adds MathJax support for LaTeX math formulas in posts
 * Version: 1.0
 * Author: YouXin Workshop
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Enqueue MathJax script on frontend
 */
function youxin_enqueue_mathjax() {
    // Only load on single posts and pages
    if (is_singular()) {
        // Check if post content contains LaTeX patterns
        global $post;
        if ($post && (
            strpos($post->post_content, '$$') !== false ||
            strpos($post->post_content, '\\(') !== false ||
            strpos($post->post_content, '\\[') !== false ||
            preg_match('/\$[^$]+\$/', $post->post_content)
        )) {
            // Add MathJax configuration
            add_action('wp_head', 'youxin_mathjax_config', 5);

            // Enqueue MathJax from CDN
            wp_enqueue_script(
                'mathjax',
                'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js',
                array(),
                '3.0',
                false // Load in header for proper rendering
            );

            // Add async attribute
            add_filter('script_loader_tag', 'youxin_mathjax_async', 10, 2);
        }
    }
}
add_action('wp_enqueue_scripts', 'youxin_enqueue_mathjax');

/**
 * Add MathJax configuration to head
 */
function youxin_mathjax_config() {
    ?>
    <script>
    window.MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']],
            processEscapes: true
        },
        options: {
            skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
        }
    };
    </script>
    <?php
}

/**
 * Add async attribute to MathJax script
 */
function youxin_mathjax_async($tag, $handle) {
    if ('mathjax' === $handle) {
        return str_replace(' src', ' async src', $tag);
    }
    return $tag;
}

/**
 * Add custom CSS for math formulas and content styling
 */
function youxin_math_styles() {
    if (is_singular()) {
        ?>
        <style>
        /* MathJax formula styling */
        .MathJax {
            font-size: 1.1em !important;
        }

        /* Buy me a coffee button - smaller size */
        img[alt="Buy Me A Coffee"] {
            height: 40px !important;
            width: auto !important;
            max-width: 150px !important;
        }

        /* Comment section styling */
        .comment-reply-title,
        #reply-title {
            font-size: 1.2em !important;
        }

        /* ASCII art / preformatted text blocks */
        .ascii-art-container {
            overflow-x: auto;
            margin: 1.5em 0;
        }

        .ascii-art-container pre {
            font-family: 'Sarasa Mono SC', 'Noto Sans Mono CJK SC', 'Source Han Mono SC',
                         'Microsoft YaHei Mono', 'Courier New', monospace !important;
            font-size: 13px !important;
            line-height: 1.4 !important;
            white-space: pre !important;
        }

        /* Table styling */
        .wp-block-table table {
            border-collapse: collapse;
            width: 100%;
        }

        .wp-block-table th,
        .wp-block-table td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: center;
        }

        .wp-block-table th {
            background-color: #f5f5f5;
            font-weight: 600;
        }

        /* Blockquote styling - reduce font size */
        .wp-block-quote,
        blockquote {
            font-size: 1em !important;
            line-height: 1.6 !important;
            padding: 1em 1.5em !important;
            margin: 1.5em 0 !important;
            border-left: 4px solid #0073aa !important;
            background: #f9f9f9 !important;
        }

        .wp-block-quote p,
        blockquote p {
            font-size: 1em !important;
            margin-bottom: 0.5em !important;
        }
        </style>
        <?php
    }
}
add_action('wp_head', 'youxin_math_styles');
