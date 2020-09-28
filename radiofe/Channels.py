from Channel import *
from tkinter import messagebox   

class channels_t():
## 

    def __init__(self):
        self.clear()
        
    def clear(self):
        self.list=[]       
        self.index=0
     
    def set_index(self, index=0):
       self.index=index 
     
    def get_index(self):
       return self.index  
     
    def append(self, channel):
      self.list.append(channel)  
  
    def up(self):
        if len(self.list)>0:
            self.index+=1
            if self.index>=len(self.list):
                self.index=0
      #      self.set()    
            self.channel=self.list[self.index]         
            return self.list[self.index]    
        else:
            return None    

    def down(self):
        if len(self.list)>0:
            self.index-=1
            if self.index<0:
                self.index=len(self.list)-1
            self.channel=self.list[self.index]         
            return self.list[self.index]    
        else:
            return None        
     
    def read(self, filename):
            fileh=open(filename) 
            list_csv=fileh.readlines()  
            fileh.close()
            for csv in list_csv:
                channel=channel_t()
                if channel.set_csv(csv)==True:
                    self.append(channel)
            return self.get()    
                
    def write(self, filename):            
        fileh=open(filename,  'w')
        fileh.write("# Channel List\n")  
        for i in self.list:
            fileh.write(i.get_csv())  
        fileh.close()     
     
    def get(self):
        return self.list[self.index]     
        
    def remove(self):
         if(len(self.list)==1):
            messagebox.showerror("Error","Last channel in the list can not be removed")       
         else:    
             del self.list[self.index]
             self.index-=1
             if(self.index<0):
                  self.index=0    
         return self.list[self.index]          
