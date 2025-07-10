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

## 3. Current Core Tasks

1. **Multi-platform Publishing Implementation**:
   - Complete WordPress publishing functionality
   - Complete WeChat official account publishing functionality
   - Ensure publishing workflow robustness and proper error handling

2. **Codebase Alignment**:
   - Refactor and clean existing codebase according to the "Key Technical Decisions" below

## 4. Key Technical Decisions

This section records critical architectural adjustments for the project:

### Decision: Remove Cloudflare Images Upload Functionality
- **Reason**: Current project traffic is low, using Cloudflare's free CDN for the entire site is sufficient for image acceleration needs, without requiring their specialized image storage and transformation services
- **Impact & Implementation**:
  - All `CloudflareImageMapper` related functionality has been removed
  - `scripts/image_mapper.py` file has been deleted
  - Image processing logic in `content_pipeline.py` has been completely removed
  - Images are served directly from the Git repository's `/assets/images/` directory with simple relative paths
  - Related configuration files and tests have been removed

### Decision: Use OneDrive as Image Hosting
- **Strategy**: Upload images to OneDrive and use the "embed" functionality for document image loading
- **Benefits**: Simple, reliable, and cost-effective for low-volume image hosting

## 5. Development Workflow & Conventions

- **Coding Style**: Follow PEP 8 standards, use type annotations, maintain consistency with existing project code style
- **Commits & Version Control**: Follow standard Git workflow with clear, descriptive commit messages
- **Testing**: Core business logic modifications and additions require corresponding `pytest` test cases
- **Communication**: Claude Code will explain plans and request confirmation before executing critical operations (file deletion, major refactoring)

## 6. Project Structure Best Practices

- **`scripts/`**: Core functionality modules only (no test files)
- **`tests/`**: All test files, including those moved from scripts/
- **`config/`**: Configuration files organized by functionality
- **Documentation**: Keep project documentation clear and up-to-date

## 7. Security Practices

- **Environment Variables**: Use `.env` files for sensitive data, exclude from version control
- **Dependencies**: Keep requirements.txt updated and minimal
- **API Keys**: Never commit secrets to the repository

---

This document serves as the guiding principle for all future development work.