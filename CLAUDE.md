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
   - ✅ **WeChat Official Account**: Complete draft saving workflow
     - Markdown to WeChat HTML conversion
     - OneDrive image upload to WeChat servers
     - AI-powered mobile layout optimization
     - Save to WeChat draft box for scheduled publishing
   - 🔄 **WordPress**: Basic API publishing (requires further enhancement)

2. **Publishing Status Management**:
   - ✅ **Status Tracking**: `_drafts/.publishing/*.yml` files track publication status
   - ✅ **Cross-platform Republishing**: Support republishing existing articles to other platforms
   - ✅ **Duplicate Prevention**: Automatically filter already-published platforms
   - ✅ **Local Preview**: WeChat versions saved to `_output/wechat_previews/`

3. **Content Enhancement Features**:
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

### Decision: WeChat Draft-Only Publishing Strategy ✅ (Completed)
- **Strategy**: Save articles as drafts in WeChat backend rather than immediate publication
- **Rationale**: Allows content creators to review, schedule, and batch publish through WeChat's native interface
- **Implementation**:
  - Content conversion (Markdown → HTML, image upload, AI optimization)
  - Save to WeChat draft box via API
  - Local preview files saved to `_output/wechat_previews/`
- **Benefits**: Maintains editorial control while automating content preparation

## 6. Development Workflow & Conventions

### Code Quality Standards
- **Coding Style**: Follow PEP 8 standards, use type annotations, maintain consistency with existing project code style
- **Error Handling**: Implement comprehensive error handling with meaningful log messages
- **Testing**: Core business logic modifications and additions require corresponding `pytest` test cases
- **Documentation**: Keep docstrings up-to-date, especially for public APIs

### Git Workflow
- **Commits**: Use descriptive commit messages following conventional commit format
- **Branching**: Work on feature branches, merge to main after testing
- **File Organization**: Maintain clean separation between production code, tests, and configuration

### Communication Protocol
- **Major Changes**: Claude Code will explain plans and request confirmation before executing critical operations
- **Status Updates**: Provide progress updates using TodoWrite tool for complex tasks
- **Decision Documentation**: Record all architectural decisions in this document

## 7. Project Structure Best Practices

### Directory Organization
- **`scripts/`**: Core functionality modules only (no test files)
- **`tests/`**: All test files, including platform-specific tests like `test_wechat_draft.py`
- **`config/`**: Configuration files organized by functionality (gemini, platforms, templates)
- **`_drafts/.publishing/`**: Publication status tracking files (included in Git)
- **`_output/`**: Generated files and previews (excluded from Git)

### File Naming Conventions
- **Status Files**: `article-name.yml` in `_drafts/.publishing/`
- **Preview Files**: `article-title_timestamp.html` and `article-title_timestamp.md` in `_output/wechat_previews/`
- **Test Files**: `test_feature_name.py` in `tests/`

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
- **Permissions**: Account must have draft management permissions

### Content Processing Standards
- **Link Removal**: All hyperlinks are removed and replaced with "阅读原文" guidance
- **Image Handling**: OneDrive images are automatically downloaded and re-uploaded to WeChat servers
- **Mobile Optimization**: AI-powered layout optimization for mobile reading experience
- **Preview Generation**: Local HTML and Markdown previews are always generated for review

## 10. Document Update History

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

**Last Updated**: 2025-07-15  
**Next Review**: When major features are added or architectural changes are needed