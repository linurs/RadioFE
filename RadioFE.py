#!/usr/bin/python3
"""! @brief RadioFE is a Internet Radio frontend for mplayer."""
##
# @mainpage RadioFE
# @section description_main Description
# A Radio front End for mplayer 
#

##
# @file RadioFE.py
#
# @brief Main file of RadioFE
#
# @section author_doxygen_example Author(s)
# - Created by Urs Lindegger on 2020-10-01
#
# Copyright (c) 2020 www.linurs.org.  All rights reserved. 
#
# @todo  
# - def hello_name(name: str) -> str:
# - speed up pop up window re-size write in queue and then jst resize the last
# - keep aspect ratio of pop up
# - separate radio from tkinter
# - publish on linus tar.gz
# - link to githb und linurs
# - logging versus logger
# - check for mplayer installed not static do it on config file and exit when nothing is 
# - browser and pop up update do not work the same: pop up update opens window, browser update not, what is better?
# - other back end than mplayer
# - bad crash if stream is not valid
# - up/down edit for favorites
# - remove favorites changes channel and therefore must remove pop up picthire (make a change channel methode that is always called)
# - channel up and down avoid adding multiple tabs with the same icy picture in browser
# - character encoding in the console what is it?
# - nicer gui and tkinter alternatives qt, gtk
# - store window sizes and positions
# - do not crash if PIL is notinstalled dev-python/pillow on embedded device without graphical display PIL is not required
# - make more clever if else True false handling in read and write file use a funtion
# - handle pop out window close better remove stuff in memory when close and reopen it clean
# - avoid using self almost everywhere
# - lcdproc to go toward embedded project and encapsulate tkradio from tk. Use ncurses lcdproc to test it on PC before testing LDC hardware, radiofe lecproc client using python library for lcdproc
# - embedded project, ui and network, clock, alarm, mono instead stereo, use web server and not fancy ui to do settings, bluetooth source select (test with parallel port PC, print case for it, elecx)
#

import os
import shutil
import argparse
import logging
import sys

from tkinter import messagebox   
   
from radiofe.tkradio import *

#Version of the program
radioversion="0.0"

#favicon file to seen in window decoration
faviconname=   'favicon.gif'

#directory where the shared files as channel lists and pictures go
share="/usr/share/RadioFE/"

#name of the default picture
defaultpicname='default.png'

if __name__ == "__main__":
      ## manage the command line parameters
    # sets default values to variables and modifies their content according the command line parameter passed
    # additionally it handles the -h and --help command line parameter automatically
    parser = argparse.ArgumentParser(
                                     description='RadioFE - A internet radio frontend for mplayer', 
                                     epilog='urs@linurs.org')
    ## command line option to show the programs version
    parser.add_argument('-v', '--version', action='version', \
    ## version used in command line option to show the programs version
    version='%(prog)s '+radioversion)
    ## command line option to enable debug messages
    parser.add_argument('-d', '--debug',   help="print debug messages",   action='store_true')  

    ## the command line arguments passed
    args = parser.parse_args()      
    
    # Configuring the logger. Levels are DEBUG, INFO, WARNING, ERROR and CRITICAL
    # the parameter filename='example.log' would write it into a file
    logging.basicConfig() # init logging 
    ## The root logger 
    logger = logging.getLogger() 
    if args.debug==True:
        logger.setLevel(logging.DEBUG)    # the level producing debug messagesl
    else:    
        logger.setLevel(logging.WARNING)
    logger.debug('Logging debug messages')
    
    if shutil.which("mplayer")==None:
         logger.error('mplayer not found')
         messagebox.showerror("Error","mplayer not found. Install it")
         exit(1)
         
    if PIL_imported:
         logging.debug('PIL imported')
    else:     
         logging.info('Python Imaging Library not found, install pillow')
        
    bundle_dir = os.path.dirname(os.path.abspath(__file__))   # get the Python environment 
    logging.debug('Bundle dir is '+bundle_dir )
    logging.debug('sys.argv[0] is '+sys.argv[0] )
    logging.debug('sys.executable is '+sys.executable )
    logging.debug('os.getcwd is '+os.getcwd() )
    ## makes that the files are found
    share_dir=bundle_dir
    ## path to favicon picture
    favicon=share_dir+os.sep+faviconname
    if (os. path. isfile(favicon)==False):
        share_dir=share
        logging.debug(favicon+' not found, so try to find it at '+share_dir )
    favicon=share_dir+os.sep+faviconname
    ## path to default
    defaultpic=share_dir+os.sep+defaultpicname
    if (os. path. isfile(favicon)==False):
             logging.error(faviconname+' not found')
             exit()
    logging.debug('Share dir is '+share_dir )   
     
 ## start the application
    radio=tkradio(bundle_dir, share_dir, favicon, defaultpic, radioversion)
    radio.run()
