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
import json

FRAME_RATE = 15
SCREEN_WIDTH = 1296
SCREEN_HEIGHT = 972

CONFIG_FILE = "config.json"

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

LIST_ISO_VALUE = [
    0,
    100,
    200, 
    320, 
    400, 
    500, 
    640, 
    800,
    1000,
    1200,
    1600
]

BRIGHTNESS_MIN = 0
BRIGHTNESS_MAX = 100

SATURATION_MIN = -100
SATURATION_MAX = 100

CONTRAST_MIN = -100
CONTRAST_MAX = 100

SHARPNESS_MIN = -100
SHARPNESS_MAX = 100

EXPOSURE_COMPENSATION_MIN = -25
EXPOSURE_COMPENSATION_MAX = 25

exposure_index = 2
image_effect_index = 0
awb_index = 1
meter_index = 1
brightness = 50
saturation = 0
iso_index = 0
contrast = 0
sharpness = 0
exposure_compensation = 0

def load_config():

    global exposure_index
    global image_effect_index
    global awb_index
    global meter_index
    global brightness 
    global saturation
    global iso_index
    global contrast
    global sharpness
    global exposure_compensation

    cur_path = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(cur_path, CONFIG_FILE)
    if not os.path.exists(config_file):
        return

    if not os.path.isfile(config_file):
        return

    try:
        json_data = open(config_file).read()
        data = json.loads(json_data)

        exposure_index = data['exposure_index']
        image_effect_index = data['image_effect_index']
        awb_index = data['awb_index']
        meter_index = data['meter_index']
        brightness = data['brightness']
        saturation = data['saturation']
        iso_index = data['iso_index']
        contrast = data['contrast']
        sharpness = data['sharpness']
        exposure_compensation = data['exposure_compensation']

    except Exception:
        pass
    print("Camera params:\n")
    print("Exposure mode: %s \n" % (LIST_EXPOSURE_MODE[exposure_index]))
    print("Image effect: %s \n" % (LIST_IMAGE_EFFECT[image_effect_index]))
    print("Auto-white-balance mode: %s \n" % (LIST_AWB_MODE[awb_index]))
    print("Metering mode: %s \n" % (LIST_METER_MODE[meter_index]))
    print("Brightness: %d \n" % (brightness))
    print("Saturation: %d \n" % (saturation))
    print("Contrast: %d \n" % (contrast))
    print("Sharpness: %d \n" % (sharpness))
    print("Exposure compensation: %d \n" % (exposure_compensation))
    if iso_index == 0:
        print("ISO: auto \n")
    else:
        print("ISO: %d \n" % (LIST_ISO_VALUE[iso_index]))

def save_config():

    cur_path = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(cur_path, CONFIG_FILE)

    with open(config_file, 'w') as outfile:
        data = {
            'exposure_index': exposure_index,
            'image_effect_index': image_effect_index,
            'awb_index': awb_index,
            'meter_index': meter_index,
            'brightness': brightness,
            'saturation': saturation,
            'iso_index': iso_index,
            'contrast': contrast,
            'sharpness': sharpness,
            'exposure_compensation': exposure_compensation,
        }
        json.dump(data, outfile)

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

def change_saturation(isUp):
    global saturation
    if isUp:
        saturation += 1
        if saturation > SATURATION_MAX:
            saturation = SATURATION_MAX
    else:
        saturation -= 1
        if saturation < SATURATION_MIN:
            saturation = SATURATION_MIN

def swith_iso():
    global iso_index
    iso_index += 1
    if iso_index >= len(LIST_ISO_VALUE):
        iso_index = 0

def change_contrast(isUp):
    global contrast
    if isUp:
        contrast += 1
        if contrast > CONTRAST_MAX:
            contrast = CONTRAST_MAX
    else:
        contrast -= 1
        if contrast < CONTRAST_MIN:
            contrast = CONTRAST_MIN

def change_sharpness(isUp):
    global sharpness
    if isUp:
        sharpness += 1
        if sharpness > SHARPNESS_MAX:
            sharpness = SHARPNESS_MAX
    else:
        sharpness -= 1
        if sharpness < SHARPNESS_MIN:
            sharpness = SHARPNESS_MIN


def change_exposure_compensation(isUp):
    global exposure_compensation
    if isUp:
        exposure_compensation += 1
        if exposure_compensation > EXPOSURE_COMPENSATION_MAX:
            exposure_compensation = EXPOSURE_COMPENSATION_MAX
    else:
        exposure_compensation -= 1
        if exposure_compensation < EXPOSURE_COMPENSATION_MIN:
            exposure_compensation = EXPOSURE_COMPENSATION_MIN

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

    load_config()
    sleep(1)

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
            camera.brightness = brightness
            camera.saturation = saturation
            camera.ISO = LIST_ISO_VALUE[iso_index]
            camera.contrast = contrast
            camera.sharpness = sharpness
            camera.exposure_compensation = exposure_compensation

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
                    save_config()
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
                elif ch == 'w':
                    change_saturation(True)
                    camera.annotate_text = 'Saturation: %d' % (saturation)
                    camera.saturation = saturation
                elif ch == 's':
                    change_saturation(False)
                    camera.annotate_text = 'Saturation: %d' % (saturation)
                    camera.saturation = saturation
                elif ch == 'r':
                    swith_iso()
                    if iso_index == 0:
                        camera.annotate_text = 'ISO: %s' % ('auto')
                    else:
                        camera.annotate_text = 'ISO: %d' % (LIST_ISO_VALUE[iso_index])
                    camera.ISO = LIST_ISO_VALUE[iso_index]
                elif ch == 'o':
                    change_contrast(False)
                    camera.annotate_text = 'Contrast: %d' % (contrast)
                    camera.contrast = contrast
                elif ch == 'p':
                    change_contrast(True)
                    camera.annotate_text = 'Contrast: %d' % (contrast)
                    camera.contrast = contrast
                elif ch == 'k':
                    change_sharpness(False)
                    camera.annotate_text = 'Sharpness: %d' % (sharpness)
                    camera.sharpness = sharpness
                elif ch == 'l':
                    change_sharpness(True)
                    camera.annotate_text = 'Sharpness: %d' % (sharpness)
                    camera.sharpness = sharpness
                elif ch == 'h':
                    change_exposure_compensation(False)
                    camera.annotate_text = 'Exposure compensation: %d' % (exposure_compensation)
                    camera.exposure_compensation = exposure_compensation
                elif ch == 'j':
                    change_exposure_compensation(True)
                    camera.annotate_text = 'Exposure compensation: %d' % (exposure_compensation)
                    camera.exposure_compensation = exposure_compensation

    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)


if __name__ == '__main__':
    main()