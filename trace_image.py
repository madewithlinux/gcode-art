# trace_image.py
import subprocess
import json
from math import sin, cos, pi, sqrt, fmod
from PIL import Image
from PIL import ImageOps

from gcode import PolargraphKinematics, CartesianKinematics
from image_kinematics import ImageKinematics


# def potrace(input_fname, output_fname):
#     subprocess.check_call(['potrace', '-s', input_fname, '-o', output_fname])

def potrace_image(input_filename):
    filename_pgm = input_filename + ".pgm"
    filename_json = input_filename + ".json"
    subprocess.check_call(['convert', input_filename, filename_pgm])
    subprocess.check_call(['potrace', '-s', filename_pgm, '-o', filename_json, '-b', 'geojson'])
    with open(filename_json) as json_file:
        data = json.load(json_file)
    return data["features"][0]["geometry"]["coordinates"]

r=70
kinematics = ImageKinematics(
    PolargraphKinematics(
        top_clip_distance=1380,
        wire_length=900,
        max_feedrate=5000,
        max_acceleration=25,
    ),
    1080, 2 * r)

polygons = potrace_image('images/kafka-logo-icon.png')
print(polygons)

# import IPython
# IPython.embed()

x_mean = 0.0
y_mean = 0.0
point_count = 0
for polygon in polygons:
    for x, y in polygon:
        x_mean += x
        y_mean += y
        point_count += 1
x_mean /= point_count
y_mean /= point_count


kinematics.move(0, 0)
scale = 1.0/3

for polygon in polygons:
    for x, y in polygon:
        # print(x,y)
        kinematics.move(
            (x - x_mean)*scale,
            (y - y_mean)*scale
        )


kinematics.to_file("trace_image.g")

