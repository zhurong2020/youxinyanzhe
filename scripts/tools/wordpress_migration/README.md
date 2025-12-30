# WordPress Migration Tools

Tools for migrating Jekyll and Gridea content to WordPress (arong.eu.org).

## IMPORTANT: Backup First!

**Before any migration, create a full WordPress backup!**

### Option 1: Use the backup script (recommended)

```bash
# Copy and run on VPS
scp scripts/tools/wordpress_migration/wp_backup.sh arong-vps:~/
ssh arong-vps 'bash ~/wp_backup.sh'

# Download backup locally
scp arong-vps:/home/backup/wp_backup_* /path/to/local/backup/
```

### Option 2: Use UpdraftPlus plugin

1. Login to WordPress admin
2. Go to Settings → UpdraftPlus Backups
3. Click "Backup Now"
4. Download both files and database backups

### Option 3: Manual backup

```bash
# On VPS
cd /var/www/arong.eu.org/public_html

# Backup files
sudo tar -czf ~/wp_files_backup.tar.gz .

# Backup database (get credentials from wp-config.php)
mysqldump -u [user] -p [database] > ~/wp_db_backup.sql
```

---

## Prerequisites

### Install Dependencies

```bash
cd /home/wuxia/projects/workshop
source venv/bin/activate
pip install requests python-frontmatter markdown beautifulsoup4 html2text
```

### Configure WordPress Credentials

Create a WordPress Application Password:
1. Log in to WordPress admin
2. Go to Users → Profile
3. Scroll to "Application Passwords"
4. Create a new password for "Migration Script"

Set environment variables:
```bash
export WP_URL="https://arong.eu.org"
export WP_USER="your_username"
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

Or create `.env` file:
```
WP_URL=https://arong.eu.org
WP_USER=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

## Scripts

### 1. Jekyll to WordPress (`jekyll_to_wp.py`)

Migrate Jekyll markdown posts with full front matter support.

**Dry Run (Preview):**
```bash
python jekyll_to_wp.py --source _posts/ --dry-run
```

**Migrate First 5 Posts (Test):**
```bash
python jekyll_to_wp.py --source _posts/ --limit 5
```

**Full Migration:**
```bash
python jekyll_to_wp.py --source _posts/ --batch-size 10
```

**Features:**
- Parses YAML front matter
- Maps categories and tags
- Handles VIP member_tier field (via ACF)
- Preserves OneDrive image URLs
- Converts Markdown to HTML
- Cleans Liquid/Jekyll template syntax ({% assign %}, {% for %}, etc.)
- Protects LaTeX math formulas during conversion
- Handles Kramdown link attributes ({:target="_blank"})

### 2. Gridea HTML to WordPress (`gridea_html_to_wp.py`)

Migrate Gridea static HTML posts back to WordPress.

**Dry Run:**
```bash
python gridea_html_to_wp.py \
  --source /home/wuxia/projects/zhurong2020.github.io/post/ \
  --dry-run
```

**Migrate with Limit:**
```bash
python gridea_html_to_wp.py \
  --source /home/wuxia/projects/zhurong2020.github.io/post/ \
  --limit 10
```

**Features:**
- Extracts content from HTML
- Converts HTML back to Markdown (for editing)
- Preserves metadata (title, date, tags)
- Handles image URLs

### 3. Generate Redirects (`generate_redirects.py`)

Generate 301 redirect rules for multiple formats.

**From Jekyll Posts:**
```bash
python generate_redirects.py --jekyll-posts _posts/ --output redirects/
```

**From Gridea Posts:**
```bash
python generate_redirects.py \
  --gridea-posts /home/wuxia/projects/zhurong2020.github.io/post/ \
  --output redirects/
```

**From Both + Migration Results:**
```bash
python generate_redirects.py \
  --jekyll-posts _posts/ \
  --gridea-posts /home/wuxia/projects/zhurong2020.github.io/post/ \
  --migration-results migration_results.json \
  --output redirects/
```

**Generated Files:**
- `yoast_redirects.csv` - For Yoast SEO plugin
- `redirection_plugin.csv` - For Redirection plugin
- `redirection_plugin.json` - JSON format
- `nginx_redirects.conf` - Nginx rewrite rules
- `htaccess_redirects.txt` - Apache .htaccess rules
- `jekyll_redirect_instructions.md` - Jekyll redirect-from guide

### 4. Pagination Scroll Fix (`deploy_pagination_fix.sh`)

Fix WordPress pagination jump to page top issue. After deployment, paginated pages (`/page/2/`, `/page/3/`, etc.) will auto-scroll to the posts list section.

**Deploy:**
```bash
./deploy_pagination_fix.sh
```

**How it works:**
- Deploys a mu-plugin to WordPress
- Detects paginated URLs (`/page/N/`)
- Auto-scrolls to `.wp-block-post-template` container
- Smooth scroll animation with 80px header offset

**Remove:**
```bash
ssh arong-vps 'sudo rm /var/www/arong.eu.org/public_html/wp-content/mu-plugins/pagination-scroll-fix.php'
```

## Migration Workflow

### Phase 1: Workshop Content (33 posts)

```bash
cd /home/wuxia/projects/workshop
source venv/bin/activate

# 1. Dry run to verify
python scripts/tools/wordpress_migration/jekyll_to_wp.py \
  --source _posts/ --dry-run

# 2. Test with 5 posts
python scripts/tools/wordpress_migration/jekyll_to_wp.py \
  --source _posts/ --limit 5

# 3. Full migration
python scripts/tools/wordpress_migration/jekyll_to_wp.py \
  --source _posts/
```

### Phase 2: Gridea Content (81 posts)

```bash
# 1. Dry run
python scripts/tools/wordpress_migration/gridea_html_to_wp.py \
  --source /home/wuxia/projects/zhurong2020.github.io/post/ \
  --dry-run

# 2. Migrate
python scripts/tools/wordpress_migration/gridea_html_to_wp.py \
  --source /home/wuxia/projects/zhurong2020.github.io/post/
```

### Phase 3: Setup Redirects

```bash
# Generate redirect rules
python scripts/tools/wordpress_migration/generate_redirects.py \
  --jekyll-posts _posts/ \
  --gridea-posts /home/wuxia/projects/zhurong2020.github.io/post/ \
  --migration-results migration_results.json \
  --output redirects/

# Import into WordPress
# Option 1: Yoast SEO → Redirects → Import CSV
# Option 2: Redirection plugin → Import → JSON
```

## Output Files

After migration, the following files are generated:

- `migration.log` - Detailed migration log
- `migration_results.json` - Jekyll migration results
- `gridea_migration.log` - Gridea migration log
- `gridea_migration_results.json` - Gridea migration results
- `redirects/` - Directory with all redirect formats

## Troubleshooting

### Common Issues

**401 Unauthorized:**
- Check WP_USER and WP_APP_PASSWORD
- Ensure Application Passwords are enabled in WordPress

**Categories not created:**
- Pre-create categories in WordPress admin
- Or ensure user has `edit_categories` capability

**Images not uploading:**
- Check file size limits in WordPress
- Verify media upload permissions

### Debug Mode

Add `-v` for verbose logging:
```bash
python jekyll_to_wp.py --source _posts/ --dry-run -v
```

## File Locations

- Scripts: `/home/wuxia/projects/workshop/scripts/tools/wordpress_migration/`
- Jekyll Posts: `/home/wuxia/projects/workshop/_posts/`
- Gridea Posts: `/home/wuxia/projects/zhurong2020.github.io/post/`
- WordPress Root: `/var/www/arong.eu.org/public_html/`
- Results: Working directory (where you run the script)
