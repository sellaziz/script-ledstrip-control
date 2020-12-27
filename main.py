#!/usr/bin/env python
"""
Script Ledstrip Control
========
Simple Script for Ledstrip control over bluetooth LE using Bluepy

"""

import sys
import argparse
import logging
import pyautogui
import os

import numpy as np
from ressources.lib.Ledstrip import LedStrip

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger()


class AmbiScript:

    def __init__(self, ledstrip, a1=False, ambi=False,setRGB=False,  R=0,G=0,B=0):
        self.ledstrip = ledstrip
        self.a1       = a1
        self.ambi     = ambi
        self.setRGB   = setRGB
        self.R        = R
        self.G        = G
        self.B        = B
        logging.debug("a1={}, ambi={},setRGB={},  R={},G={},B={}".format(a1, ambi,setRGB,  R,G,B))

    def run(self):
        print("Run")
        if self.setRGB:
            logging.info("Setting RGB to R={} G={} B={}".format(self.R, self.G, self.B))
            self.ledstrip.setRGB(self.R, self.G, self.B)
        elif self.a1:
            logging.info("Setting RGB to dominant color of the Screen")
            self.ambilight(np.array(pyautogui.screenshot()))
        elif self.ambi:
            print("Hit CTRL+C to interrupt the process")
            logging.info("Setting RGB to dominant color of the Screen until stop")
            try:
                while(True):
                    self.ambilight(np.array(pyautogui.screenshot()))
            except KeyboardInterrupt:
                print('Process Interrupted!')
                for filename in [file for file in os.listdir() if file.startswith(".screenshot")]:
                    os.remove(filename)
        logging.info('Disconnecting...')
        self.ledstrip.disconnect()
        

    def ambilight(self, img):
        if self.ledstrip.fade_mode:
            R, G, B = self.figureRGBout(np.array(img))
            logging.info("Sending R={}, G={}, B={}".format(R, G, B))
            self.ledstrip.fadeIntoRGB(R, G, B, self.ledstrip.fade_step)
        else:
            R, G, B = self.bincount_app(np.array(img))
            logging.info("Sending R={}, G={}, B={}".format(R, G, B))
            self.ledstrip.setRGB(R,G,B)
    
    @staticmethod
    def bincount_app(a):
        """Figure out the Dominant color of an Image

        Args:
            a (np.array): image as a numpy array

        Returns:
            tuple(3): value of RGB
        """
        a2D = a.reshape(-1,a.shape[-1])
        col_range = (256, 256, 256) # generically : a2D.max(0)+1
        a1D = np.ravel_multi_index(a2D.T, col_range)
        s=  np.unravel_index(np.bincount(a1D).argmax(), col_range)
        return s[0], s[1], s[2]

    @staticmethod
    def figureRGBout(img, min_val=30):
        """Figure out the Dominant color of an Image and put a minimal value

        Args:
            img (np.array): image as a numpy array

        Returns:
            tuple(3): value of RGB
        """
        a2D = img.reshape(-1,img.shape[-1])
        col_range = (256, 256, 256) # generically : a2D.max(0)+1
        a1D = np.ravel_multi_index(a2D.T, col_range)
        s=  np.unravel_index(np.bincount(a1D).argmax(), col_range)
        R,G,B=s[0], s[1], s[2]
        if (R==0 and G==0 and B==0):
            return min_val,min_val,min_val
        else:
            return R, G, B


def parse_args(argv):
    """
    Argument Parser
    """
    p = argparse.ArgumentParser(description='Simple Script for Ledstrip control over bluetooth LE using Bluepy.')
    p.add_argument('-s', '--set',  default=False, help="set - set RGB value", action="store_true")
    p.add_argument('-val', '--val', nargs=3, default=[0,0,0], help="val - specify RGB value", type=int)
    p.add_argument('-at', '--ambi-oneframe', default=False,
                   help="ambi-oneframe - adapt color for one frame", action="store_true")
    p.add_argument('-a', '--ambilight', default=False,
                   help="ambilight - adapt color to the dominant color of the screen", action="store_true")
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    args = p.parse_args(argv)
    return args


def set_log_info():
    """set logger level to INFO"""
    set_log_level_format(logging.INFO,
                         '%(asctime)s %(levelname)s:%(name)s:%(message)s')


def set_log_debug():
    """set logger level to DEBUG, and debug-level output format"""
    set_log_level_format(
        logging.DEBUG,
        "%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - "
        "%(name)s.%(funcName)s() ] %(message)s"
    )


def set_log_level_format(level, format):
    """
    Set logger level and format.
    :param level: logging level; see the :py:mod:`logging` constants.
    :type level: int
    :param format: logging formatter format string
    :type format: str
    """
    formatter = logging.Formatter(fmt=format)
    logger.handlers[0].setFormatter(formatter)
    logger.setLevel(level)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    # set logging level
    if args.verbose > 1:
        set_log_debug()
    elif args.verbose == 1:
        set_log_info()
    myledstrip = LedStrip()
    script = AmbiScript(ledstrip=myledstrip, a1=args.ambi_oneframe, ambi=args.ambilight,setRGB=(args.set),  R=args.val[0],G=args.val[1],B=args.val[2])
    script.run()