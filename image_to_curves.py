from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter


im: Image = Image.open('logo.jpg')

w, h = im.size

pixels = set()
for x in range(w):
    for y in range(h):
        pixels.add(im.getpixel((x,y)))

print(pixels)

im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=2)
im2.save("logo2.png", "PNG")

im2.convert('RGB').filter(ImageFilter.FIND_EDGES).save("logo_edges.png", "PNG")
