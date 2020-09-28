#!/usr/bin/python3

## @package gencfs 
# @author urs lindegger urs@linurs.org  

## @todo  
# - add mplayer command line into config 
# - check for mplayer installed not static do it on config file and exit when nothing is 
# - factory reset also delete favorites, why not just complete dir?
# - browser and pop up update do not work the same: pop up update opens window, browser update not, what is better?
# - other front end than mplayer
# - bad crash if stream is not valid
# - up/down edit for favorites
# - channel up and down add multiple tabs with the same icy picture in browser
# - character encoding in the console what is it?
# - nicer gui and tkinter alternatives qt, gtk
# - ebuild installer and where to put files
# - git hub
# - make more clever if else Truefalse handling in read and write file use a funtion
# - handle pop out window close better remove stuff in memory when close and reopen it clean
# - avoid using self almost everywhere
# - raspi, ui and network, clock, alarm, mono instead stereo use web server and not fancy ui to do settings, bluetooth source select (test with parallel port PC, print case for it, elecx)

## @mainpage gencfs
# radio RTTM is a simple Reduced To The Minimum internet radio.
# it is intended to listen and not to watch radio, so its gui is reduced to the minimum

import os
import subprocess
import shlex
import shutil
import argparse
import logging
import sys
import threading
import webbrowser

from Channel import *
from Channels import *
   
from tkinter import *   
from tkinter import messagebox   
from tkinter import filedialog   

from PIL import ImageTk, Image
from urllib.request import urlopen

## Version of radio
radioversion="0.0"

## favicon file to seen in window decoration
faviconname=   'favicon.gif'
defaultpicname='default.png'

str_alt_decode="alt_decode"  
str_mplayer_cmd="mplayer_cmd"  
str_volume="volume"  
str_favorite="favorite"
str_favorites_index="favorite_index"
str_icy_picture="icy_picture"
str_icy_picture_pop_update="icy_picture_pop_update"
str_icy_picture_browser_update="icy_picture_browser_update"

str_console="console"

buttonwidth=15
pic_size=100
poppic_size=450

class app_t():
##
     
# The constructor for the GUI application   
    def __init__(self):
        
        self.channel=channel_t() 
        self.channels=channels_t()
        self.favorites=channels_t()
        
        self.radio_on=False # status off the radio
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
        configdir=userpath+"/.RadioFE"
        if os.access(configdir, os.F_OK)==False:  # check if user has a directory containing persistent data
          os.mkdir(configdir)                                    # if not create the directory
        configfile="conf"
        favoritesfile="favorites.chan"
        defaultchanfile="default.chan"     
        self.pathtoconfig=configdir+"/"+configfile
        self.pathtofavorites=configdir+"/"+favoritesfile
        self.pathtodefaultchanfile=bundle_dir+"/Channels/"+defaultchanfile
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
                     logging.debug(i) 
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
   
       # new way favorites are separate file                    
        if os.access(self.pathtofavorites, os.F_OK)==True:   # check if file exists containing persistent data                 
           self.channel=self.favorites.read(self.pathtofavorites)             
        else:       
           self.channel=self.favorites.read(self.pathtodefaultchanfile)
        logging.debug("ch to "+self.channel.get_name())
        
        ## setup the gui stuff
        self.window=Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.title('RadioFE')
        
        # add an icon
        img = PhotoImage(file=favicon)
        self.window.call("wm", "iconphoto", self.window, "-default", img)
        self.window.resizable(width=FALSE, height=FALSE)
        
        ## create the menus   
        self.menubar = Menu(self.window)
        
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Factory Reset", command=self.factory_reset)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)
        
        channelmenu = Menu(self.menubar, tearoff=0)
        channelmenu.add_command(label="Get Channel Lists", command=self.get_channel_list)
        channelmenu.add_separator()
        channelmenu.add_command(label="Play Favorites", command=self.play_favorites)
        channelmenu.add_command(label="Add to Favorites", command=self.add_favorites)
        channelmenu.add_command(label="Remove from Favorites", command=self.remove_favorites)
        
        viewmenu = Menu(self.menubar, tearoff=0)
        self.icy_picture_gui=BooleanVar()
        viewmenu.add_checkbutton(label="ICY Picture show", variable=self.icy_picture_gui, command=self.icy_picture)
        self.icy_picture_gui.set(self.show_icy_picture)
        
        viewmenu.add_separator()
        viewmenu.add_command(label="ICY Picture pop out", command=self.popout)
        
        self.popout_update_gui=BooleanVar()
        viewmenu.add_checkbutton(label="ICY Picture update pop out", variable=self.popout_update_gui, command=self.icy_picture_update)
        self.popout_update_gui.set(self.show_icy_picture_pop_update)

        viewmenu.add_separator()
        viewmenu.add_command(label="ICY Picture open in browser", command=self.icy_browser)
        self.console_gui=BooleanVar()
        self.browser_update_gui=BooleanVar()
        viewmenu.add_checkbutton(label="ICY Picture update browser", variable=self.browser_update_gui, command=self.icy_browser_update)
        self.browser_update_gui.set(self.show_icy_picture_browser_update)
        
        viewmenu.add_separator()
        viewmenu.add_checkbutton(label="Console", variable=self.console_gui, command=self.console)
        self.console_gui.set(self.show_console)
   
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_cascade(label="Channel", menu=channelmenu)
        self.menubar.add_cascade(label="View", menu=viewmenu)
        self.menubar.add_command(label="About", command=self.about)
        self.window.config(menu=self.menubar)
        
        row=0
        # set up and register stream title
        self.radio_station_name_gui=StringVar()
        Label(master=self.window, textvariable=self.radio_station_name_gui).grid(row=row, columnspan=3)
        self.radio_station_name_gui.set("")
        row+=1
        self.stream_title_gui=StringVar()
        Label(master=self.window, textvariable=self.stream_title_gui).grid(row=row, columnspan=3)
        self.stream_title_gui.set("")
        row+=1
 
        self.window.chdownbutton=Button(master=self.window,text='Ch-',width=buttonwidth, command=self.chdown)
        self.window.chdownbutton.grid(row=row) 
  
        self.window.mutebutton=Button(master=self.window,text='Mute',width=buttonwidth, command=self.mute)
        self.window.mutebutton.grid(row=row, column=1)
        
        self.window.chupbutton=Button(master=self.window,text='Ch+',width=buttonwidth, command=self.chup)
        self.window.chupbutton.grid(row=row,  column=2)
        row+=1
        self.bg=self.window.chupbutton.cget('bg')
        self.fg=self.window.chupbutton.cget('fg')    
                     
        self.window.volumescale = Scale(master=self.window, from_=0, to=100, orient=HORIZONTAL, tickinterval=25,  command=self.volume_change, length=400, showvalue=0 )
        self.window.volumescale.grid(row=row, columnspan=3)
        row+=1
        
        img =Image.open(defaultpic)
        newsize = (pic_size, pic_size) 
        img=img.resize(newsize)
        self.window.picture = ImageTk.PhotoImage(img)
        self.window.picturearea=Label(self.window,  image=self.window.picture)
        self.window.picturearea.grid( row=0,  column=3,  rowspan=4)

        textwidth=72
        self.text = Text(self.window, width=textwidth, height=20, highlightthickness=0, bd=0, bg='white', relief='sunken', padx=5, pady=5)
        self.text.grid(columnspan=4,  sticky= W)
     
    def popevent(self):
             logging.debug("pop event")
             self.popout_window_created=False
             self.top.destroy()
        
    def popout(self):
        if(self.show_default_picture==False):
            img =Image.open(urlopen(self.icy_url))
            newsize = (poppic_size, poppic_size) 
            img=img.resize(newsize)
            self.picture = ImageTk.PhotoImage(img)           
            self.show_icy_picture_pop=True
   
            if(self.popout_window_created==False):
              self.top = Toplevel()
              self.top.resizable(width=FALSE, height=FALSE)
              self.top.protocol("WM_DELETE_WINDOW", self.popevent) 
              self.top.title("RadioFE picture") 
              self.top.picturearea=Label(self.top,  image=self.picture)
              self.top.picturearea.grid()
              self.popout_window_created=True
            else:   
                self.top.picturearea.configure(image=self.picture)            
    
    def icy_browser_update(self):
        if(self.browser_update_gui.get()==True):
             self.show_icy_picture_browser_update=True
        else:  
             self.show_icy_picture_browser_update=False   
    
    def icy_browser(self):
         if(self.show_default_picture==False):
           webbrowser.open_new_tab(self.icy_url)
           self.show_icy_picture_browser=True
        
    def get_channel_list(self):
        filename = filedialog.askopenfilename(initialdir=bundle_dir+"/Channels",title = "Select file",filetypes = (("Channel files","*.chan"),("All files","*.*")))  
        
        if os.access(filename, os.F_OK)==True:
            self.channels.clear()
            self.channel=self.channels.read(filename)             
            self.favorits_active=False
            self.title=""
            self.radio_station_name=self.channel.get_name()
            logging.debug("ch to "+self.channel.get_name())
            self.on(self.channel.get_url())
            self.update_gui()
                
    def play_favorites(self):
         self.favorits_active=True
         self.channel=self.favorites.get()
         self.title=""
         self.radio_station_name=self.channel.get_name()
         self.update_gui()
         self.play()
        
    def remove_favorites(self):
         if(self.favorits_active==True):
             self.channel=self.favorites.remove()
             self.play_favorites()     
         else:        
             messagebox.showerror("Error","Does not play favorites now")       
        
    def add_favorites(self):    
        if(self.favorits_active==True):
             messagebox.showinfo("Favorite","Channel is already in the favorite channel list")       
        else:   
             self.favorites.append(self.channel)

    def on_closing(self):
       self.exit()
        
    def set_volume(self):
        self.volume_change(self.volume)
        
    def volume_change(self, v):
        self.volume=v 
        x="volume "+self.volume+" 1\n"
        xb=x.encode('utf-8')
        logging.debug(xb)
        self.radio_popen.stdin.write(xb)    
        self.radio_popen.stdin.flush()
      
    def console(self):
     if(self.console_gui.get()==False):   
         self.text.grid_remove()
         self.show_console=False
     else:    
         self.text.grid()
         self.show_console=True
    
    def icy_picture(self):
     if(self.icy_picture_gui.get()==False):
         self.window.picturearea.grid_remove()
         self.show_icy_picture=False
     else:    
         self.window.picturearea.grid()
         self.show_icy_picture=True
      
    def icy_picture_update(self):
     if(self.popout_update_gui.get()==False):
         self.show_icy_picture_pop_update=False
     else:    
         self.show_icy_picture_pop_update=True
        
##
# runs the gui
    def run(self):
        self.play()
        self.set_volume()
        self.window.mainloop()        
##
# Quits the application
    def exit(self):
         self.off()
         self.window.destroy()

##
# Shows abbout messagebox
    def about(self):
         messagebox.showinfo("About","Internet Radio Front End from https://www.linurs.org \nVersion "+radioversion)       

    def play(self):
        self.on(self.channel.get_url())
        self.radio_station_name=self.channel.get_name()
        self.title=""
        self.update_gui()
        
    def on(self, url):
         if self.radio_on==True:
             self.off()
         self.radio_on=True
         r=url.split(".")
         rext=r[-1]
         if(rext.strip()=="m3u"):
             playlist="-playlist "
         else:
            playlist=""    
         cmd =self.mplayer_cmd+" -volume "+self.volume+" "+playlist+url
         logger.debug(cmd)
         args=shlex.split(cmd)
         self.text.insert('end', cmd+"\n")
         try:
             self.radio_popen= subprocess.Popen(args, 
                                  stdin=subprocess.PIPE, 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, # standard err are passed to stdout
                                  ) # open new process
         except:
            pass     
         self.update_gui()
         logging.debug(str(threading.active_count())+' threads are running') 
         if(threading.active_count()<=1):
             self.radio_info_thread = threading.Thread(target=self.radio_info_thread_function, args=())
             self.radio_info_thread.start()
             logging.debug(str(threading.active_count())+' threads are running') 
            
    def radio_info_thread_function(self):      
        logger.info('radio info thread started')    
        while(self.radio_on==True):
            a=self.radio_popen.stdout.readline();
            try:
                s=a.decode('utf-8')
            except:
                s=a.decode(self.alt_decode)
                logging.debug(s+" is not utf-8") 
            self.text.insert('end', s)
            self.text.see(END)   
           # get station name
            t=s.split(":")
            if(t[0].strip()=="Name"):      
                self.channel.set_name(t[1].strip())
                self.radio_station_name_gui.set(self.channel.get_name())
       # analyze icy      
            icy=s.split(":") 
            if(icy[0]=="ICY Info"):
                 logging.debug(s) 
                 icy_elements=s[9:len(s)].strip().split(";")
                 logging.debug("ICY contains "+str(len(icy_elements))+" elements") 
                 for element in icy_elements:
                     data=element.strip().split("=")
                     if(data[0]=="StreamTitle"):
                        logging.debug("Stream title :"+data[1])
                        self.channel.set_title(data[1].strip("'"))
                        self.stream_title_gui.set(self.channel.get_title())
                     if(data[0]=="StreamUrl"):
                        self.icy_url=element[11:len(element)].strip("\n")
                        logging.debug("Stream url :"+self.icy_url)
                        self.update_url_picture(self.icy_url)
                        if(self.show_icy_picture_pop_update==True):
                          self.popout()
                        if(self.show_icy_picture_browser_update==True)and(self.show_icy_picture_browser==True):
                          self.icy_browser()   
        logger.info('radio info thread terminated')    
     
    def off(self):
        if(self.radio_on==True):
            self.radio_popen.stdin.write(b'quit\n')
            self.radio_popen.stdin.flush()
            self.radio_popen.stdin.close()
            self.radio_popen.terminate()
            self.radio_popen.wait(timeout=0.2)
        
            self.radio_on=False
            self.radio_station_name=""
            self.update_gui()

    def mute(self):
        self.radio_popen.stdin.write(b'mute\n')    
        self.radio_popen.stdin.flush()
        if(self.radio_mute==True):
            self.radio_mute=False
        else:
           self.radio_mute=True   
        self.update_gui()   
        
    def update_url_picture(self, url):    
        img =Image.open(urlopen(url))
        newsize = (pic_size, pic_size) 
        img=img.resize(newsize)
        self.window.picture = ImageTk.PhotoImage(img)
        self.window.picturearea.configure(image=self.window.picture)
        self.show_default_picture=False
     
    def default_picture(self):   
        img =Image.open(defaultpic)
        newsize = (pic_size, pic_size) 
        img=img.resize(newsize)
        self.window.picture = ImageTk.PhotoImage(img)
        self.window.picturearea.configure(image=self.window.picture)
        self.show_default_picture=True

    def chup(self):
        self.off()
        if(self.favorits_active==False):
                self.channel=self.channels.up()
        else:        
                    self.channel=self.favorites.up()
        logging.debug("ch+ to "+self.channel.get_name())
        self.radio_station_name=self.channel.get_name()
        self.on(self.channel.get_url())
        self.title=""
        self.default_picture()
        self.update_gui()        
    
    def chdown(self):
        self.off()
        if(self.favorits_active==False):
                self.channel=self.channels.down()
        else:  
                self.channel=self.favorites.down()
        logging.debug("ch- to "+self.channel.get_name())
        self.radio_station_name=self.channel.get_name()
        self.on(self.channel.get_url())
        self.title=""
        self.default_picture()
        self.update_gui()             
      
    def save(self):
        pathtoconfigfile=open(self.pathtoconfig,  'w')     # now save the config
        pathtoconfigfile.write("#radio configuration\n")  
        pathtoconfigfile.write("version="+radioversion+"\n")  
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
     
    def factory_reset(self):
        r=messagebox.askyesno("Factory Reset","Factory reset deletes "+self.pathtoconfig+"\nContinue?")   
        if(os.path.exists(self.pathtoconfig)and(r==True)):
           os.remove(self.pathtoconfig)
           s=messagebox.askyesno("Factory Reset","Factory reset done. Exit now?")   
           if s==True:
               self.exit()
        else:
           messagebox.showinfo("Factory Reset",self.pathtoconfig+" does not exist")       
        
    def update_gui(self):
        if(self.radio_mute==True):    
                self.window.mutebutton.config(relief=SUNKEN)
        else:        
             self.window.mutebutton.config(relief=RAISED)
        self.window.volumescale.set(int(self.volume))  
        if( self.favorits_active==True):
            self.window.chupbutton.config(bg=self.bg, fg=self.fg)
            self.window.chdownbutton.config(bg=self.bg, fg=self.fg)
        else:    
            self.window.chupbutton.config(bg='black', fg='white')
            self.window.chdownbutton.config(bg='black', fg='white')
        self.radio_station_name_gui.set(self.channel.get_name())
        self.stream_title_gui.set(self.channel.get_title())
        self.icy_picture()
        self.console()
        self.popout_update_gui.set(self.show_icy_picture_pop_update)
        self.browser_update_gui.set(self.show_icy_picture_browser_update)

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
         exit()
        
    ## pyinstaller stuff required to create bundled versions:      
    frozen = 'not '
    if getattr(sys, 'frozen', False): # pyinstaller adds the name frozen to sys 
            frozen = ''  # we are running in a bundle (frozen)
            ## temporary folder of pyinstaller
            bundle_dir = sys._MEIPASS  
    else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))   # we are running in a normal Python environment 
    logging.debug('Script is '+frozen+'frozen')
    logging.debug('Bundle dir is '+bundle_dir )
    logging.debug('sys.argv[0] is '+sys.argv[0] )
    logging.debug('sys.executable is '+sys.executable )
    logging.debug('os.getcwd is '+os.getcwd() )
    ## makes that the files are found
    favicon=bundle_dir+os.sep+faviconname
    defaultpic=bundle_dir+os.sep+defaultpicname
    if (os. path. isfile(favicon)==False):
        logging.debug(favicon+' not found' )
        favicon="/usr/share/radio/"+faviconname
        logging.debug('so try to find it at '+favicon )
        if (os. path. isfile(favicon)==False):
             logging.error(faviconname+' not found')
             exit()
        
## start the application    
    app=app_t()
    app.run()
