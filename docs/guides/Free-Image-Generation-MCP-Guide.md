# 免费图片生成 MCP 服务器完全指南

> 为长期博客创作选择最适合的图片生成工具

---

## 推荐方案对比

| MCP 服务 | 免费额度 | 需要 API Key | 图片质量 | 推荐场景 |
|---------|---------|-------------|---------|---------|
| **Pollinations** | **完全免费，无限制** | 否 | ★★★★ | 日常博客配图（首选） |
| **Nano Banana (Gemini)** | 每日 2-3 张 | 是（免费） | ★★★★★ | 高质量商业图片 |
| **Stability AI** | 25 免费积分 | 是（免费） | ★★★★★ | 专业设计 |
| **本地 Stable Diffusion** | 无限（自有硬件） | 否 | ★★★★ | 大量生成 |
| **Freepik** | 有限免费 | 是 | ★★★★ | 素材搜索+生成 |

---

## 方案一：Pollinations MCP（强烈推荐）

### 为什么推荐？

- **完全免费**：无订阅、无 API Key、无隐藏成本
- **无限使用**：每月服务 2000 万张图片
- **无需注册**：开箱即用
- **隐私保护**：不存储用户数据

### 安装方法

#### Claude Code 一键安装

```bash
claude mcp add-json "mcpollinations" '{"command":"npx","args":["@pinkpixel/mcpollinations"]}'
```

#### 手动配置（Claude Code）

在 `~/.claude.json` 或项目目录下的 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "pollinations": {
      "command": "npx",
      "args": ["@pinkpixel/mcpollinations"]
    }
  }
}
```

#### Cursor 配置

在 `~/.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "pollinations": {
      "command": "npx",
      "args": ["@pinkpixel/mcpollinations"]
    }
  }
}
```

### 可用工具

| 工具 | 功能 |
|------|------|
| `generateImage` | 生成图片，返回 base64 并保存文件 |
| `respondAudio` | 生成语音 |
| `respondText` | 文本生成 |
| `listImageModels` | 列出可用模型 |

### 直接 URL 生成（无需 MCP）

你也可以直接通过 URL 生成图片：

```
https://image.pollinations.ai/prompt/YOUR_PROMPT?width=1200&height=675
```

示例：
```
https://image.pollinations.ai/prompt/A_minimalist_infographic_about_investment_DCA_strategy_blue_and_gold_colors?width=1200&height=675
```

---

## 方案二：Nano Banana MCP（Google Gemini）

### 特点

- 高质量文字渲染（约 95% 准确率）
- 支持实时数据（Google 搜索集成）
- 最高 4K 分辨率

### 配置方法

```json
{
  "mcpServers": {
    "nano-banana": {
      "command": "npx",
      "args": ["nano-banana-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 获取免费 API Key

https://aistudio.google.com/app/apikey

### 限制

- 免费版每日约 2-3 张图片
- 有每分钟速率限制

---

## 方案三：Stability AI MCP

### 特点

- 基于 Stable Diffusion 最新模型
- 支持生成、编辑、放大
- 专业级图片质量

### 安装

```bash
npm install -g @tadasant/mcp-server-stability-ai
```

### 配置

```json
{
  "mcpServers": {
    "stability-ai": {
      "command": "npx",
      "args": ["@tadasant/mcp-server-stability-ai"],
      "env": {
        "STABILITY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 获取免费积分

1. 注册 https://platform.stability.ai
2. 获得 **25 免费积分**
3. 之后 $0.01/积分，3 积分 = 1 张图片

---

## 方案四：本地 Stable Diffusion MCP

### 适合场景

- 有 NVIDIA GPU（建议 8GB+ 显存）
- 需要大量生成图片
- 追求完全隐私

### 前置要求

1. 安装 [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
2. 启动时添加 `--api` 参数

### 配置

```json
{
  "mcpServers": {
    "sd-local": {
      "command": "npx",
      "args": ["image-gen-mcp"],
      "env": {
        "SD_WEBUI_URL": "http://localhost:7860",
        "SD_OUTPUT_DIR": "./generated-images"
      }
    }
  }
}
```

---

## 方案五：Freepik MCP

### 特点

- 素材搜索 + AI 生成
- 高质量设计素材
- 商业授权友好

### 配置

```json
{
  "mcpServers": {
    "freepik": {
      "command": "npx",
      "args": ["@mcerqua/freepik-mcp"],
      "env": {
        "FREEPIK_API_KEY": "your-api-key"
      }
    }
  }
}
```

---

## 博客创作推荐工作流

### 日常配图（推荐）

```
1. 首选 Pollinations（免费无限）
2. 需要文字渲染时用 Nano Banana
3. 需要高质量素材时用 Freepik
```

### 配置示例（多服务并存）

```json
{
  "mcpServers": {
    "pollinations": {
      "command": "npx",
      "args": ["@pinkpixel/mcpollinations"]
    },
    "nano-banana": {
      "command": "npx",
      "args": ["nano-banana-mcp"],
      "env": {
        "GEMINI_API_KEY": "AIzaSy..."
      }
    }
  }
}
```

---

## 各服务优缺点详解

### Pollinations

**优点**：
- 完全免费，无配额限制
- 无需注册和 API Key
- 支持多种模型（Flux、Stable Diffusion 等）
- 开源，隐私友好

**缺点**：
- 文字渲染能力一般
- 高峰期可能较慢
- 图片质量略逊于付费服务

### Nano Banana (Gemini)

**优点**：
- 业界领先的文字渲染（95%+准确率）
- 支持实时数据集成
- 推理能力强，理解复杂提示词

**缺点**：
- 免费配额极少（每日 2-3 张）
- 有严格的速率限制
- 安全过滤较严格

### Stability AI

**优点**：
- 专业级图片质量
- 支持编辑和放大
- 定价合理

**缺点**：
- 免费积分有限（25 积分）
- 需要注册和 API Key

### 本地 Stable Diffusion

**优点**：
- 完全免费（除电费）
- 无任何限制
- 完全隐私

**缺点**：
- 需要高配置 GPU
- 安装配置复杂
- 需要自己管理模型

---

## 快速开始

### 第一步：安装 Pollinations（免费无限）

```bash
# Claude Code
claude mcp add-json "pollinations" '{"command":"npx","args":["@pinkpixel/mcpollinations"]}'

# 重启 Claude Code
```

### 第二步：测试生成

在 Claude Code 中输入：
```
请使用 pollinations 生成一张金融主题的信息图，
主题是定投策略，使用蓝色和金色，16:9 横版
```

### 第三步：添加 Nano Banana（高质量文字）

```bash
# 获取 API Key: https://aistudio.google.com/app/apikey

claude mcp add-json "nano-banana" '{"command":"npx","args":["nano-banana-mcp"],"env":{"GEMINI_API_KEY":"your-key"}}'
```

---

## Sources

- [MCPollinations - GitHub](https://github.com/pinkpixel-dev/mcpollinations)
- [Pollinations Official](https://pollinations.ai/)
- [Nano Banana MCP - GitHub](https://github.com/ConechoAI/Nano-Banana-MCP)
- [Stability AI MCP - GitHub](https://github.com/tadasant/mcp-server-stability-ai)
- [Stable Diffusion MCP - GitHub](https://github.com/Ichigo3766/image-gen-mcp)
- [Freepik MCP](https://playbooks.com/mcp/mcerqua-freepik)
- [AI Image Gen MCP](https://lobehub.com/mcp/krystian-ai-ai-image-gen-mcp)
