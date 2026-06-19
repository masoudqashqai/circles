# a generative art script
#
# Draws concentric rings whose colors are interpolated between two random
# endpoints, then additively blends them onto a dark canvas. Everything is
# rendered at a high resolution and downscaled with LANCZOS for smooth,
# anti-aliased edges, plus a soft glow layer underneath each ring.

import argparse
import colorsys
import os
import random

from PIL import Image, ImageDraw, ImageChops, ImageFilter


def random_color():
    """A vivid random RGB color (full saturation + value in HSV)."""
    h = random.random()
    s = v = 1

    float_rgb = colorsys.hsv_to_rgb(h, s, v)
    rgb = [int(i * 255) for i in float_rgb]
    return tuple(rgb)


def interpolate(start_color, end_color, factor: float):
    """Linearly blend between two colors. factor=0 -> start, factor=1 -> end."""
    reciprocal = 1 - factor
    return (
        int(start_color[0] * reciprocal + end_color[0] * factor),
        int(start_color[1] * reciprocal + end_color[1] * factor),
        int(start_color[2] * reciprocal + end_color[2] * factor),
    )


def generator(save_path: str, target_size: int = 256, rings: int = 16):
    # Render at a higher resolution, then shrink down at the end. This is what
    # gives the rings clean, anti-aliased edges instead of jagged pixels.
    scale_factor = 4
    canvas_px = target_size * scale_factor
    padding = 4 * scale_factor
    image_bg_color = (1, 1, 1)

    start_color = random_color()
    end_color = random_color()

    # The two layers we build up: a blurred "glow" and the crisp rings.
    image = Image.new("RGB", (canvas_px, canvas_px), image_bg_color)
    glow = Image.new("RGB", (canvas_px, canvas_px), image_bg_color)
    glow_draw = ImageDraw.Draw(glow)

    # Evenly divide the canvas into `rings` nested ellipses.
    step = (canvas_px - 2 * padding) // (2 * rings)

    for i in range(rings):
        overlay_image = Image.new("RGB", (canvas_px, canvas_px), image_bg_color)
        overlay_draw = ImageDraw.Draw(overlay_image)

        # Position the ring and give the inner rings slightly thicker strokes
        # so the piece has a bit more depth toward the center.
        inset = padding + i * step
        box = (inset, inset, canvas_px - inset, canvas_px - inset)
        width = max(2, (rings - i) // 2) * scale_factor

        circle_color = interpolate(start_color, end_color, random.random())

        overlay_draw.ellipse(box, outline=circle_color, width=width)
        glow_draw.ellipse(box, outline=circle_color, width=width)

        image = ImageChops.add(image, overlay_image)

    # Soft halo: blur the ring layer and add it back underneath the sharp rings.
    glow = glow.filter(ImageFilter.GaussianBlur(radius=scale_factor * 3))
    image = ImageChops.add(image, glow)

    # Downscale to the target size (this is the step the original code dropped).
    image = image.resize((target_size, target_size), resample=Image.Resampling.LANCZOS)
    image.save(save_path)


def main():
    parser = argparse.ArgumentParser(description="Generate concentric-circle art.")
    parser.add_argument("-n", "--count", type=int, default=16,
                        help="number of images to generate (default: 16)")
    parser.add_argument("-s", "--size", type=int, default=256,
                        help="output image size in pixels (default: 256)")
    parser.add_argument("-r", "--rings", type=int, default=16,
                        help="number of rings per image (default: 16)")
    parser.add_argument("-o", "--out-dir", default="imgs",
                        help="output directory (default: imgs)")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed for reproducible output")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    os.makedirs(args.out_dir, exist_ok=True)
    for i in range(args.count):
        path = os.path.join(args.out_dir, f"circle_{i}.png")
        generator(path, target_size=args.size, rings=args.rings)
        print(f"saved {path}")


if __name__ == "__main__":
    main()
