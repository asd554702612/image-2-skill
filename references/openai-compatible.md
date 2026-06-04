# Gepin AI Image API

This skill uses the Gepin AI image generation API with an OpenAI-compatible request and response shape.

## Environment

- `IMAGE_2_API_KEY`: API key used as `Authorization: Bearer ...`.

## Request

The helper posts JSON to the fixed endpoint:

```text
https://token.gptk.cc.cd/v1/images/generations
```

Payload:

```json
{
  "model": "gpt-image-2",
  "prompt": "image prompt",
  "size": "1024x1024",
  "n": 1,
  "response_format": "b64_json",
  "quality": "low",
  "output_format": "png",
  "stream": false
}
```

## Response

Supported response shapes:

```json
{"data": [{"b64_json": "..."}]}
```

```json
{"data": [{"url": "https://example.com/generated.png"}]}
```

## Size Notes

Use upstream-supported GPT image sizes:

- `1024x1024` for square output.
- `1536x1024` for landscape output.
- `1024x1536` for portrait output.
- `auto` when the upstream should choose.

Do not use `2k`, `4k`, or `3840x2160` for direct generation. Use the supported image sizes above; unsupported sizes can surface as `502 upstream_error`.
