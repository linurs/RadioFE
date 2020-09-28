class channel_t():
## 
    def __init__(self, name="", url=""):
        self.set(name=name,  url=url)

    def set(self, name="", url=""):
        self.name=name
        self.url=url
        self.title=""    
        
    def set_csv(self, csv=""):    
         if (csv[0]!="#"):
             s=csv.strip("\n")
             s=s.split(";")
             if(len(s)==2):
                 self.name=s[0].strip()
                 self.url=s[1].strip()
                 self.title=""    
                 return True
             else:
                return False    
         else:
             return False    
        
    def set_title(self, title=""):
        self.title=title        
        
    def set_name(self, name=""):
        self.name=name            
        
    def get_csv(self):
         s=self.get_name()+";"+self.get_url()+"\n"
         return s 
        
    def get_name(self):
        return self.name
    
    def get_url(self):
        return self.url    
    
    def get_title(self):
        return self.title        
        
    def clear(self):    
        self.name=""
        self.url=""
        self.title=""
