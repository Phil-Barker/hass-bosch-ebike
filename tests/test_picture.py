"""Test scaling the bike picture for round entity pictures."""
import io

from PIL import Image

from custom_components.bosch_ebike.picture import (
    PICTURE_FILL,
    fit_picture_in_circle,
    picture_path,
)


def make_png(width, height, box):
    """Create a transparent PNG with an opaque rectangle at box."""
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    image.paste((255, 0, 0, 255), box)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_fit_picture_in_circle():
    """Test that a wide picture is trimmed, centered and fits the circle."""
    # Wide bike picture with transparent margins, like the Bosch CDN images
    data = make_png(2013, 1080, (100, 50, 1900, 1050))

    with Image.open(io.BytesIO(fit_picture_in_circle(data, size=256))) as result:
        assert result.size == (256, 256)
        assert result.mode == "RGBA"

        left, top, right, bottom = result.getchannel("A").getbbox()

    width, height = right - left, bottom - top
    # Aspect ratio of the opaque content is kept
    assert abs(width / height - 1800 / 1000) < 0.05
    # Content diagonal fits inside the circle
    assert (width**2 + height**2) ** 0.5 <= 256 * PICTURE_FILL + 2
    # Content is centered
    assert abs((left + right) / 2 - 128) <= 1
    assert abs((top + bottom) / 2 - 128) <= 1


def test_fit_picture_in_circle_without_alpha():
    """Test that pictures without transparency are handled."""
    image = Image.new("RGB", (400, 200), (255, 255, 255))
    output = io.BytesIO()
    image.save(output, format="JPEG")

    with Image.open(io.BytesIO(fit_picture_in_circle(output.getvalue(), size=64))) as result:
        assert result.size == (64, 64)


def test_picture_path_changes_with_source():
    """Test that the local URL changes when the Bosch picture changes."""
    first = picture_path("bike-1", "https://cdn.example/a.png")
    second = picture_path("bike-1", "https://cdn.example/b.png")

    assert first.startswith("/api/bosch_ebike/picture/bike-1?v=")
    assert first != second
    assert first == picture_path("bike-1", "https://cdn.example/a.png")
