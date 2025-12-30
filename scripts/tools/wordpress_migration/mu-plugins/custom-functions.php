<?php
/**
 * arong.eu.org 自定义功能
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
 * 1. 自定义存档页面标题
 * 移除 "Category: " "Author: " 等前缀
 */
add_filter('get_the_archive_title', function($title) {
    if (is_category()) {
        $title = single_cat_title('', false);
    } elseif (is_author()) {
        $title = get_the_author();
    } elseif (is_tag()) {
        $title = single_tag_title('', false);
    } elseif (is_post_type_archive()) {
        $title = post_type_archive_title('', false);
    }
    return $title;
});

/**
 * 2. 自定义Meta Description
 * 注意: 如果安装了Rank Math或Yoast SEO,此功能会被覆盖(优先级更高)
 */
function arong_custom_meta_description() {
    // 检查是否已有SEO插件
    if (defined('RANK_MATH_VERSION') || defined('WPSEO_VERSION')) {
        return; // SEO插件会处理
    }

    $description = '';

    if (is_front_page()) {
        $description = '阿嵘的云生活 - 分享VPS配置、开源应用、AI技术、量化交易等云端生活经验。面向普通人的技术实践指南。';
    } elseif (is_single()) {
        global $post;
        $excerpt = wp_strip_all_tags(get_the_excerpt($post));
        if ($excerpt) {
            $description = mb_substr($excerpt, 0, 160);
        }
    } elseif (is_category()) {
        $cat_desc = category_description();
        if ($cat_desc) {
            $description = wp_strip_all_tags($cat_desc);
        } else {
            $description = '阿嵘的云生活 - ' . single_cat_title('', false) . '相关文章';
        }
    } elseif (is_author()) {
        $author_desc = get_the_author_meta('description');
        if ($author_desc) {
            $description = wp_strip_all_tags($author_desc);
        } else {
            $description = get_the_author() . '在阿嵘的云生活发表的文章';
        }
    }

    if ($description) {
        echo '<meta name="description" content="' . esc_attr($description) . '">' . "\n";
    }
}
add_action('wp_head', 'arong_custom_meta_description', 1);

/**
 * 3. 添加基本的Open Graph标签
 * 注意: SEO插件会提供更完善的OG标签
 */
function arong_add_og_tags() {
    // 检查是否已有SEO插件
    if (defined('RANK_MATH_VERSION') || defined('WPSEO_VERSION')) {
        return;
    }

    global $post;

    echo '<meta property="og:site_name" content="' . get_bloginfo('name') . '">' . "\n";
    echo '<meta property="og:locale" content="zh_CN">' . "\n";

    if (is_single()) {
        echo '<meta property="og:type" content="article">' . "\n";
        echo '<meta property="og:title" content="' . esc_attr(get_the_title()) . '">' . "\n";
        echo '<meta property="og:url" content="' . get_permalink() . '">' . "\n";

        // 获取文章特色图片
        if (has_post_thumbnail()) {
            $thumbnail = wp_get_attachment_image_src(get_post_thumbnail_id($post->ID), 'large');
            echo '<meta property="og:image" content="' . esc_url($thumbnail[0]) . '">' . "\n";
        }

        // 文章摘要
        $excerpt = wp_strip_all_tags(get_the_excerpt());
        if ($excerpt) {
            echo '<meta property="og:description" content="' . esc_attr(mb_substr($excerpt, 0, 200)) . '">' . "\n";
        }

        // 文章发布时间
        echo '<meta property="article:published_time" content="' . get_the_date('c') . '">' . "\n";
        echo '<meta property="article:modified_time" content="' . get_the_modified_date('c') . '">' . "\n";
    } else {
        echo '<meta property="og:type" content="website">' . "\n";
        echo '<meta property="og:title" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
        echo '<meta property="og:url" content="' . home_url() . '">' . "\n";
    }
}
add_action('wp_head', 'arong_add_og_tags', 5);

/**
 * 4. 启用图片懒加载
 * WordPress 5.5+ 默认支持,此处确保启用
 */
add_filter('wp_lazy_loading_enabled', '__return_true');

/**
 * 5. 优化页脚Logo和图片显示
 */
function arong_footer_image_styles() {
    echo '<style>
        .site-footer img {
            max-width: 100%;
            height: auto;
            display: block;
        }
        .site-footer .wp-block-image {
            margin-bottom: 1rem;
        }
    </style>' . "\n";
}
add_action('wp_head', 'arong_footer_image_styles');

/**
 * 6. 面包屑导航
 * 可以在主题模板中调用: arong_breadcrumbs()
 */
function arong_breadcrumbs() {
    if (is_front_page()) {
        return;
    }

    $separator = ' » ';
    $home_title = '首页';

    echo '<nav class="breadcrumbs" aria-label="面包屑导航">';
    echo '<a href="' . home_url() . '">' . $home_title . '</a>' . $separator;

    if (is_category() || is_single()) {
        $categories = get_the_category();
        if ($categories) {
            $category = $categories[0];
            echo '<a href="' . get_category_link($category->term_id) . '">' . $category->name . '</a>';
            if (is_single()) {
                echo $separator . '<span class="current">' . get_the_title() . '</span>';
            }
        }
    } elseif (is_page()) {
        echo '<span class="current">' . get_the_title() . '</span>';
    } elseif (is_author()) {
        echo '<span class="current">作者: ' . get_the_author() . '</span>';
    } elseif (is_tag()) {
        echo '<span class="current">标签: ' . single_tag_title('', false) . '</span>';
    } elseif (is_archive()) {
        echo '<span class="current">' . get_the_archive_title() . '</span>';
    } elseif (is_search()) {
        echo '<span class="current">搜索结果: ' . get_search_query() . '</span>';
    } elseif (is_404()) {
        echo '<span class="current">页面未找到</span>';
    }

    echo '</nav>';
}

/**
 * 7. 为文章添加预计阅读时间
 */
function arong_reading_time() {
    global $post;

    $content = get_post_field('post_content', $post->ID);
    $word_count = mb_strlen(strip_tags($content), 'UTF-8');
    $reading_time = ceil($word_count / 400); // 假设每分钟阅读400字

    if ($reading_time < 1) {
        $reading_time = 1;
    }

    return $reading_time . ' 分钟阅读';
}

/**
 * 8. 在文章内容中自动添加目录(针对长文章)
 */
function arong_auto_table_of_contents($content) {
    // 只在单篇文章页面生效
    if (!is_single()) {
        return $content;
    }

    // 检测文章中的标题数量
    $headings_count = preg_match_all('/<h([2-3])>(.*?)<\/h\1>/', $content, $matches);

    // 如果标题少于3个,不生成目录
    if ($headings_count < 3) {
        return $content;
    }

    $toc = '<div class="table-of-contents">';
    $toc .= '<h2>目录</h2>';
    $toc .= '<ul>';

    foreach ($matches[2] as $index => $heading) {
        $anchor = 'heading-' . $index;
        $level = $matches[1][$index];

        // 在内容中添加锚点
        $content = preg_replace(
            '/<h' . $level . '>' . preg_quote($heading, '/') . '<\/h' . $level . '>/',
            '<h' . $level . ' id="' . $anchor . '">' . $heading . '</h' . $level . '>',
            $content,
            1
        );

        // 添加到目录
        $class = $level == 3 ? ' class="sub-heading"' : '';
        $toc .= '<li' . $class . '><a href="#' . $anchor . '">' . strip_tags($heading) . '</a></li>';
    }

    $toc .= '</ul>';
    $toc .= '</div>';

    // 在第一个段落后插入目录
    $content = preg_replace('/(<p>.*?<\/p>)/', '$1' . $toc, $content, 1);

    return $content;
}
// 取消注释以启用自动目录功能
// add_filter('the_content', 'arong_auto_table_of_contents');

/**
 * 9. 优化摘要长度和格式
 */
function arong_custom_excerpt_length($length) {
    return 100; // 100个字符
}
add_filter('excerpt_length', 'arong_custom_excerpt_length');

function arong_custom_excerpt_more($more) {
    return '...';
}
add_filter('excerpt_more', 'arong_custom_excerpt_more');

// 记录激活
add_action('init', function() {
    if (!get_option('arong_functions_activated')) {
        update_option('arong_functions_activated', current_time('mysql'));
        error_log('[arong.eu.org] Custom functions activated at ' . current_time('mysql'));
    }
}, 11);
