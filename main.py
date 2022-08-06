# a generative art script

from PIL import Image, ImageDraw, ImageChops
import random, colorsys


def random_color():
    h = random.random()
    s = v = 1

    float_rgb = colorsys.hsv_to_rgb(h, s, v)
    rgb = [int(i * 255) for i in float_rgb]
    return tuple(rgb)


def interpolate(start_color, end_color, factor: float):
    reciprocal = 1 - factor
    return (
        int(start_color[0] * reciprocal + end_color[0] * factor),
        int(start_color[1] * reciprocal + end_color[1] * factor),
        int(start_color[2] * reciprocal + end_color[2] * factor)
    )


def generator(save_path: str):
    target_size = 128
    scale_factor = 2
    image_height_px = image_width_px = target_size * scale_factor
    padding = 4 * scale_factor
    image_bg_color = (1, 1, 1)
    start_color = random_color()
    end_color = random_color()

    # create canvas
    image = Image.new("RGB", (image_height_px, image_width_px), image_bg_color)

    for i in range(16):
        overlay_image = Image.new("RGB", (image_height_px, image_width_px), image_bg_color)
        overlay_draw = ImageDraw.Draw(overlay_image)

        factor = random.random()
        # factor = i / 16
        circle_color = interpolate(start_color, end_color, factor)
        overlay_draw.ellipse((0 + (i * 10) + padding,
                              0 + (i * 10) + padding,
                              255 - (i * 10) - padding,
                              255 - (i * 10) - padding),
                             outline=circle_color,
                             width=2)
        image = ImageChops.add(image, overlay_image)

    # save image
    image.resize((target_size, target_size), resample=Image.Resampling.LANCZOS)
    image.save(save_path)


if __name__ == '__main__':
    for i in range(16):
        generator(f"imgs/circle_{i}.png")
