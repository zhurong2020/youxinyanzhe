# Gemini Agent Project Configuration

This document outlines my understanding of the `workshop` project structure, conventions, and objectives to ensure my contributions are aligned with the existing framework.

## 1. Project Overview

This project is a personal blog built with Jekyll. It includes a sophisticated Python-based content pipeline designed to automate the process of processing markdown articles and publishing them to multiple platforms, with a current focus on WeChat Official Accounts.

## 2. Core Components & Technologies

*   **Static Site Generator**: Jekyll (`_config.yml`, `_posts/`, `_pages/`)
*   **Content Pipeline**: Python (`scripts/`)
    *   **Entry Point**: `run.py`
    *   **Main Orchestrator**: `scripts/content_pipeline.py`
    *   **WeChat Publisher**: `scripts/wechat_publisher.py`
*   **Configuration**: YAML files in `config/` directory (`pipeline_config.yml`, `platforms.yml`).
*   **Dependencies**: `requirements.txt` (Python), `Gemfile` (Ruby/Jekyll).
*   **Testing**: `pytest` framework (`tests/`, `pytest.ini`). Tests for WeChat API functionality are already in place.
*   **Credentials**: Sensitive keys (e.g., for WeChat API, Gemini API) are managed in a `.env` file at the project root.
*   **AI Model**: `gemini-2.5-pro` is used for content processing, configured in `config/gemini_config.yml`.

## 3. Development Workflow

1.  **Drafting**: New articles are created as Markdown files in the `_drafts/` directory.
2.  **Execution**: The `run.py` script is executed to start the pipeline.
3.  **Selection**: The user selects a draft and target platforms (e.g., WeChat).
4.  **Processing**: `ContentPipeline` reads the draft, processes its content (e.g., handling images, formatting HTML).
5.  **Publishing**:
    *   **Current (Legacy) WeChat Flow**: Generates a Markdown guide file in `_output/` for manual copy-pasting.
    *   **Target (New) WeChat Flow**: Will directly use the WeChat API to upload images and content, creating a draft in the WeChat Official Account backend.

## 4. My Directives

*   **Adherence to Conventions**: I will follow the coding style and architectural patterns established in the existing codebase and documented in `CLAUDE.md`.
*   **API Integration**: I will leverage the existing WeChat API logic (validated in the `tests/` directory) to build the new automated publishing feature.
*   **Configuration-Driven**: The new functionality will be controlled via a `publish_mode` setting in `config/platforms.yml` to ensure backward compatibility and safe rollout.
*   **Security**: I will read credentials from the `.env` file but will not display them or include them in any version-controlled files.
