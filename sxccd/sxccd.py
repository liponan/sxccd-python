import json
import time
import os.path as osp

import usb.core

from .sxccd_utils import *


class Camera():

    def __init__(self, idVendor:int = None, idProduct:int = None):
        if idVendor and idProduct:
            self.dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        else:
            self.dev = usb.core.find(manufacturer="Starlight Xpress")
        self.timeout = 1000

    def firmwareVersion(self):
        # get firmware version
        result = self.dev.ctrl_transfer( 0xC0, 255, 0, 0, 4 )
        ver_maj = decLH( result[2:4] )
        ver_min = decLH( result[0:2] )
        print("Firmware version V." + str(ver_maj) + "." + str(ver_min))

    def model(self):
        # get CAMERA MODEL
        result = self.dev.ctrl_transfer( 0xC0, 14, 0, 0, 2 )
        model_id = decLH( result )
        models = json.load( open(osp.join(osp.dirname(osp.abspath(__file__)), "models.json")) )
        try:
            print("Camera model: " + models[str(model_id)])
        except:
            raise("Unknown camera model")

    def parameters(self):
        # get CCD parameters
        result = self.dev.ctrl_transfer(0xC0, 8, 0, 0, 17 )
        params = {}
        params["hfront_porch"] = result[0]
        params["hback_porch"] = result[1]
        params["width"] = decLH( result[2:4] )
        params["vfront_porch"] = result[4]
        params["vback_porch"] = result[5]
        params["height"] = decLH( result[6:8] )
        params["pixel_width"] = decLH( result[8:10] ) / 256.0
        params["pixel_height"] = decLH( result[10:12] ) / 256.0
        params["color_matrix"] = decLH( result[12:14] )
        return params

    def reset(self):
        # RESET
        cmd = b"\xC0\x06\x00\x00\x00\x00\x00\x00"
        result = self.dev.write(0x01, cmd, self.timeout)
        return True

    def echo(self, string="Hello World!"):
        cmd = b"\x40\x00\x00\x00\x00\x00" + dec2bytes(len(string)) \
                + str.encode(string)
        result0 = self.dev.write(0x01, cmd, self.timeout)
        result1 = self.dev.read(0x82, len(string), self.timeout)
        echoed_string =  "".join([chr(c) for c in result1])
        return echoed_string


    def readPixelsDelayed(self, exp_ms, width, height, x_bin=1, y_bin=1,
                            x_offset=0, y_offset=0, verbose=False):
        # assert(exp_ms>0,
        #         "exposure time (in ms) must be larger than zero")
        # assert(exp_ms<65536,
        #         "exposure time (in ms) must be smaller than 6556 (roughly 65.5 sec)")

        params = self.parameters
        # assert(width<=params["width"],
        #         "maximum width " + params["width"] + " pixels")
        # assert(height<=params["height"],
        #         "maximum height " + params["height"] + " pixels")
        #
        # assert(x_offset+width<=params["width"],
        #         "width + x_offset cannot exceed " + params["width"] + " pixels")
        # assert(y_offset+height<=params["height"],
        #         "height + y_offset cannot exceed " + params["height"] + " pixels")

        w = int(width/x_bin)
        h = int(height/y_bin)
        nPixels = w * h
        payload = dec2bytes(x_offset) + dec2bytes(y_offset) \
                    + dec2bytes(width) + dec2bytes(height) \
                    + dec2bytes(x_bin,1) + dec2bytes(y_bin,1) + dec2bytes(exp_ms, 4)
        if verbose:
            print("payload: (" + str(len(payload)) + ")")
            print(payload)
        cmd = b'\x40\x02\x04\x00\x00\x00' + dec2bytes(len(payload)) + payload
        if verbose:
            print("command:")
            print(cmd)
            print("image size: " + str(w) + " x " + str(h))
            print("number of pixels: " + str(nPixels))
        t1 = time.time()
        result0 = self.dev.write(0x01, cmd, self.timeout)
        result1 = self.dev.read(0x82, 2*nPixels, max(2*exp_ms,5*self.timeout))
        t2 = time.time()
        if verbose:
            dt = t2 - t1
            print("exposure and data transfer done in " + str(dt) + " s")

        image = dec2image( result1, h, w )
        return image
