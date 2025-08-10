#!/bin/bash
# OneDrive博客图床快速处理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
DRAFT_FILE=""
DRAFTS_DIR="_drafts"
CONFIG_FILE="config/onedrive_config.json"
SETUP_MODE=false
BATCH_MODE=false

# 显示帮助
show_help() {
    cat << EOF
OneDrive博客图床处理工具 v1.0

用法: $0 [选项]

选项:
  -d, --draft <file>     处理指定的草稿文件
  -b, --batch [dir]      批量处理草稿目录 (默认: _drafts)
  -c, --config <file>    配置文件路径 (默认: config/onedrive_config.json)
  -s, --setup           初始化OneDrive认证设置
  -h, --help            显示此帮助信息

示例:
  $0 --setup                                    # 初始化认证
  $0 -d _drafts/2025-08-08-article.md          # 处理单个文件
  $0 --batch                                    # 批量处理_drafts目录
  $0 --batch my_drafts                          # 批量处理指定目录

功能说明:
  - 自动检测Markdown中的本地图片链接
  - 上传图片到OneDrive指定目录结构
  - 获取嵌入式分享链接
  - 自动替换文章中的图片链接
  - 支持Jekyll baseurl格式

EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--draft)
            DRAFT_FILE="$2"
            shift 2
            ;;
        -b|--batch)
            BATCH_MODE=true
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                DRAFTS_DIR="$2"
                shift 2
            else
                shift
            fi
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -s|--setup)
            SETUP_MODE=true
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

# 检查Python脚本是否存在
SCRIPT_PATH="scripts/tools/onedrive_blog_images.py"
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo -e "${RED}错误: OneDrive图床脚本不存在: $SCRIPT_PATH${NC}"
    exit 1
fi

# 检查Python依赖
check_dependencies() {
    local missing_deps=()
    
    if ! python3 -c "import requests" 2>/dev/null; then
        missing_deps+=("requests")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo -e "${RED}错误: 缺少Python依赖: ${missing_deps[*]}${NC}"
        echo -e "${YELLOW}请运行: pip install ${missing_deps[*]}${NC}"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo -e "${YELLOW}警告: 配置文件不存在: $CONFIG_FILE${NC}"
        echo -e "${BLUE}将使用默认配置创建...${NC}"
        
        # 创建默认配置文件目录
        mkdir -p "$(dirname "$CONFIG_FILE")"
        
        # 这里可以创建默认配置，但目前让脚本自己处理
        echo -e "${YELLOW}请先运行 --setup 进行初始化设置${NC}"
        return 1
    fi
    return 0
}

echo -e "${BLUE}=== OneDrive博客图床处理工具 ===${NC}"

# 检查依赖
check_dependencies

# 构建基础命令
cmd_args=("python3" "$SCRIPT_PATH" "--config" "$CONFIG_FILE")

if $SETUP_MODE; then
    # 设置模式
    echo -e "${BLUE}🚀 启动OneDrive认证设置...${NC}"
    cmd_args+=("--setup")
    
elif [[ -n "$DRAFT_FILE" ]]; then
    # 单文件处理模式
    if [[ ! -f "$DRAFT_FILE" ]]; then
        echo -e "${RED}错误: 草稿文件不存在: $DRAFT_FILE${NC}"
        exit 1
    fi
    
    if ! check_config; then
        exit 1
    fi
    
    echo -e "${BLUE}📝 处理草稿文件: ${GREEN}$DRAFT_FILE${NC}"
    cmd_args+=("--draft" "$DRAFT_FILE")
    
elif $BATCH_MODE; then
    # 批量处理模式
    if [[ ! -d "$DRAFTS_DIR" ]]; then
        echo -e "${RED}错误: 草稿目录不存在: $DRAFTS_DIR${NC}"
        exit 1
    fi
    
    if ! check_config; then
        exit 1
    fi
    
    draft_count=$(find "$DRAFTS_DIR" -name "*.md" -type f | wc -l)
    echo -e "${BLUE}📁 批量处理草稿目录: ${GREEN}$DRAFTS_DIR${NC}"
    echo -e "${BLUE}发现 ${GREEN}$draft_count${BLUE} 个Markdown文件${NC}"
    
    cmd_args+=("--batch" "$DRAFTS_DIR")
    
else
    # 无参数，显示帮助
    show_help
    exit 0
fi

echo -e "${BLUE}执行命令:${NC} ${cmd_args[*]}"
echo

# 执行命令
if "${cmd_args[@]}"; then
    echo
    if $SETUP_MODE; then
        echo -e "${GREEN}✅ OneDrive认证设置完成！${NC}"
        echo -e "${BLUE}💡 下一步:${NC}"
        echo "1. 现在可以处理草稿文件了"
        echo "2. 使用 -d <file> 处理单个文件"
        echo "3. 使用 --batch 批量处理所有草稿"
    elif [[ -n "$DRAFT_FILE" ]]; then
        echo -e "${GREEN}✅ 草稿处理完成！${NC}"
        echo -e "${BLUE}💡 提示:${NC}"
        echo "- 检查文章中的图片链接是否已更新"
        echo "- 本地图片文件可以选择性删除"
        echo "- 文章现在可以发布了"
    elif $BATCH_MODE; then
        echo -e "${GREEN}✅ 批量处理完成！${NC}"
        echo -e "${BLUE}💡 建议:${NC}"
        echo "- 检查处理日志了解详细结果"
        echo "- 验证几个文件的图片链接"
        echo "- 考虑清理本地图片文件"
    fi
else
    echo
    echo -e "${RED}❌ 处理失败，请查看上方错误信息${NC}"
    
    if $SETUP_MODE; then
        echo -e "${YELLOW}💡 故障排除:${NC}"
        echo "- 确保网络连接正常"
        echo "- 检查Azure应用配置"
        echo "- 验证重定向URI设置"
    else
        echo -e "${YELLOW}💡 故障排除:${NC}"
        echo "- 检查是否已完成认证设置 (运行 --setup)"
        echo "- 验证配置文件格式"
        echo "- 确认图片文件路径正确"
    fi
    
    exit 1
fi