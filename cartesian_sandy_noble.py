from math import sin, cos, pi, sqrt, fmod

from PIL import Image
from PIL import ImageOps

from gcode import PolargraphKinematics, CartesianKinematics
from image_kinematics import ImageKinematics

# TODO support non-square images to preserve aspect ratio

r = 390
pixel_size = 20
line_segment_length = 3  # mm
marker_width = 2

kinematics = ImageKinematics(
    PolargraphKinematics(
        top_clip_distance=870,
        wire_length=650,
        max_feedrate=750,
    ),
    4096, 2 * r)

####
n_pixels = int(2 * r / pixel_size)
max_pixel_lines = pixel_size / marker_width - 1

# draw a bounding box
# C-------B
# |       |
# |   O---A
# |       |
# D-------E
kinematics.move(0, 0)  # O
kinematics.move(r, 0)  # A
kinematics.move(r, r)  # B
kinematics.move(-r, r)  # C
kinematics.move(-r, -r)  # D
kinematics.move(r, -r)  # E
# but start in the top-left corner
kinematics.move(r, r)  # B
kinematics.move(-r, r)  # C

filename = 'logo.png'
im: Image = Image.open(filename)
print('image size: ' + str(im.size))

im = im.convert('L')
im = im.resize((n_pixels, n_pixels))
im = ImageOps.autocontrast(im)
image_width, image_height = im.size
im.save('test.png')


def image_to_gcode_coordinates(xi: int, yi: int):
    x = float(xi)
    y = float(yi)

    x -= image_width / 2
    x /= image_width
    x *= 2 * r

    y = image_height - y
    y -= image_height / 2
    y /= image_height
    y *= 2 * r

    return x, y


for yi in range(n_pixels):
    for xi in range(n_pixels):
        x, y = image_to_gcode_coordinates(xi, yi)

        y_offset = pixel_size / 2 - 1  # padding
        if xi % 2 == 1:
            y_offset *= -1

        scaled_pixel = 1 - im.getpixel((xi, yi)) / 255.0
        num_pixel_waves = int(scaled_pixel * max_pixel_lines)
        if num_pixel_waves == 0:
            x, y = image_to_gcode_coordinates(xi + 1, yi)
            kinematics.move(x, y)
            continue
        pixel_wave_width = pixel_size / num_pixel_waves

        for i in range(num_pixel_waves):
            kinematics.move(x, y + y_offset)
            kinematics.move(x + pixel_wave_width, y + y_offset)
            y_offset *= -1
            x += pixel_wave_width

        x, y = image_to_gcode_coordinates(xi + 1, yi)
        kinematics.move(x, y)

    # move around the border to the next line
    x, y = image_to_gcode_coordinates(image_width, yi)
    kinematics.move(r, y)  # A on current line
    kinematics.move(r, r)  # B
    kinematics.move(-r, r)  # C
    kinematics.move(*image_to_gcode_coordinates(0, yi + 1))  # C on next line

kinematics.to_file("cartesian_sandy_noble.g")
