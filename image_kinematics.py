from gcode import CartesianKinematics
from PIL import Image
from PIL import ImageStat
from PIL import ImageDraw


class ImageKinematics(CartesianKinematics):
    """writes to an image"""

    def __init__(self, size):
        super(ImageKinematics, self).__init__()
        self.size = size
        self.position = (0, 0)
        self.linewidth = 2  # mm
        self.border = 50
        self.pixels_per_mm = 4
        self.lines = []

    def move(self, x, y):
        super().move(x, y)
        self.lines.append((self.position, (x, y)))
        self.position = (x, y)

    def point_to_image_coordinates(self, p):
        x, y = p
        # TODO transform point
        return x, y

    def to_file(self, filename):
        super(ImageKinematics, self).to_file(filename)
        filename += ".png"
        # TODO write to png file
        im = Image.new('RGB', self.size, (255, 255, 255))
        draw = ImageDraw.Draw(im)
        for p0, p1 in self.lines:
            p0 = self.point_to_image_coordinates(p0)
            p1 = self.point_to_image_coordinates(p1)
            draw.line([p0, p1], fill=(127, 127, 127), width=self.linewidth * self.pixels_per_mm)
        im.save(filename)
