---
name: image-2
description: Use when the user explicitly asks to generate an image with the gpt-image-2 model, including requests that name gpt-image-2 or say to use image-2 for image generation.
---

# Image-2

## Overview

Use this skill only when the user explicitly specifies the `gpt-image-2` model, or asks to use `image-2` as the skill handle, for image generation. Do not use it for generic image requests that do not name `gpt-image-2` or `image-2`.

## Requirements

- `IMAGE_2_API_KEY`: API key for the Gepin AI image generation API.

The Gepin AI image generation endpoint is fixed to `https://token.gepinkeji.com/v1/images/generations`, and the default model is fixed to `gpt-image-2`.

Never hard-code or print API keys. If `IMAGE_2_API_KEY` is missing, ask the user to configure it before generating.

## 如何配置 sk

优先让用户在运行 Codex 的 shell/session 里用环境变量配置一次：

```bash
export IMAGE_2_API_KEY="sk-..."
```

用户配置后，只需要这样使用：

```text
使用 $image-2 生成图片：一只橙色猫咪宇航员，1024x1024，高质量
```

安全规则：

- 不要要求用户把 `sk` 写进 prompt、`SKILL.md`、脚本、测试或任何仓库文件。
- 不要在最终回复里展示 `sk`、`Authorization` header 或完整密钥。
- 缺少 `IMAGE_2_API_KEY` 时，用中文提示用户配置该环境变量。
- 如果用户坚持单次临时传入，可以在命令前临时设置环境变量，但这可能进入 shell history，不作为首选方式：

```bash
IMAGE_2_API_KEY="sk-..." python3 scripts/generate_image.py --prompt "cute cat" --output /absolute/path/to/output.png
```

## Generate an Image

Run the bundled helper from this skill directory:

```bash
python3 scripts/generate_image.py \
  --prompt "a clean product render of a ceramic teapot on a white table" \
  --size 1024x1024 \
  --quality high \
  --print-request \
  --output /absolute/path/to/output.png
```

Optional arguments:

- `--size`: image size, default `1024x1024`; use `1536x1024` for landscape, `1024x1536` for portrait, or `auto` when the upstream should choose.
- `--n`: number of images requested, default `1`.
- `--response-format`: pass through `b64_json` or `url` when needed.
- `--quality`: pass through `low`, `medium`, `high`, or `auto`.
- `--background`: pass through `auto`, `transparent`, or `opaque`.
- `--output-format`: pass through `png`, `jpeg`, or `webp` when needed.
- `--output-compression`, `--moderation`, `--input-fidelity`, `--style`, `--partial-images`: pass-through API parameters.
- `--print-request`: prints a sanitized endpoint and payload summary before generating. It must not include API keys.

Avoid `2k`, `4k`, and `3840x2160` as generation sizes for this API path. Use the supported image sizes listed above; unsupported sizes can return `502 upstream_error`.

The helper posts to an OpenAI-compatible image generation endpoint and supports responses containing either `data[0].b64_json` or `data[0].url`.

## Response Pattern

Always respond to the user in Chinese when using this skill.

After successful generation:

1. 确认图片已使用 `gpt-image-2` 生成。
2. 提供图片绝对路径。
3. 展示“本次请求参数”，列出实际传入 endpoint 和 payload 字段；不要展示 API key、Authorization header 或任何密钥。
4. 展示“其他可选参数”，列出未使用但可按需传入的参数：`n`、`response_format`、`quality`、`background`、`output_format`、`output_compression`、`moderation`、`input_fidelity`、`style`、`partial_images`、`stream`。
5. In Codex App, show the image with Markdown using the absolute path:

```markdown
![Generated image](/absolute/path/to/output.png)
```

Keep the Chinese response concise. Use labels like:

- `图片路径`
- `本次请求参数`
- `其他可选参数`

## Troubleshooting

- Missing `IMAGE_2_API_KEY`: respond in Chinese and tell the user to configure that environment variable.
- HTTP errors: summarize the status code and API response without exposing secrets.
- Unsupported response shape: explain that the API must return `data[0].b64_json` or `data[0].url`.
