class CoordinateTransformer:
    def __init__(self):
        # TODO
        self.image_width: int = 0
        self.image_height: int = 0
        self.gcode_r: float = 0
        self.mm_per_pixel = 0

    def image_to_gcode(self, pixel: (float, float)) -> (float, float):
        px, py = pixel
        # transform to center-origin coordinates
        px = (px - self.image_width / 2) / self.image_width
        py = (self.image_height - py - self.image_height / 2) / self.image_height
        return (
            px * self.mm_per_pixel,
            py * self.mm_per_pixel,
        )
