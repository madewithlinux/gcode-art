from PIL import Image
from PIL import ImageColor
from PIL import ImageFilter


def trace_image_dfs(image: Image, num_colors=2):
    im2 = image.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=num_colors)
    im2_edges = im2.convert('RGB').filter(ImageFilter.FIND_EDGES)
    image = im2_edges.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=2)

    line_color = 0
    w, h = image.size

    # find and start from all starting points
    w, h = im.size

    paths = []
    visited = set()

    def dfs_internal(x0: int, y0: int, m_stack: list, m_visited: set):
        """modifies stack and visited arguments"""
        m_visited.add((x0, y0))
        adjacent = []
        for x in range(x0 - 1, x0 + 2):
            for y in range(y0 - 1, y0 + 2):
                pixel = (x, y)

                if x < 0 or y < 0 or x >= w or y >= h:  # skip invalid
                    continue
                if x == x0 and y == y0:  # skip self
                    continue
                if (x, y) in m_visited:  # skip visited
                    continue
                if image.getpixel(pixel) != line_color:  # skip other color
                    continue

                adjacent.append(pixel)

        # prefer closest by absolute distance
        adjacent.sort(key=lambda p: (p[0] - x0) ** 2 + (p[1] - y0) ** 2)

        if len(adjacent) == 0:
            return None
        elif len(adjacent) == 1:
            return adjacent[0]
        else:
            m_stack += adjacent[1:]
            return adjacent[0]

    def dfs(x0, y0, m_paths: list):
        """manages it's own stack"""
        startpixel = (x0, y0)
        stack = [startpixel]
        while len(stack) > 0:
            pixel = stack.pop()
            if pixel in visited:
                continue
            m_paths.append([])  # start new path
            while pixel is not None:
                m_paths[-1].append(pixel)
                x, y = pixel
                pixel = dfs_internal(x, y, stack, visited)

    for x in range(w):
        for y in range(h):
            pixel = (x, y)
            if image.getpixel(pixel) == line_color and pixel not in visited:
                dfs(x, y, paths)

    # filter out single pixel paths
    return list(path for path in paths if len(path) > 1)


def hsv_paths(paths: list, size, filename: str) -> Image:
    im = Image.new('RGB', size, (255, 255, 255))
    pixdata = im.load()

    for path in paths:
        pathlen = len(path)
        for i, p in enumerate(path):
            color_rgb = ImageColor.getrgb(f"hsv({(i / pathlen) * 360:4f}, 100%, 100%)")
            x, y = p
            pixdata[x, y] = color_rgb

    im.save(filename)


if __name__ == '__main__':
    im: Image = Image.open('logo.jpg')

    paths = trace_image_dfs(im)
    print(len(paths))

    hsv_paths(paths, im.size, "hsv_paths.png")
