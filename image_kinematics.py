from gcode import Kinematics
from PIL import Image
from PIL import ImageDraw


class ImageKinematics(Kinematics):
    """writes to an image"""

    def __init__(self, delegate, image_size, print_area_size):
        self.delegate = delegate
        self.image_size = image_size
        self.position = (0, 0)
        self.linewidth = 2  # mm
        self.border = 20
        self.pixels_per_mm = int((self.image_size - 2 * self.border) / print_area_size)
        self.lines = []

    def move(self, x, y):
        self.delegate.move(x, y)
        self.lines.append((self.position, (x, y)))
        self.position = (x, y)

    def point_to_image_coordinates(self, p):
        """assumes origin is in the middle"""
        drawing_area_r = (self.image_size - self.border) / 2
        gcode_max = drawing_area_r / self.pixels_per_mm

        x, y = p

        x /= gcode_max
        x *= drawing_area_r
        x += self.image_size / 2

        y /= gcode_max
        y *= drawing_area_r
        y += self.image_size / 2
        y = self.image_size - y

        return x, y

    @property
    def gcode(self):
        return self.delegate

    def to_file(self, filename):
        """additionally writes image file to filename.png"""
        self.delegate.to_file(filename)
        filename += ".png"
        # TODO write to png file
        im = Image.new('RGB', (self.image_size, self.image_size), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        for p0, p1 in self.lines:
            p0 = self.point_to_image_coordinates(p0)
            p1 = self.point_to_image_coordinates(p1)
            draw.line([p0, p1], fill=(0, 0, 0), width=self.linewidth * self.pixels_per_mm)
        im.save(filename)
