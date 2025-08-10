#!/bin/bash
# 快速图片处理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
IMAGE_DIR=""
ARTICLE_DATE=$(date '+%Y/%m')
ANALYZE_ONLY=false

# 显示帮助
show_help() {
    cat << EOF
图片智能处理工具 v1.0

用法: $0 [选项] -d <图片目录>

选项:
  -d, --dir <dir>        图片目录路径 (必需)
  -t, --date <date>      文章日期，格式: YYYY/MM (默认: 当前月份)
  -a, --analyze         仅分析不处理
  -h, --help            显示此帮助信息

示例:
  $0 -d temp_images_20250808                    # 处理图片
  $0 -d temp_images_20250808 -a                 # 仅分析
  $0 -d temp_images_20250808 -t 2025/08         # 指定日期处理

存储策略:
  < 50KB      → 本地存储 (assets/images/)
  50-200KB    → 本地存储 + 压缩
  200KB-1MB   → CDN存储
  > 1MB       → CDN存储 + 生成缩略图

EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dir)
            IMAGE_DIR="$2"
            shift 2
            ;;
        -t|--date)
            ARTICLE_DATE="$2"
            shift 2
            ;;
        -a|--analyze)
            ANALYZE_ONLY=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 检查必需参数
if [[ -z "$IMAGE_DIR" ]]; then
    echo -e "${RED}错误: 必须指定图片目录${NC}"
    show_help
    exit 1
fi

# 检查目录是否存在
if [[ ! -d "$IMAGE_DIR" ]]; then
    echo -e "${RED}错误: 目录不存在: $IMAGE_DIR${NC}"
    exit 1
fi

# 检查是否有图片文件
image_count=$(find "$IMAGE_DIR" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.webp" \) | wc -l)

if [[ $image_count -eq 0 ]]; then
    echo -e "${YELLOW}警告: 在 $IMAGE_DIR 中未找到图片文件${NC}"
    exit 1
fi

echo -e "${BLUE}=== 图片智能处理工具 ===${NC}"
echo -e "目录: ${GREEN}$IMAGE_DIR${NC}"
echo -e "日期: ${GREEN}$ARTICLE_DATE${NC}"
echo -e "图片数量: ${GREEN}$image_count${NC}"
echo -e "模式: ${GREEN}$(if $ANALYZE_ONLY; then echo '仅分析'; else echo '分析+处理'; fi)${NC}"
echo

# 检查Python脚本是否存在
SCRIPT_PATH="scripts/tools/image_manager.py"
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo -e "${RED}错误: 图片管理脚本不存在: $SCRIPT_PATH${NC}"
    exit 1
fi

# 检查配置文件
CONFIG_PATH="config/image_config.json"
if [[ ! -f "$CONFIG_PATH" ]]; then
    echo -e "${YELLOW}警告: 配置文件不存在，将使用默认配置${NC}"
fi

# 检查Python依赖
if ! python3 -c "import PIL" 2>/dev/null; then
    echo -e "${RED}错误: 缺少PIL库，请运行: pip install Pillow${NC}"
    exit 1
fi

# 构建命令
cmd_args=("python3" "$SCRIPT_PATH" "--image-dir" "$IMAGE_DIR" "--article-date" "$ARTICLE_DATE")

if [[ -f "$CONFIG_PATH" ]]; then
    cmd_args+=("--config" "$CONFIG_PATH")
fi

if $ANALYZE_ONLY; then
    cmd_args+=("--analyze-only")
fi

# 执行命令
echo -e "${BLUE}执行命令:${NC} ${cmd_args[*]}"
echo

if "${cmd_args[@]}"; then
    echo
    echo -e "${GREEN}✅ 处理完成！${NC}"
    
    if ! $ANALYZE_ONLY; then
        echo
        echo -e "${BLUE}💡 下一步:${NC}"
        echo "1. 复制上面生成的Markdown链接到文章中"
        echo "2. 检查本地assets目录是否有新文件"
        echo "3. 如有CDN上传，验证链接可访问性"
        echo "4. 可以删除临时图片目录: rm -rf $IMAGE_DIR"
    fi
else
    echo
    echo -e "${RED}❌ 处理失败，请查看上方错误信息${NC}"
    exit 1
fi