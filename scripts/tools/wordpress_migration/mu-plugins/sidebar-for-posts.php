<?php
/**
 * Plugin Name: Sidebar for Single Posts
 * Description: Adds a sidebar only to single post pages
 * Version: 1.1
 */

add_filter("the_content", "add_post_sidebar", 100);

function add_post_sidebar($content) {
    if (!is_single() || is_admin()) {
        return $content;
    }
    
    $popular_posts = get_posts(array(
        "numberposts" => 5,
        "orderby" => "date",
        "order" => "DESC",
        "post__not_in" => array(get_the_ID())
    ));
    
    $categories = get_categories(array(
        "orderby" => "count",
        "order" => "DESC",
        "number" => 6,
        "hide_empty" => true
    ));
    
    $sidebar_css = "
    <style>
    .post-with-sidebar-wrapper {
        display: flex;
        gap: 40px;
        max-width: 1200px;
        margin: 20px auto;
    }
    .post-main-content {
        flex: 1;
        min-width: 0;
    }
    .post-sidebar {
        width: 280px;
        flex-shrink: 0;
    }
    .post-sidebar-inner {
        position: sticky;
        top: 100px;
        padding: 20px;
        background: #f8fafc;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    .post-sidebar h4 {
        font-size: 15px;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #3b82f6;
    }
    .post-sidebar ul {
        list-style: none;
        padding: 0;
        margin: 0 0 20px 0;
    }
    .post-sidebar li {
        padding: 8px 0;
        border-bottom: 1px solid #e2e8f0;
    }
    .post-sidebar li:last-child {
        border-bottom: none;
    }
    .post-sidebar a {
        color: #475569;
        text-decoration: none;
        font-size: 13px;
        line-height: 1.5;
        display: block;
    }
    .post-sidebar a:hover {
        color: #3b82f6;
    }
    .post-sidebar .cat-count {
        color: #94a3b8;
        font-size: 12px;
    }
    @media (max-width: 900px) {
        .post-with-sidebar-wrapper {
            flex-direction: column;
        }
        .post-sidebar {
            width: 100%;
            margin-top: 30px;
        }
        .post-sidebar-inner {
            position: static;
        }
    }
    </style>
    ";
    
    $sidebar_html = "<div class=\"post-sidebar\"><div class=\"post-sidebar-inner\">";
    
    if (!empty($popular_posts)) {
        $sidebar_html .= "<h4>📚 最新文章</h4><ul>";
        foreach ($popular_posts as $post) {
            $sidebar_html .= "<li><a href=\"" . get_permalink($post->ID) . "\">" . esc_html($post->post_title) . "</a></li>";
        }
        $sidebar_html .= "</ul>";
    }
    
    if (!empty($categories)) {
        $sidebar_html .= "<h4>📂 文章分类</h4><ul>";
        foreach ($categories as $cat) {
            $sidebar_html .= "<li><a href=\"" . get_category_link($cat->term_id) . "\">" . esc_html($cat->name) . " <span class=\"cat-count\">(" . $cat->count . ")</span></a></li>";
        }
        $sidebar_html .= "</ul>";
    }
    
    $sidebar_html .= "</div></div>";
    
    $wrapped = $sidebar_css;
    $wrapped .= "<div class=\"post-with-sidebar-wrapper\">";
    $wrapped .= "<div class=\"post-main-content\">" . $content . "</div>";
    $wrapped .= $sidebar_html;
    $wrapped .= "</div>";
    
    return $wrapped;
}
