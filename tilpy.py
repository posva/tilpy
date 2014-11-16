#! /usr/bin/env python2

import sys, getopt, json, time, os, re, tempfile, logging
from PIL import Image

# Define logging level
logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.ERROR)
log = logging.getLogger('log')
log.setLevel(logging.ERROR)
# Default values

outFile = ''

# Handle options

def usage():
    print '--help', '\t', 'Print this help'
# tilpy spr0 spr1 out > fusion spr0 and spr1 int out
# tilpy spr0 out -h 10 [-v 10] > split spr0 into out-1, out-2, ..., out-n with n = h * v -> horizontal, vertical splits
# tilpy spr0 out -w 10 [-h 10] > split spr0 into out-1, out-2, ..., out-n using deafult split parameters
# tilpy --split spr0 out1 out-no > split spr0 into the specified images. If no other parameters are given the number of parameters will decide how to split (width/len(outs))
    print '--split', '\t', 'Split instead of join. This mode activates when passing a single input file. Do `%s -sh` or `%s --split --help` (order is important) to get more help about this.'%(sys.argv[0], sys.argv[0])

# Helper functions to parse args
def isPoint(s):
    try:
        tab = [int(i) for i in s.split(',')]
        if len(tab) == 1:
            x = y = tab[0]
        else:
            x, y = tab
    except ValueError:
        return False, False
    return x, y

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Parse them
try:
    opts, args = getopt.getopt(sys.argv[1:],
            'hs:vO:o:',
            ['help', 'verbose', 'out-file=', '', 'offset=', 'split', 'separation='])
except getopt.GetoptError as err:
    # print help information and exit:
        print(err) # will print something like 'option -a not recognized'
        usage()
        sys.exit(2)
for o, a in opts:
    if o in ('--verbose'):
        log.setLevel(logging.INFO)
    elif o in ('--help'):
        usage()
        sys.exit()
    elif o in ('-O', '--out-file'):
        outFile = a
    elif o in ('-o', '--offset'):
        x, y = isPoint(a)
        if not x:
            print 'Invalid offset %s'%a
            sys.exit(2)
        offset = Point(x, y)
    elif o in ('-s', '--separation'):
        x, y = isPoint(a)
        if not x:
            print 'Invalid offset %s'%a
            sys.exit(2)
        separation = Point(x, y)
    else:
        assert False, 'unhandled option'

if len(args) < 1 or (len(args) == 1 and outFile == ''):
    print 'No input files were given! Print help with -h'
    print 'Usage example: %s file1.png file2.png out.png'%sys.argv[0]
    sys.exit(2)

if outFile == '':
    outFile = args[-1]
    args.pop()

# Sprite
# Store information about an image
class Sprite:
    def __init__(self, f):
        self._img = Image.open(f)
        self._w, self._h = self._img.size
        self._area = self._w * self._h
    def __lt__(self, b):
        return self._area < b._area
    def __le__(self, b):
        return self._area <= b._area
    def __ge__(self, b):
        return self._area >= b._area
    def __gt__(self, b):
        return self._area > b._area

    @property
    def area(self):
        return self._area

    @property
    def img(self):
        return self._img

# Generate a spritesheet using an array of sprite or a single spritesheet
class SpriteSheet:
    def __init__(self, images, out):
        self._sprites = map(Sprite, images)
        self._outFile = out
        if len(self._sprites) > 1: # we can build a spritesheet
            self.computeSize()

    def computeSize(self):
        totalArea = sum([s.area for s in self._sprites])
        log.info('Total area: %d'%totalArea)

    def save(self):
        w = 300
        h = self._sprites[0].img.size[1]
        result = Image.new("RGBA", (w, h))
        x = 0
        for i in self._sprites:
            result.paste(i, (x, 0))
            x += i.size[0]


log.info('Loading %d images'%len(args))
ss = SpriteSheet(args, outFile)

ss.save()

log.info('Saving %s'%outFile)
result.save(outFile)
