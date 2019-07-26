# trace_image.py
import subprocess
import json
from PIL import Image

from gcode import PolargraphKinematics, CartesianKinematics
from image_kinematics import ImageKinematics


def potrace_image(input_filename, infill=True):
    polygons = []
    filename_pgm = input_filename + ".pgm"
    filename_json = input_filename + ".json"
    filename_infill_pgm = input_filename + 'infill.pgm'
    filename_infill_json = input_filename + 'infill.json'

    # replace alpha with white
    subprocess.check_call(
        ['convert', '-background', 'white', '-alpha', 'remove', '-alpha', 'off',
         input_filename, filename_pgm])

    # trace outline
    subprocess.check_call(['potrace', '-s', filename_pgm, '-o', filename_json, '-b', 'geojson'])
    with open(filename_json) as json_file:
        trace_data = json.load(json_file)
        for feature in trace_data['features']:
            polygons += feature["geometry"]["coordinates"]

    if not infill:
        return polygons

    im: Image = Image.open(input_filename)
    x, y = im.size
    subprocess.check_call([
        'composite', '-compose', 'Screen',
        filename_pgm,
        '-size',
        f'{x}x{y}',
        # 'tile:pattern:HS_HORIZONTAL',
        'tile:images/half_tile_8px.png',
        filename_infill_pgm,
    ])
    # trace outline
    subprocess.check_call(['potrace', '-s', filename_infill_pgm, '-o', filename_infill_json, '-b', 'geojson'])
    with open(filename_infill_json) as json_file:
        infill_data = json.load(json_file)
        for feature in infill_data['features']:
            polygons += feature["geometry"]["coordinates"]

    return polygons


r = 300
kinematics = ImageKinematics(
    PolargraphKinematics(
        top_clip_distance=1350,
        wire_length=900,
        max_feedrate=5000,
        max_acceleration=25,
    ),
    4096, 2 * r)

polygons = potrace_image('images/kafka-logo.png')
scale = 1.0 / 1

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

kinematics.travel(0, 0)

for polygon in polygons:
    x, y = polygon[0]
    kinematics.travel(
        (x - x_mean) * scale,
        (y - y_mean) * scale
    )
    for x, y in polygon:
        kinematics.move(
            (x - x_mean) * scale,
            (y - y_mean) * scale
        )

kinematics.to_file("trace_image.g")
