from __future__ import division
from PIL import Image
import os
from pprint import pprint
import numpy

red = (249, 24, 0)

directory = os.path.dirname(os.path.realpath(__file__))
infile = os.path.join(directory, 'Input', 'OdEct.png')

def color_separator(im):
    if im.getpalette():
        im = im.convert('RGB')

    colors = im.getcolors()
    width, height = im.size
    colors_dict = dict((val[1],Image.new('RGB', (width, height), (0,0,0)))
                        for val in colors)
    pix = im.load()
    for i in xrange(width):
        for j in xrange(height):
            colors_dict[pix[i,j]].putpixel((i,j), pix[i,j])
    return colors_dict

def find_height(infile):

    # im = Image.open(infile)
    colors_dict = color_separator(infile)
    # pprint(colors_dict)
    out = colors_dict[red]
    out.show()

    pixels = list(out.getdata())
    width, height = infile.size
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]

    first = next(row for row in pixels if row.__contains__(red))
    top = pixels.index(first)
    print "first @", top

    pixels.reverse()
    last = next(row for row in pixels if row.__contains__(red))
    bot = pixels.index(last)
    print "last @", bot

    return bot- top, (bot - top) / height

def pixel_write(infile, temp):

    im = Image.open(infile).convert("L")
    im.save(temp)
    im = Image.open(temp).convert("RGB")
    # box = (126, 132, 158, 133)  # (126, 132, 161, 200)
    pixels = im.load()  # create the pixel map

    for i in range(127, 161):
        for j in range(132, 134):
            pixels[i, j] = red

    # for i in range(img.size[0]):  # for every pixel:
    #     for j in range(img.size[1]):
    #         pixels[i, j] = (i, j, i%(j+1))  # set the colour accordingly

    return im

if __name__ == '__main__':
    directory = os.path.dirname(os.path.realpath(__file__))
    infile = os.path.join(directory, 'Input', 'IMG_0942.jpg')
    temp = os.path.join(directory, 'Input', 'temp.jpg')

    out = pixel_write(infile, temp).rotate(-90)
    out.show()
    print find_height(out)
