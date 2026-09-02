import io

import pytest
from PIL import Image

from app.core.exceptions import ImageValidationError
from app.utils.image_validation import decode_image_safely


def test_decode_rejects_garbage_bytes():
    with pytest.raises(ImageValidationError):
        decode_image_safely(b"definitely not an image")


def test_decode_accepts_valid_png():
    buf = io.BytesIO()
    Image.new("RGB", (8, 8)).save(buf, format="PNG")
    image = decode_image_safely(buf.getvalue())
    assert image.size == (8, 8)
