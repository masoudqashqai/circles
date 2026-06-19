# a generative art script
#
# Draws concentric rings whose colors are interpolated between two random
# endpoints, then additively blends them onto a dark canvas. Everything is
# rendered at a high resolution and downscaled with LANCZOS for smooth,
# anti-aliased edges, plus a soft glow layer underneath each ring.

import argparse
import colorsys
import math
import os
import random

from PIL import Image, ImageDraw, ImageChops, ImageFilter


def random_color():
    """A cool, spacey random RGB color.

    Hues are kept in the cyan -> blue -> violet -> magenta range so the
    palette reads like deep space / a nebula rather than a rainbow.
    """
    h = random.uniform(0.5, 0.85)
    s = random.uniform(0.55, 0.9)
    v = random.uniform(0.75, 1.0)

    float_rgb = colorsys.hsv_to_rgb(h, s, v)
    rgb = [int(i * 255) for i in float_rgb]
    return tuple(rgb)


def make_background(canvas_px: int, tints):
    """Dark navy canvas with a soft color nebula and a scattering of stars.

    The nebula is painted as a handful of big, overlapping blobs in colors
    drawn from this image's own gradient, then blurred into soft clouds so the
    background stays cohesive with the rings on top of it.
    """
    bg = Image.new("RGB", (canvas_px, canvas_px), (3, 5, 16))

    # --- nebula: blurred color clouds ---
    nebula = Image.new("RGB", (canvas_px, canvas_px), (0, 0, 0))
    nebula_draw = ImageDraw.Draw(nebula)
    for _ in range(12):
        tint = interpolate(tints[0], tints[1], random.random())
        cx = random.randint(0, canvas_px)
        cy = random.randint(0, canvas_px)
        r = random.randint(canvas_px // 5, canvas_px // 2)
        nebula_draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tint)
    nebula = nebula.filter(ImageFilter.GaussianBlur(radius=canvas_px // 8))
    bg = ImageChops.add(bg, nebula, scale=4)  # scale>1 keeps the cloud faint

    # --- stars ---
    draw = ImageDraw.Draw(bg)
    star_count = canvas_px // 10
    for _ in range(star_count):
        x = random.randint(0, canvas_px - 1)
        y = random.randint(0, canvas_px - 1)
        b = random.randint(40, 180)
        size = random.choice((1, 1, 2))
        draw.ellipse((x, y, x + size, y + size), fill=(b, b, min(255, b + 30)))
    return bg


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

    start_color = random_color()
    end_color = random_color()

    # Starry nebula background, plus separate black layers for the crisp rings
    # and their glow (kept black so the blur stays clean before compositing).
    image = make_background(canvas_px, (start_color, end_color))
    rings_layer = Image.new("RGB", (canvas_px, canvas_px), (0, 0, 0))
    rings_draw = ImageDraw.Draw(rings_layer)
    glow = Image.new("RGB", (canvas_px, canvas_px), (0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    # Drift the ring centers along one random direction, more for the inner
    # rings, so the nested circles lean into a 3D tunnel / wormhole.
    angle = random.uniform(0, 2 * math.pi)
    drift = canvas_px * random.uniform(0.04, 0.11)
    dx, dy = drift * math.cos(angle), drift * math.sin(angle)
    center = canvas_px / 2

    # Evenly divide the canvas into `rings` nested ellipses.
    step = (canvas_px - 2 * padding) // (2 * rings)

    cx = cy = center
    for i in range(rings):
        # Inner rings sit smaller and are nudged along the drift direction.
        radius = center - (padding + i * step)
        t = i / max(1, rings - 1)
        cx = center + dx * t
        cy = center + dy * t
        box = (cx - radius, cy - radius, cx + radius, cy + radius)

        # Slightly thicker strokes toward the center for depth.
        width = max(2, (rings - i) // 2) * scale_factor
        circle_color = interpolate(start_color, end_color, random.random())

        rings_draw.ellipse(box, outline=circle_color, width=width)
        glow_draw.ellipse(box, outline=circle_color, width=width)

    # A bright core glowing at the tunnel's vanishing point.
    core_r = step * 1.2
    core = interpolate(interpolate(start_color, end_color, 0.5), (255, 255, 255), 0.6)
    rings_draw.ellipse((cx - core_r, cy - core_r, cx + core_r, cy + core_r), fill=core)
    glow_draw.ellipse((cx - core_r * 2, cy - core_r * 2,
                       cx + core_r * 2, cy + core_r * 2), fill=core)

    # Composite: nebula+stars -> soft halo (subtle) -> crisp rings on top.
    glow = glow.filter(ImageFilter.GaussianBlur(radius=scale_factor * 2))
    image = ImageChops.add(image, glow, scale=2.2)  # scale>1 dims the glow
    image = ImageChops.add(image, rings_layer)

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
