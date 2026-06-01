#!/usr/bin/env python3
from __future__ import annotations

import base64
import importlib.util
import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_image.py"
spec = importlib.util.spec_from_file_location("generate_image", SCRIPT)
generate_image = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(generate_image)


class GenerateImageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.env = mock.patch.dict(os.environ, {}, clear=True)
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()

    def args(self, output: str) -> Namespace:
        return Namespace(
            prompt="paint a quiet desk lamp",
            output=output,
            size="1024x1024",
            stream=False,
            n=1,
            response_format=None,
            quality=None,
            background=None,
            output_format=None,
            output_compression=None,
            moderation=None,
            input_fidelity=None,
            style=None,
            partial_images=None,
            print_request=False,
        )

    def test_missing_api_key_reports_required_variable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(generate_image.ImageGenerationError, "IMAGE_2_API_KEY"):
                generate_image.generate_image(self.args(str(Path(tmp) / "out.png")))

    def test_writes_b64_json_response_to_output(self) -> None:
        os.environ["IMAGE_2_API_KEY"] = "test-key"
        expected = b"fake-png-bytes"

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out.png"
            with mock.patch.object(
                generate_image,
                "request_json",
                return_value={"data": [{"b64_json": base64.b64encode(expected).decode("ascii")}]},
            ) as request_json:
                result = generate_image.generate_image(self.args(str(output)))

            self.assertEqual(output.resolve(), result)
            self.assertEqual(expected, output.read_bytes())
            request_json.assert_called_once()
            endpoint, api_key, payload = request_json.call_args.args
            self.assertEqual("https://token.gepinkeji.com/v1/images/generations", endpoint)
            self.assertEqual("test-key", api_key)
            self.assertEqual("gpt-image-2", payload["model"])
            self.assertEqual("1024x1024", payload["size"])
            self.assertEqual(1, payload["n"])
            self.assertFalse(payload["stream"])
            self.assertNotIn("response_format", payload)
            self.assertNotIn("output_format", payload)

    def test_build_payload_includes_documented_optional_fields(self) -> None:
        args = self.args("/tmp/out.webp")
        args.size = "1536x1024"
        args.response_format = "b64_json"
        args.quality = "medium"
        args.background = "auto"
        args.output_format = "webp"
        args.output_compression = 80
        args.moderation = "auto"
        args.input_fidelity = "high"
        args.style = "natural"
        args.partial_images = 2

        payload = generate_image.build_payload(args)

        self.assertEqual(
            {
                "model": "gpt-image-2",
                "prompt": "paint a quiet desk lamp",
                "stream": False,
                "size": "1536x1024",
                "response_format": "b64_json",
                "quality": "medium",
                "background": "auto",
                "output_format": "webp",
                "moderation": "auto",
                "input_fidelity": "high",
                "style": "natural",
                "n": 1,
                "output_compression": 80,
                "partial_images": 2,
            },
            payload,
        )

    def test_downloads_url_response_to_output(self) -> None:
        os.environ["IMAGE_2_API_KEY"] = "test-key"
        expected = b"downloaded-image"

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out.png"
            with mock.patch.object(
                generate_image,
                "request_json",
                return_value={"data": [{"url": "https://cdn.example/out.png"}]},
            ), mock.patch.object(generate_image, "download_url", return_value=expected) as download:
                result = generate_image.generate_image(self.args(str(output)))

            self.assertEqual(output.resolve(), result)
            self.assertEqual(expected, output.read_bytes())
            download.assert_called_once_with("https://cdn.example/out.png")

    def test_sanitized_request_summary_excludes_api_key(self) -> None:
        args = self.args("/tmp/out.png")

        summary = generate_image.sanitized_request_summary(args)

        self.assertEqual("https://token.gepinkeji.com/v1/images/generations", summary["endpoint"])
        self.assertEqual("gpt-image-2", summary["payload"]["model"])
        self.assertNotIn("api_key", summary)
        self.assertNotIn("Authorization", str(summary))


if __name__ == "__main__":
    unittest.main()
