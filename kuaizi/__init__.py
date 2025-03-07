# -*- coding: utf-8 -*-

# Define pixel scale of different surveys, unit = arcsec / pixel
import warnings
from pkg_resources import get_distribution, DistributionNotFound
HSC_pixel_scale = 0.168
DECaLS_pixel_scale = 0.262
Dragonfly_pixel_scale = 2.5
SDSS_pixel_scale = 0.395
CFHT_pixel_scale = 0.186

# Define zeropoint of different surveys
HSC_zeropoint = 27.0
DECaLS_zeropoint = 22.5
SDSS_zeropoint = 22.5
CFHT_zeropoint = 30.0

# Define FWHM seeing of different surveys
HSC_seeing = 0.7
Dragonfly_seeing = 6.0

HSC_binray_mask_dict = {0: 'BAD',
                        1:  'SAT (saturated)',
                        2:  'INTRP (interpolated)',
                        3:  'CR (cosmic ray)',
                        4:  'EDGE (edge of the CCD)',
                        5:  'DETECTED',
                        6:  'DETECTED_NEGATIVE',
                        7:  'SUSPECT (suspicious pixel)',
                        8:  'NO_DATA',
                        9:  'BRIGHT_OBJECT (bright star mask, not available in S18A yet)',
                        10: 'CROSSTALK',
                        11: 'NOT_DEBLENDED (For objects that are too big to run deblender)',
                        12: 'UNMASKEDNAN',
                        13: 'REJECTED',
                        14: 'CLIPPED',
                        15: 'SENSOR_EDGE',
                        16: 'INEXACT_PSF'}

# from . import measure # do not import measure here, it will require scarlet/autograd

warnings.simplefilter('ignore')

__all__ = ["utils", "fitting", "download", "detection",
           "display", "measure", "wavelet", "mock"]
__name__ = 'kuaizi'
__author__ = ['Jiaxuan Li']

from . import utils
from . import display
from . import measure
from . import detection
from .utils import set_env, set_matplotlib

# Version
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
