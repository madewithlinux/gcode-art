from gcode import Kinematics
from PIL import Image
from PIL import ImageDraw


class ImageKinematics(Kinematics):
    """writes to an image"""

    def __init__(self, delegate: Kinematics, *, pixels_per_mm=4, line_thickness=2):
        self.delegate = delegate
        self.position = (0, 0)
        self.linewidth = line_thickness  # mm
        self.border = 20
        self.pixels_per_mm = pixels_per_mm
        self.lines = []

    def move(self, x, y):
        self.delegate.move(x, y)
        self.lines.append((self.position, (x, y)))
        self.position = (x, y)

    def travel(self, x, y):
        self.delegate.travel(x, y)
        self.position = (x, y)

    @property
    def gcode(self):
        return self.delegate.gcode

    def to_file(self, filename):
        """additionally writes image file to filename.png"""
        self.delegate.to_file(filename)
        filename += ".png"
        # TODO write to png file
        size, image_lines = self.get_image_size_and_lines()
        im = Image.new('RGB', size, (255, 255, 255))
        draw = ImageDraw.Draw(im)
        for p0, p1 in image_lines:
            draw.line([p0, p1], fill=(0, 0, 0), width=self.linewidth * self.pixels_per_mm)
        im.save(filename)

    def get_image_size_and_lines(self) -> ((int, int), list):
        """assumes origin is in the middle"""

        max_x = 0
        min_x = 0
        max_y = 0
        min_y = 0
        for line in self.lines:
            for x, y in line:
                max_x = max(max_x, x)
                min_x = min(min_x, x)
                max_y = max(max_y, y)
                min_y = min(min_y, y)

        range_x = max_x - min_x
        range_y = max_y - min_y
        image_w = self.pixels_per_mm * range_x
        image_h = self.pixels_per_mm * range_y

        def gcode_to_image_coordinates(p):
            x, y = p
            return ((x - min_x) / range_x * image_w,
                    image_h - (y - min_y) / range_y * image_h,
                    )

        return ((int(image_w + self.border), int(image_h + self.border)), [(
            gcode_to_image_coordinates(line[0]),
            gcode_to_image_coordinates(line[1]),
        ) for line in self.lines])
