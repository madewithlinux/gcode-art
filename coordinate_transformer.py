from PIL import Image


def transformer_for_image_path_and_width(
        image_filename: str,
        width_mm: float):
    image = Image.open(image_filename)
    return transformer_for_image_size_and_width(image.size, width_mm)

def transformer_for_image_size_and_width(
        image_size: (float, float),
        width_mm: float):
    return CoordinateTransformer(
        image_size[0],
        image_size[1],
        width_mm / image_size[0],
    )



class CoordinateTransformer:
    def __init__(self,
            image_width: int,
            image_height: int,
            mm_per_pixel: float
        ):
        # TODO
        self.image_width: int = image_width
        self.image_height: int = image_height
        self.mm_per_pixel: float = mm_per_pixel

    @property
    def gcode_width(self) -> float:
        return self.image_width * self.mm_per_pixel

    @property
    def gcode_height(self) -> float:
        return self.image_height * self.mm_per_pixel

    def _normalize_image_coordinate(self, pixel: (float, float)) -> (float, float):
        """
        normalize both x and y to [0,1]
        """
        px, py = pixel
        return (
            px / self.image_width,
            1.0 - py / self.image_height,
        )

    def _normalize_gcode_coordinate(self, point: (float, float)) -> (float, float):
        """
        normalize both x and y to [0,1]
        """
        px, py = point
        return (
            px / (self.gcode_width/2) + 0.5,
            py / (self.image_height/2) + 0.5,
        )

    def image_to_gcode(self, pixel: (float, float)) -> (float, float):
        px, py = self._normalize_image_coordinate(pixel)
        # transform to center-origin coordinates on [-0.5,0.5]
        px = px - 0.5
        py = py - 0.5
        # scale
        return (
            px * self.gcode_width,
            py * self.gcode_height,
        )

    def gcode_to_image(self, point: (float, float)) -> (float, float):
        px, py = self._normalize_gcode_coordinate(point)
        # invert y
        py = 1-py
        # scale
        return (
            px * self.image_width,
            py * self.image_height,
        )
