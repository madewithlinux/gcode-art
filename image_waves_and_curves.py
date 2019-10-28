from math import sin, cos, pi, sqrt, fmod
from PIL import Image
from PIL import ImageColor
from PIL import ImageFilter
from PIL import ImageOps

from gcode import PolargraphKinematics, CartesianKinematics, Kinematics
from coordinate_transformer import transformer_for_image_size_and_width
from image_kinematics import ImageKinematics

from image_to_waves import image_to_waves
from image_to_curves import trace_image_dfs


def image_vector_paths(k: Kinematics, paths: list, size: (int, int), width: float, filename: str):
    r = max(size) / 2
    image_width, image_height = size
    t = transformer_for_image_size_and_width(size, 564)

    def image_to_gcode_coordinates(xi: int, yi: int):
        return t.image_to_gcode((xi, yi))

    for path in paths:
        k.travel(*image_to_gcode_coordinates(*path[0]))
        for pt in path[1:]:
            k.move(*image_to_gcode_coordinates(*pt))


if __name__ == '__main__':
    line_height = 13  # mm
    r = line_height * 22.5

    kinematics = ImageKinematics(
        PolargraphKinematics(
            top_clip_distance=1340,
            wire_length=900,
            max_feedrate=5000,
            max_acceleration=25,
        ),
        pixels_per_mm=2,
        line_thickness_mm=1,
    )

    filename = 'images/Bulbasaur.png'
    im: Image = Image.open(filename)

    paths = trace_image_dfs(im, num_colors=3)
    image_vector_paths(kinematics, paths, im.size, r*2, filename)

    image_to_waves(im, kinematics, line_height, r)
    kinematics.to_file(f"{filename}.g")
