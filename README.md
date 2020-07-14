# sxccd-python
Python API for Startlight Xpress CCD (sxccd)

Okay, let's face it. Startlight CCDs ship with a easy-to-use GUI software Startlight Live, which has an infamouse bug: it crashes when the image is too large or exposure time is too long. 
For example, on my Mac BookPro, the longest exposure tiem I can do is 500ms with 2x2 binning.
Not a chance for 1x1 binning even with 1ms exposure time.

I realized that Starlight has a very strict timeout setting, which is presumably 1 second. Once exposure + data transfer time exceeds 1 second, a time out of the USB communication between the software and the CCD occurs.
That's why I never could take a image with exposure time longer than 500ms and/or with 1x1 binning mode.
Speaking of binning, the software also has some bugs with binning, of which I haven't figured out the reason.

## sxccd.py

Here, I implemented some selected functions provided by [SXCCD's USB API](https://www.sxccd.com/developers/sx_usb_prog_ref.txt).

For example:

```
import sxccd

camera = sxccd.Camera()

# print out camera model
camera.model()

# print out firmware version
camera.firmwareVersion()

# retrive current camera parameters
params = camera.parameters()

# reset camera
camera.reset()

# echo
echo_result = camera.echo("Hello world!")
print( echo_result )

# Timed exposure
image = readPixelsDelayed( exp_ms, width, height, x_bin=1, y_bin=1, x_offset=0, y_offset=0, verbose=False)

```

where `exp_ms` is exposure time in ms (1~65535), `width` and `height` are width and height in pixels to be read, respectively, `x_bin` and `y_bin` are bin nubmer for x and y axis, respectively, and `verbose` is the flag for verbose output.

## sxccd_image.py

Looking for automatic exposure? We have you covered. `sxccd_image.py` allows you to perform automatic multi-exposure and saves the images to HDF5 file.

### Usage

```
python sxccd_image.py EXP_TIME [--delay DELAY] [--prefix PREFIX] [--number NUM] [--bin BIN] [--single-image]
```

`EXP_TIME`: exposure time in ms (1~65535)

`DELAY`: delay time in sec before the exposure process starts. Default: 0.

`PREIFX`: prefix of outout filename. Default is `images`. For example, if the exposure time was 10 ms, then the default output filename is `images_000010.h5`.

`NUM`: number of exposures to be performed. Default: 1. 

`BIN`: number of bining. Default: 1.

If `--single` is given, the program saves every single image in `/imgs` dataset in the h5 file. Otherwise the program only saves the averaged image, which can be found under `/avg` dataset.
