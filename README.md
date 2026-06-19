# circles

A small generative art script that draws concentric rings, colored by a
random gradient and finished with a soft neon glow.

## Gallery

![circle 0](https://github.com/masoudqashqai/circles/blob/master/imgs/circle_0.png)
![circle 1](https://github.com/masoudqashqai/circles/blob/master/imgs/circle_1.png)
![circle 2](https://github.com/masoudqashqai/circles/blob/master/imgs/circle_2.png)
![circle 3](https://github.com/masoudqashqai/circles/blob/master/imgs/circle_3.png)
![circle 4](https://github.com/masoudqashqai/circles/blob/master/imgs/circle_4.png)
![circle 5](https://github.com/masoudqashqai/circles/blob/master/imgs/circle_5.png)
![circle 6](https://github.com/masoudqashqai/circles/blob/master/imgs/circle_6.png)
![circle 7](https://github.com/masoudqashqai/circles/blob/master/imgs/circle_7.png)

## How it works

Each image is built from a stack of nested ellipses. Two random colors are
chosen as gradient endpoints, and every ring is given a color interpolated
between them. The rings are drawn at high resolution and additively blended
onto a near-black canvas, a blurred copy is laid underneath as a glow, and the
result is downscaled with LANCZOS resampling for clean, anti-aliased edges.

## Usage

```bash
pip install -r requirements.txt
python main.py
```

### Options

```
-n, --count    number of images to generate (default: 16)
-s, --size     output image size in pixels (default: 256)
-r, --rings    number of rings per image (default: 16)
-o, --out-dir  output directory (default: imgs)
    --seed     random seed for reproducible output
```

Example:

```bash
python main.py --count 8 --size 512 --rings 24 --seed 7
```
