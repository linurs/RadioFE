import subprocess
import shlex
import logging
import queue

import threading
import webbrowser
import shutil

from tkinter import *   
from tkinter import messagebox   
from tkinter import filedialog   
from urllib.request import urlopen

from radiofe.radio import *

try:
   from PIL import ImageTk, Image
   PIL_imported=True  # Indication that PIL the python imageing library (pillow) is imported 
except:
   PIL_Imported=False 
   
#width of the buttons in the radio window
buttonwidth=15

#size of the picture in the radio window
pic_size=100   

class tkradio(radio):

    def __init__(self, bundle_dir, share_dir, favicon, defaultpic, radioversion):
        """The constructor for the GUI application"""   
        radio.__init__(self, bundle_dir, share_dir, favicon, defaultpic, radioversion)

        self.poppic_x=450
        self.poppic_y=450
        self.queue = queue.Queue()
        
        # setup the gui stuff
        self.window=Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.title('RadioFE')
        
        # add an icon
        img = PhotoImage(file=self.favicon)
        self.window.call("wm", "iconphoto", self.window, "-default", img)
        self.window.resizable(width=FALSE, height=FALSE)
        
        # create the menus   
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
        viewmenu.add_command(label="ICY Picture pop out", command=self.popoute)
        
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
        """Destroy the pop up window"""
        logging.debug("pop event")
        self.popout_window_created=False
        self.top.destroy()
        
    def sampler(self):    
          logging.debug("sampler called")
   #       self.popout(self.poppic_x, self.poppic_y) # to be replaced by pipe and just do the last pipe entry
          if self.queue.qsize():
              logging.debug("queue has data")
              while self.queue.empty()==False:
                  try:
                    size = self.queue.get()
                    logging.debug(size)
                    self.queue.task_done()
                  except queue.Empty:
                    pass
              self.popout(size[0], size[1])      
              logging.debug("resize picture")
          else:    
              logging.debug("queue has no data")
        
    def popconfigure(self, event):
        """Size op pop up window has changed"""
        if(self.poppic_x!=event.width-2)or(self.poppic_y!=event.height-2):
            logging.debug("pop config event. Height "+str(event.height)+" Width "+str(event.width))
            self.poppic_x=event.width-2
            self.poppic_y=event.height-2
            logging.debug("new size. Height "+str(self.poppic_y)+" Width "+str(self.poppic_x))
            self.queue.put((self.poppic_x, self.poppic_y))  
            
      #      self.popout(self.poppic_x, self.poppic_y)
            self.window.after(250, self.sampler)
        else:
            logging.debug("pop config event without size change")
     
        
    def popoute(self):
         self.popout(self.poppic_x, self.poppic_y)
         
    def popout(self, x, y):
        """Create or update pop up window"""
        if(self.show_default_picture==False):
            newsize = (x, y) 
            img=self.img.resize(newsize)
            self.picture = ImageTk.PhotoImage(img)           
            self.show_icy_picture_pop=True
   
            if(self.popout_window_created==False):
              self.top = Toplevel()
              self.top.protocol("WM_DELETE_WINDOW", self.popevent) 
              self.top.title("RadioFE picture") 
              self.top.picturearea=Label(self.top,  image=self.picture)
              self.top.picturearea.grid()
              self.top.bind("<Configure>", self.popconfigure)
              self.popout_window_created=True
            else:   
                self.top.picturearea.configure(image=self.picture)            
    
    def icy_browser_update(self):
        """Set browser update flag"""
        if(self.browser_update_gui.get()==True):
             self.show_icy_picture_browser_update=True
        else:  
             self.show_icy_picture_browser_update=False   
    
    def icy_browser(self):
        """Open browser with icy picture"""
        if(self.show_default_picture==False):
           webbrowser.open_new_tab(self.icy_url)
           self.show_icy_picture_browser=True
        
    def get_channel_list(self):
        """Get chanell list"""
        filename = filedialog.askopenfilename(initialdir=self.share_dir+"/Channels",title = "Select file",filetypes = (("Channel files","*.chan"),("All files","*.*")))  
        
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
        """Play favorites"""
        self.favorits_active=True
        self.channel=self.favorites.get()
        self.title=""
        self.radio_station_name=self.channel.get_name()
        self.update_gui()
        self.play()
        
    def remove_favorites(self):
        """Remove favorites"""
        if(self.favorits_active==True):
             self.channel=self.favorites.remove()
             self.play_favorites()     
        else:        
             messagebox.showerror("Error","Does not play favorites now")       
        
    def add_favorites(self):
        """add favorites"""    
        if(self.favorits_active==True):
             messagebox.showinfo("Favorite","Channel is already in the favorite channel list")       
        else:   
             self.favorites.append(self.channel)

    def on_closing(self):
       """exit""" 
       self.exit()
        
    def set_volume(self):
        """Set volume"""
        self.volume_change(self.volume)
        
    def volume_change(self, v):
        """Volume has changed in gui so set it"""
        self.volume=v 
        x="volume "+self.volume+" 1\n"
        xb=x.encode('utf-8')
        logging.debug(xb)
        self.radio_popen.stdin.write(xb)    
        self.radio_popen.stdin.flush()
      
    def console(self):
         """Show and hide console"""        
         if(self.console_gui.get()==False):   
             self.text.grid_remove()
             self.show_console=False
         else:    
             self.text.grid()
             self.show_console=True
    
    def icy_picture(self):
         """Show and hide icy picture"""
         if(self.icy_picture_gui.get()==False):
             self.window.picturearea.grid_remove()
             self.show_icy_picture=False
         else:    
             self.window.picturearea.grid()
             self.show_icy_picture=True
      
    def icy_picture_update(self):
         """Update icy picture"""
         if(self.popout_update_gui.get()==False):
             self.show_icy_picture_pop_update=False
         else:    
             self.show_icy_picture_pop_update=True
        
    def run(self):
        """run"""
        self.window.after(250, self.start) # start thread after mainloop to have thread in mainloop
        self.window.mainloop()        
        
    def start(self):    
        self.play()
        self.set_volume()
        
    def exit(self):
         """exit"""
         self.off()
         self.window.destroy()

    def about(self):
         """Shows abbout messagebox"""
         messagebox.showinfo("About","Internet Radio Front End from https://www.linurs.org \nVersion "+radioversion)       

    def play(self):
        """Play the selected radio station"""
        self.on(self.channel.get_url())
        ## name of the radio station
        self.radio_station_name=self.channel.get_name()
        ## song title
        self.title=""
        self.update_gui()

    def on(self, url):
         """Turn the radio on"""
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
         logging.debug(cmd)
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
             pass

    def radio_info_thread_function(self):      
        """thread reading radio infor mation from mplayer as title and picture"""
        logging.info('radio info thread started')    
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
                        self.img =Image.open(urlopen(self.icy_url))
                        self.update_url_picture()
                        if(self.show_icy_picture_pop_update==True):
                          self.popout( self.poppic_x,  self.poppic_y)
                        if(self.show_icy_picture_browser_update==True)and(self.show_icy_picture_browser==True):
                          self.icy_browser()   
        logger.info('radio info thread terminated')    

    def off(self):
        """Turn the radio off"""
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
        """Mute the radio"""
        self.radio_popen.stdin.write(b'mute\n')    
        self.radio_popen.stdin.flush()
        if(self.radio_mute==True):
            self.radio_mute=False
        else:
           self.radio_mute=True   
        self.update_gui()   
        
    def update_url_picture(self):    
        """Update the picture in the radio window"""
        newsize = (pic_size, pic_size) 
        img=self.img.resize(newsize)
        self.window.picture = ImageTk.PhotoImage(img)
        self.window.picturearea.configure(image=self.window.picture)
        self.show_default_picture=False

    def default_picture(self):   
        """Put the default picture into the radio window"""
        img =Image.open(defaultpic)
        newsize = (pic_size, pic_size) 
        img=img.resize(newsize)
        self.window.picture = ImageTk.PhotoImage(img)
        self.window.picturearea.configure(image=self.window.picture)
        self.show_default_picture=True

    def chup(self):
        """Channel up button pressed"""
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
        """Channel down button pressed"""   
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

    def factory_reset(self):
        """Delete the setting files"""
        r=messagebox.askyesno("Factory Reset","Factory reset deletes "+self.configdir+"\nContinue?")   
        if(os.path.exists(self.configdir)and(r==True)):
           try:
             shutil.rmtree(self.configdir) 
           except OSError as e:
             logging.error("%s : %s" % (self.configdir, e.strerror))  
           s=messagebox.askyesno("Factory Reset","Factory reset done. Exit now?")   
           if s==True:
               self.exit()
        else:
           messagebox.showinfo("Factory Reset",self.configdir+" does not exist")       
      
    def update_gui(self):
        """update widges in the radio window"""  
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
