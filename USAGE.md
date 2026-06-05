# Image-2 Skill 使用说明

这个 skill 用于在 Codex 中通过 Gepin AI 图片生成 API 调用 `gpt-image-2` 生成图片。

## 1. 固定配置

- 接口地址：`https://token.gptk.cc.cd/v1/images/generations`
- 模型：`gpt-image-2`
- 用户只需要配置 API Key：`IMAGE_2_API_KEY`

## 2. 安装到 Codex

从 GitHub 克隆仓库后，进入仓库目录：

```bash
git clone <your-github-repo-url>
cd image-2-skill
```

安装到 Codex 的个人 skills 目录：

```bash
mkdir -p ~/.codex/skills
rm -rf ~/.codex/skills/image-2
cp -R . ~/.codex/skills/image-2
```

安装后，Codex 会通过 skill 名称 `$image-2` 使用它。

确认安装文件存在：

```bash
ls ~/.codex/skills/image-2
```

应该能看到：

```text
SKILL.md
USAGE.md
scripts/
agents/
references/
```

如果 Codex 已经打开，安装后建议重启 Codex 或开启新会话，让 skill 元数据重新加载。

## 3. 配置 API Key

在运行 Codex 的 shell/session 中设置：

```bash
export IMAGE_2_API_KEY="sk-..."
```

如果你希望每次打开终端都自动生效，可以写入 shell 配置文件，例如 `~/.zshrc`：

```bash
echo 'export IMAGE_2_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc
```

不要把真实 `sk` 写进 prompt、文档、脚本或仓库文件里。最终回复也不会展示 API key 或 `Authorization` header。

## 4. 在 Codex 中使用

在 Codex 对话里明确点名 `$image-2`，并描述要生成的图片。

方图示例：

```text
使用 $image-2 生成图片：一只橙色猫咪宇航员，1024x1024，高质量
```

横图示例：

```text
使用 $image-2 生成图片：未来城市夜景海报，横图，高质量
```

竖图示例：

```text
使用 $image-2 生成图片：未来城市夜景海报，竖图，高质量
```

更完整的示例：

```text
使用 $image-2 生成图片：一个极简科技产品宣传图，白色干净背景，真实摄影风格。尺寸 1536x1024，quality high，输出到当前目录。
```

Codex 使用该 skill 后，会用中文回复，并包含：

- 图片路径
- 本次请求参数：endpoint 和 payload
- 其他可选参数
- 图片预览

## 5. Codex 会自动做什么

当你说“使用 `$image-2` 生成图片”时，Codex 会：

1. 读取 `IMAGE_2_API_KEY`。
2. 调用固定 endpoint：`https://token.gptk.cc.cd/v1/images/generations`。
3. 使用固定模型：`gpt-image-2`。
4. 根据你的描述选择或传入尺寸、质量等参数。
5. 保存图片到本地路径。
6. 用中文告诉你本次请求参数和可选参数。

Codex 不会在回复里展示 API key。

## 6. 直接运行脚本

在 skill 目录中运行：

```bash
python3 scripts/generate_image.py \
  --prompt "一只橙色猫咪宇航员，浅色背景，贴纸风格" \
  --size 1024x1024 \
  --quality high \
  --print-request \
  --output ./cat-astronaut.png
```

成功后脚本会输出图片的绝对路径。

## 7. 常用尺寸

- `1024x1024`：方图，默认值。
- `1536x1024`：横图。
- `1024x1536`：竖图。
- `auto`：让 API 自动选择。

不要把 `1k`、`2k`、`4k` 或 `3840x2160` 当作生成尺寸传入；请使用当前 API 支持的尺寸值，否则可能返回 `502 upstream_error`。

## 8. 可选参数

- `--quality`：`low`、`medium`、`high`、`auto`。
- `--n`：生成数量，默认 `1`。
- `--response-format`：`b64_json` 或 `url`。
- `--background`：`auto`、`transparent`、`opaque`。
- `--output-format`：`png`、`jpeg`、`webp`。
- `--output-compression`：输出压缩率，数字。
- `--moderation`：审核策略参数。
- `--input-fidelity`：输入保真度参数。
- `--style`：风格参数。
- `--partial-images`：流式部分图片数量，数字。
- `--stream`：请求流式返回。
- `--print-request`：生成前打印脱敏请求参数。

`--print-request` 只会展示 endpoint 和 payload，不会展示 API key。

## 9. 常见问题

### 缺少 API Key

错误：

```text
error: 缺少必需的环境变量：IMAGE_2_API_KEY
```

解决：

```bash
export IMAGE_2_API_KEY="sk-..."
```

### 尺寸值失败

如果 `1k`、`2k`、`4k`、`3840x2160` 返回 `502 upstream_error`，请改用：

- `1536x1024`
- `1024x1536`
- `1024x1024`

### 触发频率限制

如果返回 `rate_limit_exceeded`，说明当前 API 额度或速率限制暂时达到上限。等待一会儿再重试。

### 不想长期设置环境变量

可以单次临时传入，但不推荐，因为可能进入 shell history：

```bash
IMAGE_2_API_KEY="sk-..." python3 scripts/generate_image.py \
  --prompt "cute cat" \
  --output ./cute-cat.png
```

## 10. 更新已安装的 skill

如果你拉取了新版本或修改了本地仓库，需要重新复制到 Codex skills 目录：

```bash
rm -rf ~/.codex/skills/image-2
cp -R . ~/.codex/skills/image-2
```

然后重启 Codex 或开启新会话。
