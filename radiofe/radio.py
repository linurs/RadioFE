import os
import logging

from radiofe.Channel import *
from radiofe.Channels import *

#string used in config file for character decoding
str_alt_decode="alt_decode"  

#string used in config file for the mplayer commend
str_mplayer_cmd="mplayer_cmd"  

#string used in config file for volume setting
str_volume="volume"  

#string used in config file for favorite
str_favorite="favorite"

#string used in config file for favorite index
str_favorites_index="favorite_index"

#string used in config file for icy picture setting
str_icy_picture="icy_picture"

#string used in config file for icy picture pop up update setting
str_icy_picture_pop_update="icy picture_pop_update"

#string used in config file for icy picture browser update setting
str_icy_picture_browser_update="icy_picture_browser_update"

#string used in config file for show console setting
str_console="console"

class radio():           
## Constructor    
    def __init__(self, bundle_dir, share_dir, favicon, defaultpic, radioversion):
        self.bundle_dir=bundle_dir
        self.share_dir=share_dir
        self.favicon=favicon
        self.defaultpic=defaultpic
        self.radioversion=radioversion
        
        self.channel=channel_t() 
        self.channels=channels_t()
        self.favorites=channels_t()
        # status off the radio
        self.radio_on=False 
        self.radio_mute=False # mute status off the radio
        self.favorits_active=True # decides if Ch+ and Ch- buttons work on favorites or channels
        self.show_icy_picture=True
        self.show_icy_picture_pop=False
        self.show_icy_picture_pop_update=False
        self.show_console=True
        self.show_default_picture=True
        self.popout_window_created=False
        self.show_icy_picture_browser=False
        self.show_icy_picture_browser_update=False
        
        userpath=os.path.expanduser("~")           # check what user
        self.configdir=userpath+"/.RadioFE"
        if os.access(self.configdir, os.F_OK)==False:  # check if user has a directory containing persistent data
          os.mkdir(self.configdir)                                    # if not create the directory
        configfile="conf"
        favoritesfile="favorites.chan"
        defaultchanfile="default.chan"     
        self.pathtoconfig=self.configdir+"/"+configfile
        self.pathtofavorites=self.configdir+"/"+favoritesfile
        self.pathtodefaultchanfile=share_dir+"/Channels/"+defaultchanfile
        logging.debug("Config file "+self.pathtoconfig)
        self.alt_decode='iso8859_2'
        self.mplayer_cmd="mplayer -slave -quiet -prefer-ipv4"
        self.volume="80"
        self.show_icy_picture=True
        self.show_icy_picture_pop=False
        self.show_icy_picture_pop_update=False
        self.show_console=True
        
        if os.access(self.pathtoconfig, os.F_OK)==True:   # check if file exists containing persistent data     
            pathtoconfigfile=open(self.pathtoconfig) # now read the file containing persistent data 
            radioconf=pathtoconfigfile.readlines()  
            pathtoconfigfile.close()
            for i in radioconf: 
                     logging.debug(i.strip()) 
                     t=i.split("=")
                     if(t[0]==str_alt_decode):
                        self.alt_decode=t[1].strip()   
                     if(t[0]==str_mplayer_cmd):
                        self.mplayer_cmd=t[1].strip()     
                     if(t[0]==str_volume):
                        self.volume=t[1].strip()           
                     if(t[0]==str_favorites_index):  
                         self.favorites.set_index(int(t[1]))
                     if(t[0]==str_icy_picture):
                        if(t[1].strip()=="True"):
                           self.show_icy_picture=True
                        else:
                           self.show_icy_picture=False
                     if(t[0]==str_icy_picture_pop_update):
                        if(t[1].strip()=="True"):
                           self.show_icy_picture_pop_update=True
                        else:
                           self.show_icy_picture_pop_update=False       
                     if(t[0]==str_icy_picture_browser_update):
                        if(t[1].strip()=="True"):
                           self.show_icy_picture_browser_update=True
                        else:
                           self.show_icy_picture_browser_update=False         
                     if(t[0]==str_console):
                        if(t[1].strip()=="True"):
                           self.show_console=True
                        else:
                           self.show_console=False     
                    
        if os.access(self.pathtofavorites, os.F_OK)==True:   # check if file exists containing persistent data                 
           self.channel=self.favorites.read(self.pathtofavorites)             
        else:       
           self.channel=self.favorites.read(self.pathtodefaultchanfile)
        logging.debug("ch to "+self.channel.get_name())

    def save(self):
        """Save the radio settings to the files"""     
        pathtoconfigfile=open(self.pathtoconfig,  'w')     # now save the config
        pathtoconfigfile.write("#radio configuration\n")  
        pathtoconfigfile.write("version="+self.radioversion+"\n")  
        pathtoconfigfile.write(str_alt_decode+"="+self.alt_decode+"\n")  
        pathtoconfigfile.write(str_mplayer_cmd+"="+self.mplayer_cmd+"\n")  
        pathtoconfigfile.write(str_volume+"="+self.volume+"\n")  
        pathtoconfigfile.write(str_favorites_index+"="+str(self.favorites.get_index())+"\n")  
        if(self.show_console==True):
            pathtoconfigfile.write(str_console+"=True\n")  
        else:    
            pathtoconfigfile.write(str_console+"=False\n")  
    
        if(self.show_icy_picture==True):
            pathtoconfigfile.write(str_icy_picture+"=True\n")  
        else:    
            pathtoconfigfile.write(str_icy_picture+"=False\n")  

        if(self.show_icy_picture_pop_update==True):
            pathtoconfigfile.write(str_icy_picture_pop_update+"=True\n")  
        else:    
            pathtoconfigfile.write(str_icy_picture_pop_update+"=False\n")  
            
        if(self.show_icy_picture_browser_update==True):
            pathtoconfigfile.write(str_icy_picture_browser_update+"=True\n")  
        else:    
            pathtoconfigfile.write(str_icy_picture_browser_update+"=False\n")      

        pathtoconfigfile.close()
        logging.debug(self.pathtoconfig+" saved")  
        self.favorites.write(self.pathtofavorites)    
        logging.debug(self.pathtofavorites+" saved") 
