"""
Image packing code from http://www.pygame.org/wiki/ImagePacker?parent=CookBook 
"""

from __future__ import with_statement

import sys
import os, shutil
import Image
import glob
import datetime

try:
    import cStringIO as StringIO
except:
    import StringIO

ASSETS_FOLDER = 'assets'

assetcount = dict(textures=0, graphics=0, fonts=0, sounds=0, musics=0)

def _pack_textures(basedir, fp, config, teximage, width, height, name):
    texinputs = []

    line = fp.readline()
    while line:
        entry = tuple(line.split())
        if entry:
            texinputs.append(entry)
            line = fp.readline()
        else:
            break

    format = 'RGBA'
    size = (width, height)
    images = sorted([ (i.size[0] * i.size[1], gid, i) 
                      for gid, i in ((gid,Image.open(os.path.join(basedir, x)).convert(format)) 
                                      for (gid, x) in texinputs)])
    tree = PackNode(size)
    image = Image.new(format, size)
    graphics = []
    for area, gid, img in images:
        uv = tree.insert(img.size)
        if uv is None: raise ValueError('Pack size too small.')
        graphics.append((gid, uv.area))
        image.paste(img, uv.area)

    image.save(os.path.join(ASSETS_FOLDER, teximage))
    config.write("""\
Texture %s {
    source = %s
}

""" % (name, teximage))
    assetcount['textures'] += 1

    for (graphic, area) in graphics:
        config.write("""\
Graphic %s {
    texture = sprites
    area    = %.0f %.0f %.0f %.0f
}

""" % (graphic, area[0], area[1], area[2] - area[0], area[3] - area[1]))
        assetcount['graphics'] += 1

def _write_font(config, name, font_config, font_image):
    shutil.copy(os.path.join(basedir, font_config), ASSETS_FOLDER)
    shutil.copy(os.path.join(basedir, font_image), ASSETS_FOLDER)
    config.write("""\
Texture %s {
    source = %s
}

Font %s {
    source = %s
    texture = %s
}

""" % (name, font_image, name, font_config, name))
    assetcount['fonts'] += 1

def _write_sound(config, tag, name, path):
    config.write("""\
%s %s {
    source = %s
}
 
""" % (tag, name, path))
    assetcount['sounds' if tag == 'Sound' else 'musics'] += 1

def process_command(fp, basedir, config, command):
    if command[0] == 'TexturePack':
        name = command[1]
        teximage = command[2]
        width = int(command[3])
        height = int(command[4])
        _pack_textures(basedir, fp, config, teximage, width, height, name)
    elif command[0] == 'Font':
        name = command[1]
        font_config = command[2]
        font_image = command[3]
        _write_font(config, name, font_config, font_image)
    elif command[0] == 'Texture':
        name = command[1]
        texture_path = os.path.join(basedir, command[2])
        shutil.copy(texture_path, ASSETS_FOLDER)
    elif command[0] == 'Resource':
        resource_path = os.path.join(basedir, command[1])
        shutil.copy(resource_path, ASSETS_FOLDER)
    elif command[0] == 'Music' or command[0] == 'Sound':
        tag  = command[0]
        name = command[1]
        path = command[2]
        resource_path = os.path.join(basedir, path)
        shutil.copy(resource_path, ASSETS_FOLDER)
        _write_sound(config, tag, name, path)

def assemble(basedir):
    config = StringIO.StringIO()
    config.write("""\
//  Bluegin resource configuration file
//  (Generated by assetpack.py on %s)
//
//  Texture <texture-id> {
//      source = <file path>
//  }
//
//  Graphics <name> {
//      texture = <texture-id>
//      area = <x y width height>
//  }
//  
//  Sound <name> {
//      source = <file path>
//  }
//
//  Music <name> {
//      source = <file path>
//  }
//
""" % str(datetime.datetime.now()))

    inputs = []
    with file(os.path.join(basedir, 'resources.pack')) as fp:
        line = fp.readline()
        while line:
            command = line.split()
            if command:
                process_command(fp, basedir, config, command)
            line = fp.readline()

    with file(os.path.join(ASSETS_FOLDER, 'resources.config'), 'wb') as fp:
        fp.write(config.getvalue())

class PackNode(object):
   """
   Creates an area which can recursively pack other areas of smaller sizes into itself.
   """

   def __init__(self, area):
       #if tuple contains two elements, assume they are width and height, and origin is (0,0)
       if len(area) == 2:
           area = (0,0,area[0],area[1])
       self.area = area

   def __repr__(self):
       return "<%s %s>" % (self.__class__.__name__, str(self.area))

   def get_width(self):
       return self.area[2] - self.area[0]
   width = property(fget=get_width)

   def get_height(self):
       return self.area[3] - self.area[1]
   height = property(fget=get_height)

   def insert(self, area):
       if hasattr(self, 'child'):
           a = self.child[0].insert(area)
           if a is None: return self.child[1].insert(area)
           return a
       area = PackNode(area)
       if area.width <= self.width and area.height <= self.height:
           self.child = [None,None]
           self.child[0] = PackNode((self.area[0]+area.width, self.area[1], self.area[2], self.area[1] + area.height))
           self.child[1] = PackNode((self.area[0], self.area[1]+area.height, self.area[2], self.area[3]))
           return PackNode((self.area[0], self.area[1], self.area[0]+area.width, self.area[1]+area.height))

if __name__ == '__main__':
    basedir = sys.argv[1]
    if os.path.exists(ASSETS_FOLDER):
        shutil.rmtree(ASSETS_FOLDER)
    os.mkdir(ASSETS_FOLDER)
    assemble(basedir)
    # vcpath = os.path.join('vc9', 'BlueGin', 'assets')
    # shutil.rmtree(vcpath)
    # shutil.copytree(ASSETS_FOLDER, vcpath)
    print '%d textures, %d graphics, %d fonts, %d sounds and %d music files written.' % (
            assetcount['textures'], 
            assetcount['graphics'], 
            assetcount['fonts'], 
            assetcount['sounds'], 
            assetcount['musics'])
