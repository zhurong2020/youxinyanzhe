# Claude Code Project Conventions

This document defines the conventions and guidelines for Claude Code (AI assistant) working on this blog publishing automation project.

## 1. Project Overview

This project is a robust, automated multi-platform blog content publishing system. The core goal is to streamline the entire workflow from content creation to final publication.

## 2. Claude Code's Role & Responsibilities

Claude Code serves as the AI software engineer for this project, with primary responsibilities:

- **Feature Implementation**: Develop, debug, and implement new features based on requirements
- **Code Refactoring & Optimization**: Continuously improve code readability, performance, and maintainability  
- **Automation Tasks**: Write and maintain automation scripts for testing and deployment workflows
- **Convention Adherence**: Strictly follow all technical decisions and development conventions defined in this document

## 3. Completed Core Tasks ✅

1. **Multi-platform Publishing System**:
   - ✅ **GitHub Pages**: Full Jekyll publishing with frontmatter processing
   - ✅ **WeChat Official Account**: Complete content processing with publish guidance workflow
     - Markdown to WeChat HTML conversion
     - OneDrive image upload to WeChat servers
     - AI-powered mobile layout optimization
     - Generate publish guidance files for manual publishing (due to API limitations)
   - 🔄 **WordPress**: Basic API publishing (requires further enhancement)

2. **YouTube Podcast Generator** ✅:
   - ✅ **English to Chinese Podcast**: Convert English YouTube videos to Chinese learning podcasts
   - ✅ **Automatic Article Generation**: Create Jekyll articles with embedded podcast audio
   - ✅ **Multi-language TTS Support**: Support for Chinese, English, Japanese, Korean TTS
   - ✅ **Flexible Configuration**: Multiple TTS models and conversation styles
   - ✅ **Learning Guide Generation**: Automatic English learning guides and content outlines
   - ✅ **Integration with Main Menu**: Full workflow integrated into run.py interface

3. **Publishing Status Management**:
   - ✅ **Status Tracking**: `_drafts/.publishing/*.yml` files track publication status
   - ✅ **Cross-platform Republishing**: Support republishing existing articles to other platforms
   - ✅ **Duplicate Prevention**: Automatically filter already-published platforms
   - ✅ **Publish Guidance**: WeChat guidance files saved to `.tmp/output/wechat_guides/`

4. **Content Enhancement Features**:
   - ✅ **Conditional Content**: Investment articles automatically include risk disclaimers
   - ✅ **UI Improvements**: Fixed subscription form alignment with flexbox
   - ✅ **AI Integration**: Gemini-powered content optimization

## 4. Current Development Focus

1. **System Optimization**:
   - Monitor and improve WeChat publishing reliability
   - Enhance WordPress publishing functionality
   - Add batch operation capabilities

2. **Documentation & Testing**:
   - Maintain comprehensive test coverage
   - Keep documentation synchronized with feature updates

3. **Article Sync Management System** (规划中):
   - 文章同步管理功能集成到run.py主菜单
   - 支持posts到archived的单个和批量同步
   - Gridea格式内容准备（去除frontmatter）
   - 同步状态检查和差异提示
   - 日志记录同步操作历史

## 5. Key Technical Decisions

This section records critical architectural adjustments for the project:

### Decision: Remove Cloudflare Images Upload Functionality ✅ (Completed)
- **Reason**: Current project traffic is low, using Cloudflare's free CDN for the entire site is sufficient for image acceleration needs, without requiring their specialized image storage and transformation services
- **Impact & Implementation**:
  - All `CloudflareImageMapper` related functionality has been removed
  - `scripts/image_mapper.py` file has been deleted
  - Image processing logic in `content_pipeline.py` has been completely removed
  - Images are served directly from the Git repository's `/assets/images/` directory with simple relative paths
  - Related configuration files and tests have been removed

### Decision: Use OneDrive as Image Hosting ✅ (Completed)
- **Strategy**: Upload images to OneDrive and use the "embed" functionality for document image loading
- **Benefits**: Simple, reliable, and cost-effective for low-volume image hosting
- **WeChat Integration**: OneDrive images are automatically downloaded and re-uploaded to WeChat servers during publishing

### Decision: Implement Source File Management for Multi-platform Publishing ✅ (Completed)
- **Strategy**: Use "方案A" - maintain source files in `_drafts/` directory for republishing
- **Implementation**:
  - Published articles can be converted back to source format for republishing to other platforms
  - Remove platform-specific frontmatter and footer content
  - Maintain original content integrity while adapting for different platforms
- **Benefits**: Enables flexible cross-platform content distribution without manual rework

### Decision: Publishing Status Management with YAML Files ✅ (Completed)
- **Strategy**: Track publication status using individual YAML files in `_drafts/.publishing/`
- **Implementation**:
  - Each article has a corresponding `article-name.yml` status file
  - Tracks published platforms, timestamps, and publication count
  - Enables intelligent platform filtering and duplicate prevention
- **Benefits**: Reliable state management, supports team collaboration, maintains publication history

### Decision: WeChat Publish Guidance Strategy ✅ (Completed)
- **Strategy**: Generate publish guidance files instead of direct API publishing due to permission limitations
- **Rationale**: WeChat API draft/publishing permissions require enterprise certification or special approval
- **Implementation**:
  - Complete content processing (Markdown → HTML, image upload, AI optimization)
  - Generate comprehensive publish guidance files in `.tmp/output/wechat_guides/`
  - Provide step-by-step instructions for manual publishing in WeChat backend
  - Include ready-to-use HTML content for direct copy-paste
- **Benefits**: Maintains full automation of technical processing while providing clear guidance for manual publication

### Decision: WeChat API Permission Investigation and Resolution ✅ (Completed)
- **Issue Discovered**: WeChat API returned `40007 invalid media_id` errors during draft saving attempts
- **Root Cause Analysis**:
  - IP whitelist configuration was required and resolved
  - Draft/publishing API permissions are limited to enterprise-certified accounts
  - Basic personal/organization accounts lack sufficient API permissions for automated publishing
- **Investigation Process**:
  - Used WeChat official API debugging tools to verify request formats
  - Tested multiple API endpoints (`/draft/add`, `/material/add_news`, `/freepublish/submit`)
  - Confirmed access_token generation and image upload functionality works correctly
- **Final Resolution**: Pivot to publish guidance file generation strategy

## 6. Development Workflow & Conventions

### Code Quality Standards
- **Coding Style**: Follow PEP 8 standards, use type annotations, maintain consistency with existing project code style
- **Type Safety**: Always use explicit type conversions (e.g., `str()`, `int()`) when IDE indicates type issues
- **Import Standards**: Use correct import paths (e.g., `from google.generativeai.generative_models import GenerativeModel`)
- **Error Handling**: Implement comprehensive error handling with meaningful log messages
- **Testing**: Core business logic modifications and additions require corresponding `pytest` test cases
- **Documentation**: Keep docstrings up-to-date, especially for public APIs

### Testing Standards and Conventions
- **Test File Organization**: All test files must be placed in the `tests/` directory
- **Debug Tools Organization**: Standalone debugging tools moved to `scripts/tools/` directory:
  - `wechat_api_debug.py`: WeChat API testing and debugging
  - `wechat_system_verify.py`: System verification utilities
- **Existing Test Modules**: Always check and utilize existing test modules before creating new ones:
  - `test_wechat_draft.py`: WeChat functionality testing
  - `test_content_pipeline.py`: Content processing pipeline tests
  - `conftest.py`: Shared test fixtures and configurations
  - `run_tests.py`: Test runner with custom configurations
- **Test File Naming**: Follow `test_*.py` pattern for all test files
- **Test Generation**: Test article generation functionality improved with:
  - Enhanced AI prompts to avoid format issues
  - Content cleaning logic to remove explanatory text
  - Proper front matter handling
- **Test Isolation**: Each test should be independent and not rely on external state
- **Cleanup**: Remove temporary test files after testing completion, maintain clean project structure

### Virtual Environment Usage (CRITICAL)
- **Virtual Environment Location**: `venv/` directory in project root
- **Activation Command**: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- **Requirements**: All dependencies listed in `requirements.txt`
- **Python Version**: Python 3.8+ required
- **Important**: ALWAYS activate virtual environment before:
  - Running `run.py` or any project scripts
  - Installing dependencies with `pip install`
  - Running tests with `pytest`
  - Using any Python development tools
- **Verification**: Check activation with `which python` - should point to `venv/bin/python`
- **Deactivation**: Use `deactivate` command when done
- **IDE Configuration**: Ensure VS Code/PyCharm uses `venv/bin/python` as interpreter

### Git Workflow
- **Commits**: Use descriptive commit messages following conventional commit format
- **Branching**: Work on feature branches, merge to main after testing
- **File Organization**: Maintain clean separation between production code, tests, and configuration

### Communication Protocol
- **Major Changes**: Claude Code will explain plans and request confirmation before executing critical operations
- **Status Updates**: Provide progress updates using TodoWrite tool for complex tasks
- **Decision Documentation**: Record all architectural decisions in this document

### Content Classification and Series Management Standards

#### 四大核心分类体系
博客采用四大核心分类体系，所有新文章必须归入以下之一：
- **🧠 Cognitive Upgrade** (`categories: [cognitive-upgrade]`): 思维模型、学习方法、认知心理学、决策科学
- **🛠️ Tech Empowerment** (`categories: [tech-empowerment]`): 实用工具推荐、技术教程、自动化方案、效率提升
- **🌍 Global Perspective** (`categories: [global-perspective]`): 国际趋势洞察、文化差异观察、跨文化思维训练
- **💰 Investment & Finance** (`categories: [investment-finance]`): 投资策略、理财方法、财务自由规划、量化分析

#### 系列文章导航系统设计方案 (待实现)

**设计目标**: 在分类页面右侧边栏添加系列文章导航，方便用户在大类下选择特定系列

**技术实现方案**:
1. **标签体系**: 使用Jekyll的tags系统标识系列文章
   - 格式: `tags: ["系列名称", "其他标签"]`
   - 示例: `tags: ["普通人云生活", "VPS教程", "技术工具"]`

2. **系列定义约定**:
   ```yaml
   # _data/series.yml
   技术赋能:
     - name: "普通人云生活"
       tag: "普通人云生活"
       description: "利用云技术提升生活效率"
       icon: "☁️"
     - name: "AI工具实战"
       tag: "AI工具"
       description: "人工智能工具使用指南"
       icon: "🤖"
   
   全球视野:
     - name: "Musk Empire"
       tag: "马斯克帝国"
       description: "深度解析马斯克商业帝国"
       icon: "🚀"
   ```

3. **侧边栏组件设计**:
   - 位置: 分类页面右侧边栏 (利用Jekyll主题的sidebar功能)
   - 结构: 系列标题 + 文章列表 + 系列描述
   - 样式: 与主题一致的卡片式设计
   - 交互: 点击系列名展开/收起文章列表

4. **实现步骤**:
   - 创建`_includes/series-navigation.html`组件
   - 在分类页面模板中引入侧边栏组件
   - 使用Liquid语法动态生成系列导航
   - 添加相应的CSS样式

**内容创作约定**:
- 系列文章必须使用统一的标签命名
- 首篇文章应包含系列介绍和导航
- 每篇文章应包含系列内的前后文章链接
- **Front Matter Standards**: 
  - **Required Fields**: Only 3 fields are mandatory: `title`, `date`, and `header`
  - **Title Length**: 25-35 characters for optimal 3×2 grid display (2-3 lines in homepage layout)
  - **Excerpt Field**: Must be included for all articles, 50-60 characters maximum
    - Appears in homepage article previews and page headers
    - Use double quotes, avoid nested quotes to prevent YAML parsing errors
    - Focus on key value proposition, avoid detailed descriptions
  - **Classification Field**: `categories` must contain exactly one of the four core categories above (using English slugs)
  - **Automatic Processing**: content_pipeline.py will automatically add other necessary fields during distribution
- **Article Structure**: Each article must include:
  - **Opening Hook**: Brief engaging opening (matching excerpt content) after front matter
  - **More Tag**: `<!-- more -->` tag to separate preview from full content
  - **Background Context**: Optional background information after more tag for reader context
  - **Main Content Introduction**: Natural transition leading into detailed content
  - **🎧 播客收听** section with AI-generated Chinese podcast (length adjusted to content)
  - **🌍 英文原始资料** section with original English sources for learning and research
- **Writing Style**: Follow established blog style from zhurong2020.github.io:
  - Objective, fact-based approach rather than personal opinions
  - Use "你知道吗?" and similar engaging opening questions
  - Scientific popularization tone for general audiences
  - Data-driven arguments with specific numbers and comparisons
  - Open-ended questions to encourage reader thinking
  - Series articles should leave space for future content expansion

### Jekyll Assets Path Standards (Critical for GitHub Pages Deployment)
- **Problem Context**: Site deployed with `baseurl: "/youxinyanzhe"` requires special path handling
- **NEVER use absolute paths** like `/assets/images/...` or `/assets/audio/...`
- **ALWAYS use Jekyll baseurl variable**: `{{ site.baseurl }}/assets/...`
- **Asset Path Examples**:
  - ❌ Wrong: `<img src="/assets/images/example.jpg">`
  - ✅ Correct: `<img src="{{ site.baseurl }}/assets/images/example.jpg">`
  - ❌ Wrong: `<source src="/assets/audio/podcast.mp3">`
  - ✅ Correct: `<source src="{{ site.baseurl }}/assets/audio/podcast.mp3">`
  - ❌ Wrong: `![Image](/assets/images/example.gif)`
  - ✅ Correct: `![Image]({{ site.baseurl }}/assets/images/example.gif)`
- **Asset Organization**:
  - Images: `/assets/images/posts/YYYY/MM/filename.ext`
  - Audio: `/assets/audio/filename.mp3`
  - Static assets: `/assets/css/`, `/assets/js/`
- **Testing Protocol**: Always test assets on both local Jekyll server and GitHub Pages
- **Common Symptoms of Path Issues**:
  - Images not displaying (broken image icons)
  - Audio players showing as disabled/grayed out
  - CSS/JS not loading properly
- **Debugging**: Use browser developer tools Network tab to check for 404 errors on asset URLs

### Testing and Debugging Workflow
- **Test File Organization**: Maintain clean separation between tests (`tests/`) and tools (`scripts/tools/`)
- **Debugging Strategy**: Use dedicated debugging tools in `scripts/tools/` for specific issues
- **Logging and Debugging**: 
  - Unified logging system with `.build/logs/pipeline.log`
  - Intelligent log level filtering (DEBUG only in verbose mode)
  - Session tracking with unique identifiers
  - Log rotation to prevent file bloat
- **Tool Naming**: Use descriptive names like `wechat_api_debug.py`, `wechat_system_verify.py`
- **Cleanup Protocol**: Remove temporary debug files after issues are resolved, keep organized structure

## 7. Project Structure Best Practices

### Directory Organization
- **`docs/`**: Project documentation and guides
- **`scripts/`**: Core functionality modules organized by purpose
  - **`core/`**: Core business logic (content_pipeline, wechat_publisher)
  - **`utils/`**: Reusable utilities and helper functions
  - **`tools/`**: Standalone tools and scripts
- **`tests/`**: All test files, including platform-specific tests and debugging utilities
- **`config/`**: Configuration files organized by functionality (gemini, platforms, templates)
- **`_drafts/.publishing/`**: Publication status tracking files (included in Git)
- **`_drafts/archived/`**: Archived completed articles for reference
- **`_drafts/musk-empire/`**: Musk Empire series planning and requirements files
- **`.build/`**: Build and runtime files (excluded from Git)
  - **`logs/`**: Application logs
  - **`htmlcov/`**: Test coverage reports
- **`.tmp/`**: Temporary files and outputs (excluded from Git)
  - **`output/wechat_guides/`**: WeChat publish guidance files
  - **`output/wechat_image_cache/`**: WeChat uploaded image cache and mappings
  - **`output/packages/`**: Generated content packages

### File Naming Conventions
- **Status Files**: `article-name.yml` in `_drafts/.publishing/`
- **Guidance Files**: `article-title_timestamp_guide.md` and `article-title_timestamp_content.html` in `.tmp/output/wechat_guides/`
- **Test Files**: `test_feature_name.py` in `tests/`
- **Debug Files**: `test_*_debug.py`, `test_*_verify.py` for debugging and verification utilities

## 8. Security Practices

### Sensitive Data Management
- **Environment Variables**: Use `.env` files for sensitive data, exclude from version control
- **API Keys**: Never commit secrets to the repository
- **IP Whitelisting**: WeChat API requires IP whitelist configuration in official account backend

### Deployment Security
- **VPS Deployment**: Use static IP addresses for production WeChat publishing
- **Access Control**: Limit API permissions to minimum required scope
- **Dependencies**: Keep requirements.txt updated and minimal, avoid unnecessary packages

## 9. WeChat Integration Specific Guidelines

### API Configuration Requirements
- **Credentials**: `WECHAT_APPID` and `WECHAT_APPSECRET` must be set in `.env`
- **IP Whitelist**: Production server IP must be configured in WeChat backend
- **Permissions**: Account must have "永久素材管理" (permanent material management) permissions
- **API Limits**: System automatically tracks daily API call limits:
  - Token requests: 2000/day
  - Image uploads: 1000/day
  - Material additions: 1000/day
  - News creations: 1000/day

### Content Processing Standards
- **Two-stage AI Processing**: 
  - Stage 1: Content summarization and rewriting for WeChat audience
  - Stage 2: Mobile-friendly HTML formatting with inline CSS and emojis
- **Link Removal**: All hyperlinks are removed and replaced with "阅读原文" guidance
- **Image Handling**: OneDrive images are automatically downloaded and re-uploaded to WeChat servers
- **Mobile Optimization**: AI-powered layout optimization for mobile reading experience
- **Publishing Modes**:
  - **API Mode**: Direct publishing to WeChat draft box via permanent material API
  - **Guide Mode**: Generate detailed manual publishing guidance files
- **HTML Cleaning**: Content is cleaned and optimized for WeChat editor compatibility

## 10. Document Update History

### 2025-08-04: YouTube播客生成器多语言支持和OAuth认证修复 ✅
- **多语言播客生成修复**:  
  - ✅ 修复播客脚本生成语言逻辑，现在正确支持中文、英文、日文、韩文四种语言
  - ✅ 修复TTS语音合成语言适配，根据target_language自动选择对应语言
  - ✅ 修复备用脚本生成，针对不同语言提供对应的对话内容
  - ✅ 在generate_from_youtube方法中保存当前目标语言供TTS使用
- **YouTube上传OAuth认证优化**:
  - ✅ 增强YouTube API配置，支持OAuth和API Key两种认证方式
  - ✅ 添加OAuth token自动刷新机制，无需重复认证
  - ✅ 在上传前检查认证类型，只允许OAuth用户上传
  - ✅ 提供清晰的错误提示和scripts/tools/youtube_oauth_setup.py工具指引
- **文档完善**:
  - ✅ 更新youtube_podcast_setup.md，新增多语言选择和OAuth设置说明
  - ✅ 添加外部工具使用指南，包括OAuth设置工具路径
  - ✅ 完善故障排除部分，涵盖语言生成和认证问题解决方案
  - ✅ 明确OAuth认证持久性和自动管理特性
- **技术改进**:
  - 播客脚本prompt根据目标语言动态生成（中/英/日/韩）
  - TTS引擎智能语言适配（gTTS支持en/zh-CN/ja/ko）
  - YouTube API双重认证支持（OAuth用于上传，API Key用于读取）
  - 自动token刷新和错误恢复机制

### 2025-08-04: 多级会员验证系统完整实现与价格优化 ✅
- **会员系统核心功能**:
  - ✅ 完整的多级会员验证系统（体验、月度、季度、年度）
  - ✅ 用户信息收集和管理流程
  - ✅ 自动化访问码生成和邮件发送系统
  - ✅ 会员专区页面和权限分级显示
  - ✅ 后端管理脚本和数据统计功能
- **价格体系优化**:
  - 月度会员：¥19 → ¥35 (对应 Buy Me Coffee 1杯 $5)
  - 季度会员：¥49 → ¥108 (对应 Buy Me Coffee 3杯 $15)  
  - 年度会员：¥159 → ¥180 (对应 Buy Me Coffee 5杯 $25)
  - 年度会员提供最佳性价比：每月仅¥15 (57%折扣)
- **技术实现**:
  - JavaScript前端验证码验证系统
  - Python后端管理和邮件发送
  - Jekyll页面集成和导航菜单更新
  - 环境配置和安全数据管理
- **运营策略**:
  - 与Buy Me Coffee支付渠道完美对接
  - 合理的价格梯次鼓励长期订阅
  - 灵活的内容分级和权限管理
- **文档完善**:
  - 完整的使用指南和操作手册
  - 价格配置和系统维护说明
  - 故障排除和扩展指导

## 10. Document Update History (Historical)

### 2025-07-27: 文章标题和摘要长度规范化 ✅
- **标题长度标准**: 建立25-35字最佳标题长度规范
  - 优化3×2网格布局的2-3行显示效果
  - 修复过短标题（18字→27字，16字→35字）
  - 微调中等长度标题提升关键词密度
- **摘要字段规范**: 统一excerpt字段要求
  - 严格控制在50-60字范围内
  - 避免YAML引号嵌套问题
  - 专注核心价值主张，提升首页显示效果
- **脚本prompt同步**: 更新AI生成规范
  - content_pipeline.py摘要生成prompt更新
  - gemini_config.yml测试文章生成规范同步
  - 确保自动化流程与手动规范一致
- **文档完善**: 在Front Matter Standards中详细记录规范要求

### 2025-07-25: 主页布局优化与分类页面完善 ✅
- **布局问题修复**: 解决主页四个关键布局问题
  - 内容分类导航从1x4高度过高恢复为2x2紧凑布局
  - 修复标题上方间距过大，使用精确margin控制
  - 订阅区域标题上边距优化，提升视觉密度
  - 分类页面文章显示从密集4列改为按行列表显示
- **分类页面系统**: 创建完整的四大分类页面体系
  - 每个分类页面包含详细说明和内容方向指导
  - 使用Jekyll主题的category布局和list显示模式
  - 统一的页面结构和用户体验
- **视觉一致性**: 利用Jekyll主题功能实现更好的集成
  - 精确的间距控制和响应式设计
  - 保持与主题设计语言的一致性
  - 动态统计数据和交互效果

### 2025-07-25: 博客四大核心分类体系重构 ✅
- **重构完成**: 实施基于用户价值定位的四大核心分类体系
- **新分类体系**:
  - **🧠 认知升级系列**: 思维模型、学习方法、认知心理学与决策科学
  - **🛠️ 技术赋能系列**: 实用工具推荐、技术教程与自动化方案
  - **🌍 全球视野系列**: 国际趋势洞察、文化差异观察与跨文化思维训练
  - **💰 投资理财系列**: 投资思维培养、理财方法实践与财务自由规划
- **文章重新归类**: 全部14篇现有文章按新体系重新分类
  - 认知升级系列：1篇 (需要重点补强)
  - 技术赋能系列：4篇 (AI工具、自托管、VPS、远程工具)
  - 全球视野系列：5篇 (Tesla分析系列、新闻观点分析)
  - 投资理财系列：4篇 (美股投资、QDII基金、量化策略、加密货币)
- **主页全面升级**: 
  - 更新四大分类展示布局，使用2x2网格展示
  - 重新设计intro文案体现核心价值定位
  - 优化按钮文案和精选推荐逻辑适配新分类
- **战略价值**:
  - 聚焦投资理财系列作为主要流量入口和变现重点
  - 强化全球视野差异化竞争优势
  - 为后续内容创作和用户增长提供清晰方向定位
- **实施原则**: 基于"让普通人受益于科技、全球视野与终身学习"的核心理念

### 2025-07-24: System Optimization and Logging Enhancement ✅
- **Fixed**: Test article generation issues including double front matter and AI explanation text
- **Enhanced**: Gemini prompt optimization to generate cleaner content without embedded YAML blocks
- **Improved**: Content cleaning logic to properly remove AI explanatory text
- **Optimized**: Logging system to reduce duplicate records and improve clarity
- **Unified**: Log directory structure to `.build/logs/` with file rotation
- **Cleaned**: Duplicate test files and reorganized debug tools to `scripts/tools/`
- **Added**: Intelligent logging with level filtering and session tracking
- **Benefits**: More stable test article generation, cleaner logs, better developer experience

### 2025-07-24: Project Structure Refactoring ✅
- **Added**: Unified `docs/` directory for all project documentation
- **Refactored**: Script organization with `core/`, `utils/`, and `tools/` subdirectories
- **Improved**: Runtime file management with `.build/` and `.tmp/` directories
- **Updated**: All import paths and file references to match new structure
- **Enhanced**: .gitignore to properly exclude temporary and build files
- **Benefits**: Better separation of concerns, cleaner project structure, follows software engineering best practices

### 2025-07-24: Jekyll Assets Path Standards and Media Fix ✅
- **Added**: Critical Jekyll Assets Path Standards section to prevent baseurl deployment issues
- **Fixed**: Tesla article audio player grayed out issue - incorrect asset paths
- **Fixed**: OneDrive GIF images not displaying - path and format issues
- **Established**: Mandatory use of `{{ site.baseurl }}` variable for all asset paths
- **Documentation**: Common symptoms, debugging methods, and asset organization standards
- **Testing Protocol**: Requirements for local and GitHub Pages testing
- **Root Cause**: GitHub Pages deployment with baseurl="/youxinyanzhe" requires Jekyll variable usage
- **Prevention**: Clear examples of correct vs incorrect path syntax for images, audio, CSS/JS

### 2025-07-24: Enhanced Content Format - Podcast and English Resources ✅
- **Added**: New mandatory content sections for all blog articles:
  - **🎧 播客收听**: AI-generated Chinese podcast version (using 豆包 AI, length adjusted to content)
  - **🌍 英文原始资料**: Original English sources for advanced readers and English learning
- **Content Strategy Enhancement**: 
  - Podcast provides accessible content consumption for commuting readers
  - English resources serve dual purpose: in-depth research and language learning materials
  - Maintains content accessibility across different reader preferences and skill levels
- **Implementation**: Successfully applied to Tesla Unboxed Manufacturing article as template
- **Technical Details**:
  - Podcast section includes MP3 links, estimated duration, and usage suggestions
  - English section categorizes content by type (video, audio) with difficulty levels and key terminology
  - Both sections use emoji-based visual organization for easy scanning

### 2025-07-20: Investment-Oriented Content Strategy Framework ✅
- **Added**: Comprehensive "Investment-Oriented Content Strategy" framework in Section 12
- **Core Innovation**: Technology + Investment synergy approach to attract high-quality readership
- **Theoretical Foundation**: Integration of classic financial literature (《金钱心理学》、《穷查理的宝典》、《穷爸爸富爸爸》)
- **Cross-Series Strategy**: Natural cross-referencing between "Musk Empire" and "Investment & Quantitative Trading" series
- **Content Guidelines**: 
  - Balanced narrative avoiding sensationalism for objective data analysis
  - Historical perspective using technology development cases for investment thinking
  - Quantitative analysis with trackable metrics and milestone indicators
  - Risk assessment balancing technical challenges with rational optimism
- **Reader Conversion**: Value-driven approach providing concrete investment analysis frameworks
- **Implementation**: Successfully applied to Tesla Optimus article as pilot case study
- **Reference Integration**: Connects with existing blog content (zhurong2020.github.io) for consistency

### 2025-07-19: Musk Empire Series Research Enhancement & Bug Fixes ✅
- **Added**: Comprehensive research on X (formerly Twitter) and The Boring Company for Musk Empire series
- **Created**: Detailed supplement document `musk-empire-supplement-x-boring-company.md` with latest 2025 data
- **Updated**: Tesla AI Empire article with X and Boring Company content integration
- **Enhanced**: Series planning document with deep research materials for future articles
- **Fixed**: Date correction from 2025-01-18 to 2025-07-18 in Tesla article
- **Bug Fixes**:
  - Fixed multi-platform input parsing issue (input "1,2" causing "invalid input" error)
  - Fixed Gemini API safety filter blocking normal tech content (finish_reason=2)
  - Added safety settings to allow technical article content generation
  - Enhanced error handling for API response validation
- **Key Research Findings**:
  - X acquisition by xAI for $33B in March 2025, transforming into AI data engine
  - Boring Company valuation exceeds $7B, serving 3M+ passengers in Vegas Loop
  - Cross-company synergies: $2B SpaceX investment in xAI, extensive tech sharing
  - Investment perspective: emphasize fact-based analysis over media conclusions

### 2025-07-17: Content Creation and Series Management ✅
- **Added**: "Musk Empire" series management conventions in Section 12
- **Added**: Content creation workflow and lifecycle management
- **Added**: Series consistency and reader engagement guidelines
- **Updated**: Directory organization to include `_drafts/musk-empire/` and `_drafts/archived/` 
- **Updated**: File naming conventions for series planning and archived content
- **Updated**: Project structure documentation to reflect content creation needs

### 2025-07-16: WeChat API升级和代码规范完善 ✅
- **WeChat API双模式**: 实现API直接发布和指导文件生成两种模式
- **永久素材管理**: 集成微信公众号永久素材管理接口
- **API限制管理**: 新增智能API调用量跟踪和限制管理
- **AI两阶段处理**: 内容精简和移动端排版的双重AI优化
- **代码规范更新**: 完善类型安全、导入标准和测试规范
- **测试约定**: 明确测试文件组织和现有测试模块使用规范

### 2025-07-15: WeChat API Investigation and Workflow Optimization ✅
- **Added**: WeChat API permission investigation and resolution decision
- **Added**: Testing and debugging workflow conventions based on recent experience
- **Added**: Type safety requirements for code quality standards
- **Updated**: WeChat publishing strategy from draft-saving to publish guidance generation
- **Updated**: Directory organization to reflect new `wechat_guides` structure
- **Updated**: File naming conventions for guidance files and debug utilities
- **Updated**: Content processing standards to include HTML cleaning and guidance generation

### 2025-07-15: Major Update - Multi-platform Publishing System ✅
- **Added**: Completed core tasks section with detailed feature status
- **Added**: New technical decisions for source file management and publishing status tracking
- **Added**: WeChat draft-only publishing strategy documentation
- **Added**: Comprehensive security practices for API integration
- **Added**: WeChat-specific integration guidelines and requirements
- **Updated**: Project structure best practices to reflect current architecture
- **Updated**: Development workflow to include TodoWrite usage and decision documentation

### Initial Version: Project Foundation
- **Established**: Basic project overview and Claude Code responsibilities
- **Documented**: Cloudflare Images removal decision
- **Documented**: OneDrive image hosting strategy
- **Established**: Core development conventions and security practices

---

**Note**: This document serves as the living guideline for all development work. It should be updated whenever major architectural decisions are made or significant features are implemented.

**Last Updated**: 2025-07-20  
**Next Review**: When major features are added or architectural changes are needed

## 11. Key Lessons from Recent Development

### WeChat API Integration Challenges
- **Permission Requirements**: Enterprise certification often required for full API access
- **Alternative Approaches**: When direct API access is limited, focus on maximizing automation of preparatory work
- **User Experience**: Well-structured guidance files can provide significant value even when full automation isn't possible

### Debugging and Testing Best Practices
- **Systematic Investigation**: Use official debugging tools when available to verify API requests
- **Incremental Testing**: Test each component (authentication, image upload, content processing) separately
- **Clean Project Structure**: Regularly clean up temporary debug files and organize reusable test utilities

## 12. Content Creation and Series Management

### "Musk Empire" Series Conventions
- **Planning Files**: All series planning and requirements are centralized in `_drafts/musk-empire/`
  - `series-plan.md`: Complete series outline and chapter structure
  - `writing-requirements.md`: Detailed writing guidelines and style conventions
- **Content Creation Process**:
  1. Reference planning files in `_drafts/musk-empire/` for topic selection and style guidelines
  2. Create new articles directly in `_drafts/` root directory
  3. Follow established writing style: engaging, insightful, data-driven
  4. Include reader interaction elements and series navigation
- **Article Lifecycle Management**:
  - **Draft Stage**: Work on articles in `_drafts/` root directory
  - **Publishing**: Use existing multi-platform publishing system
  - **Archival**: Move completed articles to `_drafts/archived/` for reference
- **Series Consistency**: Maintain consistent tone, formatting, and cross-references between articles

### Content Creation Best Practices
- **Research-Based Writing**: Use provided source materials and maintain factual accuracy
- **Audience Focus**: Target Chinese domestic readers with relevant data and cultural context
- **Technical Depth**: Balance technical accuracy with accessibility for general readers
- **Series Continuity**: Reference previous articles and build narrative progression
- **Reader Engagement**: Include thought-provoking questions and encourage comments

### Investment-Oriented Content Strategy (New Framework - 2025-07-20)

#### Core Philosophy: Technology + Investment Synergy
- **Target Audience**: Attract readers interested in both technology innovation and investment/financial management
- **Content Integration**: Seamlessly blend technical analysis with investment thinking to create higher reader value
- **Long-term Engagement**: Guide readers toward comprehensive investment education and rational decision-making

#### Cross-Series Integration Strategy
- **"Musk Empire" Series**: Focus on technology innovation while incorporating investment perspective analysis
- **Investment & Quantitative Trading Series**: Provide practical investment methods and financial management tools
- **Natural Cross-referencing**: Create organic connections between series to enhance reader stickiness and learning continuity

#### Theoretical Framework: Classic Financial Literature
**Primary Reference Books**:
- **《金钱心理学》(The Psychology of Money)**: 
  - Emphasize avoiding emotional decision-making, focus on data-driven analysis
  - Explain media preference for pessimistic narratives vs. objective technical assessment
  - Use historical cases (e.g., 1903 Washington Post's prediction about human flight) to illustrate cognitive limitations
- **《穷查理的宝典》(Poor Charlie's Almanack)**: 
  - Apply multi-model thinking to evaluate disruptive companies
  - Emphasize first-principles thinking and long-term perspective
- **《穷爸爸富爸爸》(Rich Dad Poor Dad)**: 
  - Distinguish between investment opportunities and speculation
  - Emphasize financial education and independent thinking

#### Content Creation Guidelines
**Investment Thinking Integration**:
1. **Balanced Narrative**: Avoid sensationalism, provide objective data analysis
2. **Historical Perspective**: Use historical technology development cases to guide current investment thinking
3. **Quantitative Analysis**: Provide trackable metrics and milestone indicators
4. **Risk Assessment**: Honestly discuss technical challenges while maintaining rational optimism
5. **Reader Interaction**: Include investment-oriented discussion questions

**Practical Application**:
- Reference existing blog content (zhurong2020.github.io) for consistency
- Connect with quantitative trading methods and AI-assisted investment tools
- Emphasize "technology empowering individual investment" philosophy
- Provide specific thinking frameworks and actionable insights

#### Reader Conversion Strategy
- **Natural Guidance**: Lead readers from technology content to investment thinking
- **Value Creation**: Provide concrete investment analysis frameworks, not just concept introduction
- **Series Synergy**: Create anticipation for investment content through technology articles
- **Community Building**: Encourage rational discussion and independent thinking in comment sections