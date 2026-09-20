import io

import pytest
from PIL import Image

from vision.processor import ImageProcessor, MAX_IMAGE_BYTES


def test_oversized_bytes_rejected():
    p = ImageProcessor(api_key="k")
    result = p.process_image(b"0" * (MAX_IMAGE_BYTES + 1))
    assert result["success"] is False
    assert result["tags"] == []


def test_failed_caption_is_not_success(monkeypatch):
    p = ImageProcessor(api_key="k")
    monkeypatch.setattr(p, "generate_caption", lambda _i: "Error: Could not process image")
    result = p.process_image(b"x")
    assert result["success"] is False
    assert result["tags"] == []


def test_valid_image_loads():
    buf = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buf, format="PNG")
    assert ImageProcessor(api_key="k")._load_image(buf.getvalue()).width == 10
