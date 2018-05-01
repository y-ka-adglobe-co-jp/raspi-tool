#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import picamera
from time import sleep
import termios
import itertools
import tty, sys
import datetime as dt
import os

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

LIST_AWB_MODE = [
    'off',
    'auto',
    'sunlight',
    'cloudy',
    'shade',
    'tungsten',
    'fluorescent',
    'incandescent',
    'flash',
    'horizon'
]

LIST_METER_MODE = [
    'average',
    'spot',
    'backlit',
    'matrix'
]

BRIGHTNESS_MIN = 0
BRIGHTNESS_MAX = 100

exposure_index = 2
image_effect_index = 0
awb_index = 1
meter_index = 1
brightness = 50

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

def swith_awb():
    global awb_index
    awb_index += 1
    if awb_index >= len(LIST_AWB_MODE):
        awb_index = 0

def swith_meter():
    global meter_index
    meter_index += 1
    if meter_index >= len(LIST_METER_MODE):
        meter_index = 0

def change_brightness(isUp):
    global brightness
    if isUp:
        brightness += 1
        if brightness > BRIGHTNESS_MAX:
            brightness = BRIGHTNESS_MAX
    else:
        brightness -= 1
        if brightness < BRIGHTNESS_MIN:
            brightness = BRIGHTNESS_MIN


def main():
    ap = argparse.ArgumentParser(description = "Camera tool for Raspberry pi")
    ap.add_argument("-p", "--path", required = True, help = "Captured image directory")

    args = vars(ap.parse_args())
    path = os.path.normpath(args["path"])

    if not os.path.exists(path):
        sys.stderr.write(path + ' is not exist.\n')
        sys.exit(1)

    if not os.path.isdir(path):
        sys.stderr.write(path + ' is not a valid directory.\n')
        sys.exit(1)


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
            camera.video_stabilization = False
            camera.exposure_mode = LIST_EXPOSURE_MODE[exposure_index]
            camera.image_effect = 'none'
            camera.awb_mode = LIST_AWB_MODE[awb_index]
            camera.meter_mode = LIST_METER_MODE[meter_index]

            camera.sharpness = 0
            camera.contrast = 0
            camera.brightness = 50
            camera.saturation = 0
            camera.ISO = 0
            camera.exposure_compensation = 0

            camera.resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)

            camera.start_preview()

            tty.setcbreak(sys.stdin.fileno())
            while 1:
                ch = sys.stdin.read(1).lower()
                if ch == ' ':
                    Time_String = dt.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                    ImageName = os.path.join(path, 'image' + Time_String + '.jpg')
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
                elif ch == 'b':
                    swith_awb()
                    camera.annotate_text = 'Auto-white-balance mode: %s' % (LIST_AWB_MODE[awb_index])
                    camera.awb_mode = LIST_AWB_MODE[awb_index]
                elif ch == 'm':
                    swith_meter()
                    camera.annotate_text = 'Metering mode: %s' % (LIST_METER_MODE[meter_index])
                    camera.meter_mode = LIST_METER_MODE[meter_index]
                elif ch == 'a':
                    change_brightness(False)
                    camera.annotate_text = 'Brightness: %d' % (brightness)
                    camera.brightness = brightness
                elif ch == 'd':
                    change_brightness(True)
                    camera.annotate_text = 'Brightness: %d' % (brightness)
                    camera.brightness = brightness

    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)


if __name__ == '__main__':
    main()