'''
Basic Picture Viewer
====================

This simple image browser demonstrates the scatter widget. You should
see three framed photographs on a background. You can click and drag
the photos around, or multi-touch to drop a red dot to scale and rotate the
photos.

The photos are loaded from the local images directory, while the background
picture is from the data shipped with kivy in kivy/data/images/background.jpg.
The file pictures.kv describes the interface and the file shadow32.png is
the border to make the images look like framed photographs. Finally,
the file android.txt is used to package the application for use with the
Kivy Launcher Android application.

For Android devices, you can copy/paste this directory into
/sdcard/kivy/pictures on your Android device.

The images in the image directory are from the Internet Archive,
`https://archive.org/details/PublicDomainImages`, and are in the public
domain.

'''

import kivy
kivy.require('1.0.6')
from math import isclose

from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import Metrics
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.utils import platform
from kivy.config import Config

if platform != 'android':
    Config.set('kivy', 'desktop', '1')
    Config.set('graphics', 'fullscreen', 'auto')

Config.set('modules', 'touchring', 'image=touch.png,scale=.1,alpha=1')

class FlatButton(ButtonBehavior, Label):
    text = StringProperty("")


class PopupTrans(Popup):
    pass


class TransparentImage(Image):
    def collide_point(self, x, y, dont_collide_transparent_pixels=False):
        # test widget collision as usual
        collide_widget = super().collide_point(x, y)
        # return as usual if we do not consider transparent pixels or outside of widget space
        if not (collide_widget and dont_collide_transparent_pixels):
            return collide_widget
        # global -> local coords
        x_loc, y_loc = self.to_local(x, y)
        # get normalized image size
        sized_texture_size = self.norm_image_size
        # local coords -> texture coords
        sized_texture_x, sized_texture_y = x_loc - (self.width - sized_texture_size[0])/2, y_loc - (self.height - sized_texture_size[1])/2
        # if we are on the widget but not on the texture -> don't collide
        if sized_texture_x < 0 or sized_texture_y < 0:
            return False
        if sized_texture_x >= sized_texture_size[0] or sized_texture_y >= sized_texture_size[1]:
            return False
        # sized texture -> original texture coords
        x_texture, y_texture = int(sized_texture_x * self.texture.width / sized_texture_size[0]), int(sized_texture_y * self.texture.height / sized_texture_size[1])
        # if we are on the widget but not on the texture -> don't collide
        if x_texture < 0 or y_texture < 0:
            return False
        if x_texture >= self.texture.width or y_texture >= self.texture.height:
            return False
        # calculate pixel index
        pix_index = 4 * (self.texture.width * (self.texture.height - y_texture) + x_texture) + 3
        Logger.info("Pixel Index: {}/{} {}".format(pix_index, len(self.texture.pixels), pix_index >= len(self.texture.pixels) ))
        if pix_index >= len(self.texture.pixels):
            return False
        # get pixel alpha
        pixel = self.texture.pixels[pix_index]
        # if == 0 => transparent -> don't collide
        if pixel == 0:
            return False
        return True


class Picture(Scatter):
    '''Picture is the class that will show the image with a white border and a
    shadow. They are nothing here because almost everything is inside the
    picture.kv. Check the rule named <Picture> inside the file, and you'll see
    how the Picture() is really constructed and used.

    The source property will be the filename to show.
    '''

    source = StringProperty(None)      
    def on_touch_down(self, touch):
        x_loc, y_loc = self.to_local(touch.x,touch.y)
        if not self.collide_point(touch.x,touch.y) or not self.ids['image'].collide_point(x_loc, y_loc, dont_collide_transparent_pixels=True):
            return False
        if touch.is_triple_tap:
            return super().on_touch_down(touch)
        elif touch.is_double_tap:
            # self.scale = 1.0
            # self.pos = touch.x - self.width / 2, touch.y - self.height / 2
            anim = Animation(scale = 0.25,t='in_back',duration=1.1) & Animation(opacity=0,t='in_quart')
            anim.start(self)
            anim.bind(on_complete=lambda a,b: self.safe_delete_me())
            return True
        else:
            return super().on_touch_down(touch)
            
    def safe_delete_me(self):
        if self and self.parent :
            self.parent.clear_widgets([self])
        

class PicturesApp(App):

    def resize(self, wid):
        Logger.info("Window: size"+str(wid.size))
        
    def open_pp(self):
        p = PopupTrans()
        p.open()
        
    def reboot(self):
        import os
        os.system('reboot')
        

    def build(self):

        # the root is created in pictures.kv
        root = self.root

        super().build()

        # get any files into images directory
        curdir = dirname(__file__)
        for filename in glob(join(curdir, 'images', '*')):
            try:
                # load the image
                picture = Picture(source=filename)
                # add to the main field
                root.add_widget(picture)
            except Exception as e:
                Logger.exception('Pictures: Unable to load <%s>' % filename)
        Logger.info("Metrics: {} {} {}".format(str(Metrics.density),str(Metrics.dpi),str(Metrics.dpi_rounded)))

    def on_pause(self):
        return True


if __name__ == '__main__':
    PicturesApp().run()

