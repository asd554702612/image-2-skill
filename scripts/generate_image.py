#!/usr/bin/env python3
"""Generate an image with an OpenAI-compatible image endpoint."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1024"
DEFAULT_ENDPOINT = "https://token.gepinkeji.com/v1/images/generations"
PASSTHROUGH_FIELDS = (
    "response_format",
    "quality",
    "background",
    "output_format",
    "moderation",
    "input_fidelity",
    "style",
)
NUMERIC_FIELDS = ("n", "output_compression", "partial_images")


class ImageGenerationError(Exception):
    """Raised when the relay cannot produce a usable image."""


def read_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImageGenerationError(f"缺少必需的环境变量：{name}")
    return value


def request_json(endpoint: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ImageGenerationError(f"Image relay returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ImageGenerationError(f"Could not reach image relay: {exc.reason}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ImageGenerationError("Image relay returned non-JSON response") from exc

    if not isinstance(parsed, dict):
        raise ImageGenerationError("Image relay returned an unexpected JSON response")
    return parsed


def first_image_item(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ImageGenerationError("Image relay response must include data[0]")
    return data[0]


def download_url(url: str) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise ImageGenerationError(f"Could not download generated image: {exc.reason}") from exc


def image_bytes_from_response(response: dict[str, Any]) -> bytes:
    item = first_image_item(response)
    b64_json = item.get("b64_json")
    if isinstance(b64_json, str) and b64_json.strip():
        try:
            return base64.b64decode(b64_json)
        except ValueError as exc:
            raise ImageGenerationError("Image relay returned invalid b64_json") from exc

    url = item.get("url")
    if isinstance(url, str) and url.strip():
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ImageGenerationError("Generated image URL must use http or https")
        return download_url(url)

    raise ImageGenerationError("Image relay must return data[0].b64_json or data[0].url")


def write_image(path: Path, content: bytes) -> Path:
    if not content:
        raise ImageGenerationError("Generated image content is empty")
    output = path.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    return output


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def numeric_value(value: str) -> int | float:
    try:
        parsed = float(value) if "." in value else int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    return parsed


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": DEFAULT_MODEL,
        "prompt": args.prompt,
        "stream": args.stream,
    }

    if args.size:
        payload["size"] = args.size

    for field in PASSTHROUGH_FIELDS:
        value = getattr(args, field)
        if value is not None:
            payload[field] = value

    for field in NUMERIC_FIELDS:
        value = getattr(args, field)
        if value is not None:
            payload[field] = value

    return payload


def sanitized_request_summary(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "endpoint": DEFAULT_ENDPOINT,
        "payload": build_payload(args),
    }


def generate_image(args: argparse.Namespace) -> Path:
    api_key = read_required_env("IMAGE_2_API_KEY")

    payload = build_payload(args)
    response = request_json(DEFAULT_ENDPOINT, api_key, payload)
    image_bytes = image_bytes_from_response(response)
    return write_image(Path(args.output), image_bytes)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an image with the gpt-image-2 model.")
    parser.add_argument("--prompt", required=True, help="Prompt to send to the image model.")
    parser.add_argument("--output", required=True, help="Path where the generated image will be saved.")
    parser.add_argument("--size", default=DEFAULT_SIZE, help=f"Image size, such as 1024x1024, 1536x1024, 1024x1536, or auto. Default: {DEFAULT_SIZE}.")
    parser.add_argument("--stream", action="store_true", help="Request streaming response from the relay.")
    parser.add_argument("--n", type=positive_int, default=1, help="Number of images to generate. Default: 1.")
    parser.add_argument("--response-format", dest="response_format", help="Response format, such as b64_json or url.")
    parser.add_argument("--quality", help="Quality value to pass through, such as low, medium, high, or auto.")
    parser.add_argument("--background", help="Background value to pass through, such as auto, transparent, or opaque.")
    parser.add_argument("--output-format", dest="output_format", help="Output format to pass through, such as png, jpeg, or webp.")
    parser.add_argument("--output-compression", dest="output_compression", type=numeric_value, help="Output compression value to pass through.")
    parser.add_argument("--moderation", help="Moderation strategy to pass through.")
    parser.add_argument("--input-fidelity", dest="input_fidelity", help="Input fidelity value to pass through.")
    parser.add_argument("--style", help="Style value to pass through.")
    parser.add_argument("--partial-images", dest="partial_images", type=numeric_value, help="Streaming partial image count to pass through.")
    parser.add_argument("--print-request", action="store_true", help="Print sanitized request parameters before generating.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.print_request:
        print(json.dumps(sanitized_request_summary(args), ensure_ascii=False, indent=2), file=sys.stderr)
    try:
        output = generate_image(args)
    except ImageGenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
