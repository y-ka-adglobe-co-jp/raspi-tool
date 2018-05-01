#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import picamera
from time import sleep
import termios
import itertools
import tty, sys
import datetime as dt

FRAME_RATE = 15
SCREEN_WIDTH = 1296
SCREEN_HEIGHT = 972

LIST_EXPOSURE_MODE = ['off', 'auto', 'night', 'backlight']
LIST_IMAGE_EFFECT = [
    'none',
    'negative',
    'solarize',
    'sketch',
    'denoise',
    'emboss',
    'oilpaint',
    'hatch',
    'gpen',
    'pastel',
    'watercolor',
    'film',
    'blur',
    'saturation',
    'colorswap',
    'washedout',
    'posterise',
    'colorpoint',
    'colorbalance',
    'cartoon',
    'deinterlace1',
    'deinterlace2'
]
exposure_index = 2
image_effect_index = 0

def swith_exposure():
    global exposure_index
    exposure_index += 1
    if exposure_index >= len(LIST_EXPOSURE_MODE):
        exposure_index = 0

def swith_image_effect():
    global image_effect_index
    image_effect_index += 1
    if image_effect_index >= len(LIST_IMAGE_EFFECT):
        image_effect_index = 0

def main():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        with picamera.PiCamera() as camera:
            camera.framerate = FRAME_RATE
            camera.vflip = True
            camera.hflip = True
            camera.rotation = 0
            camera.crop = (0.0, 0.0, 1.0, 1.0)
            camera.color_effects = None
            camera.exposure_mode = LIST_EXPOSURE_MODE[exposure_index]
            camera.image_effect = 'none'

            camera.sharpness = 0
            camera.contrast = 0
            camera.brightness = 50
            camera.saturation = 0
            camera.ISO = 0
            camera.video_stabilization = False
            camera.exposure_compensation = 0
            camera.meter_mode = 'average'
            camera.awb_mode = 'auto'

            camera.resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)

            camera.start_preview()

            tty.setcbreak(sys.stdin.fileno())
            while 1:
                ch = sys.stdin.read(1)
                if ch == ' ':
                    Time_String = dt.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                    ImageName = './photos/image' + Time_String + '.jpg'
                    camera.capture(ImageName)
                    camera.annotate_text = 'Captured'
                    sleep(1)
                elif ch == 'q':
                    camera.stop_preview()
                    camera.close()
                    exit(0)
                elif ch == 'e':
                    swith_exposure()
                    camera.annotate_text = 'Exposure_mode: %s' % (LIST_EXPOSURE_MODE[exposure_index])
                    camera.exposure_mode = LIST_EXPOSURE_MODE[exposure_index]
                elif ch == 'i':
                    swith_image_effect()
                    camera.annotate_text = 'Image effect: %s' % (LIST_IMAGE_EFFECT[image_effect_index])
                    camera.image_effect = LIST_IMAGE_EFFECT[image_effect_index]

    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)


if __name__ == '__main__':
    main()