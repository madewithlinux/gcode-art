from PIL import Image
from PIL import ImageColor
from PIL import ImageFilter

from gcode import Turtle, PolargraphKinematics, NullKinematics
from image_kinematics import ImageKinematics

from coordinate_transformer import transformer_for_image_size_and_width


def trace_image_dfs(image: Image, num_colors=2):
    im2 = image.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=num_colors)
    im2_edges = im2.convert('RGB').filter(ImageFilter.FIND_EDGES)
    image = im2_edges.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=2)

    line_color = 0
    w, h = image.size

    # find and start from all starting points
    w, h = image.size

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

    paths = optimize_paths(paths)

    # filter out single pixel paths
    return list(path for path in paths if len(path) > 1)


def optimize_paths(paths: list) -> list:
    outpaths = []
    for path in paths:
        # sanity check: can't have a single point or empty path
        if len(path) < 2:
            continue

        changed = True
        while changed:
            path, changed = compact_path_ommit_midpoints(path)

        changed = True
        while changed:
            path, changed = compact_path_ommit_length_two(path)

        outpaths.append(path)

    return outpaths


def compact_path_ommit_midpoints(path: list) -> (list, bool):
    """
    compact adjacent lines
    returns new path
    """
    if len(path) <= 2:
        # can't optimize a path with no midpoints
        return path, False

    outpath = []
    changed = False
    outpath.append(path[0])
    for i in range(len(path) - 2):
        a = path[i]
        b = path[i + 1]
        c = path[i + 2]
        horizontal = a[0] == b[0] and b[0] == c[0]
        vertical = a[1] == b[1] and b[1] == c[1]
        if not (horizontal or vertical):
            outpath.append(b)
        else:
            changed = True
    outpath.append(path[-1])

    return outpath, changed


def compact_path_ommit_length_two(path: list) -> (list, bool):
    """
    removes length-two segments, averaging to middle, to
    hopefully make curves
    returns new path
    """
    if len(path) <= 2:
        # can't optimize a path with no midpoints
        return path, False
    outpath = []
    changed = False

    i = 0
    while i < len(path) - 1:

        a = path[i]
        b = path[i + 1]
        # horizontal = a[0] == b[0]
        # vertical = a[1] == b[1]
        dist2 = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
        if dist2 == 1:
            c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            outpath.append(c)
            i += 1
        else:
            outpath.append(a)

        i += 1

    # make sure we specifically preserve the begin and end points of this path
    if path[0] != outpath[0]:
        outpath = [path[0]] + outpath
    if path[1] != outpath[1]:
        outpath.append(path[-1])

    return outpath, changed


def hsv_paths(paths: list, size, filename: str):
    im = Image.new('RGB', size, (255, 255, 255))
    pixdata = im.load()

    for path in paths:
        pathlen = len(path)
        for i, p in enumerate(path):
            color_rgb = ImageColor.getrgb(f"hsv({(i / pathlen) * 360:4f}, 100%, 100%)")
            x, y = p
            pixdata[x, y] = color_rgb

    im.save(filename)


def image_vector_paths(paths: list, size, filename: str):
    r = max(size) / 2

    # k = ImageKinematics(NullKinematics(), pixels_per_mm=12)
    k = ImageKinematics(
        PolargraphKinematics(
            top_clip_distance=1340,
            wire_length=900,
            max_feedrate=5000,
            max_acceleration=25,
        ),
        pixels_per_mm=2,
        line_thickness_mm=1,
    )
    image_width, image_height = size

    t = transformer_for_image_size_and_width(size, 564)

    def image_to_gcode_coordinates(xi: int, yi: int):
        return t.image_to_gcode((xi, yi))
        # x = float(xi)
        # y = float(yi)

        # x -= image_width / 2

        # y = image_height - y
        # y -= image_height / 2

        # return x, y

    for path in paths:
        k.travel(*image_to_gcode_coordinates(*path[0]))
        for pt in path[1:]:
            k.move(*image_to_gcode_coordinates(*pt))
    k.to_file(filename + ".g")


def image_trace_many_colors(filename):
    foldername = filename + ".d"
    import os
    if not os.path.exists(foldername):
        os.mkdir(foldername)

    im: Image = Image.open(filename)
    # for i in range(2, 10):
    for i in [2]:
        paths = trace_image_dfs(im, num_colors=i)
        filename = f"{foldername}/{i}.png"
        hsv_paths(paths, im.size, filename)
        image_vector_paths(paths, im.size, filename)
        print(filename)


if __name__ == '__main__':
    # im: Image = Image.open('logo.jpg')
    #
    # paths = trace_image_dfs(im)
    # print(len(paths))
    #
    # hsv_paths(paths, im.size, "hsv_paths.png")
    image_trace_many_colors(
        # filename="/home/j0sh/Documents/code/3d_printing/gcode_making_scripts/images/1-Bulbasaur.png")
        filename="images/magikarp_fishbowl2.png")
