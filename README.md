# Image-2 Codex Skill

一个用于 Codex 的图片生成 skill，通过 Gepin AI 图片生成 API 调用 `gpt-image-2` 生成图片。

## 固定配置

- Endpoint: `https://token.gepinkeji.com/v1/images/generations`
- Model: `gpt-image-2`
- 用户只需要配置环境变量：`IMAGE_2_API_KEY`

## 安装

克隆仓库后，在仓库目录执行：

```bash
mkdir -p ~/.codex/skills
rm -rf ~/.codex/skills/image-2
cp -R . ~/.codex/skills/image-2
```

安装后重启 Codex，或开启新会话，让 skill 元数据重新加载。

## 配置 Key

```bash
export IMAGE_2_API_KEY="sk-..."
```

不要把真实 key 提交到仓库，也不要写进 prompt 或文档。

## 在 Codex 中使用

```text
使用 $image-2 生成图片：一只橙色猫咪宇航员，1024x1024，高质量
```

横图：

```text
使用 $image-2 生成图片：未来城市夜景海报，横图，高质量
```

竖图：

```text
使用 $image-2 生成图片：未来城市夜景海报，竖图，高质量
```

## 支持尺寸

- `1024x1024`：方图，默认值。
- `1536x1024`：横图。
- `1024x1536`：竖图。
- `auto`：让 API 自动选择。

不要把 `2k`、`4k` 或 `3840x2160` 当作生成尺寸传入；请使用当前 API 支持的尺寸值。

## 更多说明

完整使用说明见 [USAGE.md](USAGE.md)。

## 验证

```bash
python3 -m unittest tests/test_generate_image.py
python3 /Users/mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```
