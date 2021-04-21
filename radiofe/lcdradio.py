import socket
import time

def b2int(b):
     return int(b.decode())

class lcdproc_t():
    
     def __init__(self):
         HOST = '127.0.0.1'  
         PORT = 13666       
         self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         try:
             self.s.connect((HOST, PORT))
             self.connected=True
             data=self.trans(b'hello\n').split()
             self.display_x=b2int(data[7])
             self.display_y=b2int(data[9])
             self.char_x=b2int(data[11])
             self.char_y=b2int(data[13])
             self.display_xp=self.display_x*self.char_x
             self.display_yp=self.display_y*self.char_y
             self.trans(b'client_set name Linurs\n')
         except:
             self.connected=False
             
     def add_clock(self):
             self.trans(b'screen_add clock\n')
           #  self.trans(b'screen_set clock priority input\n')
             self.trans(b'screen_set clock priority foreground\n')
             self.trans(b'widget_add clock first num\n')
             self.trans(b'widget_add clock second num\n')
             self.trans(b'widget_add clock third num\n')
             self.trans(b'widget_add clock fourth num\n')
             self.trans(b'widget_add clock fifth num\n')
             
     def set_clock(self):      
        g=(time.time()/60) %1 
        t=time.localtime()  
        hour_t=str(t[3]/10)
        hour=str(t[3]%10)
        min_t=str(t[4]/10)
        min=str(t[4]%10)
        b=b'widget_set clock first 1 '+hour_t.encode()+b'\n'
        self.trans(b)
        b=b'widget_set clock second 4 '+hour.encode()+b'\n'
        self.trans(b)
        b=b'widget_set clock third 7 10\n'
        self.trans(b)
        b=b'widget_set clock fourth 8 '+min_t.encode()+b'\n'
        self.trans(b)
        b=b'widget_set clock fifth 11 '+min.encode()+b'\n'
        self.trans(b)
        return g
             
     def add_radio(self, volume=50):
            self.trans(b'screen_add radio\n') 
            self.trans(b'screen_set radio priority input\n')
           #  self.trans(b'screen_set radio priority foreground\n')
            self.trans(b'widget_add radio song scroller\n')
            self.trans(b'widget_add radio station scroller\n')
            self.trans(b'widget_add radio volumex string\n')
            self.trans(b'widget_add radio volume hbar\n')
            self.trans(b'widget_add radio volume0 string\n')
            self.trans(b'widget_set radio volume0 1 3 0%\n')
            self.trans(b'widget_add radio volume100 string\n')
            self.trans(b'widget_set radio volume100 13 3 100%\n')
            self.set_volume(volume)        
             
     def add_direct_keys(self):    
         self.trans(b'client_add_key A\n')
         self.trans(b'client_add_key B\n')
         self.trans(b'client_add_key C\n')     
         self.trans(b'client_add_key D\n')     
         self.trans(b'client_add_key E\n')
        
     def trans(self, c):
         self.s.sendall(c)
         data=self.read()
         return(data)
         
     def read(self):    
         data = self.s.recv(1024)
         return data
         
     def set_station(self, station):
        b=b'widget_set radio station 1 1 16 1 h 8 "'+station.encode('ascii', 'ignore')+b'"\n'
        self.trans(b)
        
     def set_song(self, song):
        b=b'widget_set radio song 1 2 16 2 h 8 "'+song.encode('ascii', 'ignore')+b'"\n'
        self.trans(b)

     def set_volume(self, v):    
         volume_str=str(v)+"%"
         volume_b=volume_str.encode()
         volume_bar=str(int(self.display_xp*v/100)).encode()
         self.trans(b'widget_set radio volumex 7 3 '+volume_b+b'\n')
         self.trans(b'widget_set radio volume 1 4 '+volume_bar+b'\n')
         
     def backlight_off(self):
        b=b'backlight off\n'
        self.trans(b)    
        
     def backlight_on(self):
        b=b'backlight on\n'
        self.trans(b)       
         
if __name__ == "__main__":
         s=lcdproc_t()
         if s.connected==True:
             while True:
                 print()
                 print("q quit") 
                 print("c clock")
                 print("r radio screen")
                 print("s change station") 
                 print("g change song")
                 print("v volume")
                 print("n backlight on")
                 print("f backlight off")
                 print("k keys")
                 k = input("Press command: ")
                 c=k.upper()
                 if c in ['Q']:
                     break	
                 elif c in ['C']:        
                     s.add_clock()    
                     while True:
                         t=s.set_clock()    
#                         if t>0.5:  
#                            sec=int(60+t*60)
#                         else:
#                            sec=int(60-t*60)
#                         print(sec)   
#                         if sec==0:
#                             sec=1
                         sec=15
                         time.sleep(sec)   
                 elif c in ['R']:    
                     s.add_radio(volume=60)
                 elif c in ['S']:
                     station = input("Type station: ")
                     s.set_station(station)
                 elif c in ['G']:
                     song = input("Type song: ")
                     s.set_song(song)
                 elif c in ['N']:
                     s.backlight_on()    
                 elif c in ['F']:
                     s.backlight_off()        
                 elif c in ['K']:
                     while True:
                         s.add_direct_keys()
                         data=s.read()
                         print(data)       
                 elif c in ['V']:    
                     n = input("Type volume: ")
                     try:
                         ni=int(n)
                         s.set_volume(ni)
                     finally:
                       pass    
         else:
            print("Can not connect to LCDd")   
