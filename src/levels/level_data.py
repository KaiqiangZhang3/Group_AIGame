class LevelData:
    """Represents the data and metadata for a game level."""
    def __init__(self,
                 layout,
                 name="Unnamed Level",
                 background_music=None,
                 next_level=None,
                 hidden_level=None):
        self.layout = layout.split('\n')[1:]  # The 2D layout of the level
        self.name = name  # Level name
        self.background_music = background_music  # Path to background music file
        self.next_level = next_level  # Next level to load after this one
        self.hidden_level = hidden_level  # Hidden level to load after this one

LEVEL_2 = LevelData(
    layout=                                                                  
"""                                                           
           P                                                                       
          XXX                                                                      
         X   X                                                                     
        X     X                                                                    
       XXX S XXX                                                                   
      X   X X   X            C                                                     
     X     X     X        XXXXXX                                                   
    XXXXX   S   XXXXX    X      X                                                  
   X     XXX XXX     X  X  S S  X                                                 
  X       X   X       XXX  X X  XXX                                                
 XXX  M            S  XXX        XXX         XXXXXX                               
X   XXXXX        XXXXX X    C     X        X      X                               
     X                 X X          X       X  S    X                              
 XXX                 XXXXXXXXXXXXXX      XXXXXXXXXXX                             
                                                                                   
          XXXXX              XXXXX                                                 
         X S S X            X S S X            XXXXXX                              
        XXXXXXX            XXXXXXX            X      X                             
       X                          X          X      X                             
      X   XXXXXXXXXXXXXXXXXXXX   X          X M    S X                           
     X   X                    X   X          XXXXXXXXXXXX                          
    X   X     S S S S S      X   X                                                
   X   XXXXXXXXXXXXXXXXXXXXXXXXX   X         X     X E                            
  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX                            
 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX                           
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX                        
""",
    name="Level 2",
    background_music=None
)

LEVEL_1 = LevelData(
    layout=                                                                  
"""                                                           
P                                                                                
XXXXX       C                                                                    
X   X      XXX                                                                   
X   X     X S X                                                                  
XXXXX    XXXXXXX                                                                 
X        X     X         XXXX                                                    
X        X     X        X    X                                                   
X        XXXXXXX       X S  S X        C                                         
X                     XXXXXXXXXX     XXXXX        SSSSSSS                        
X                                   X     X      X       X                       
X                                  X S S S X    XX S S S XX                      
X                                 XXXXXXXXX   XXX       XXX                      
X                                              XXXXX   XXXXX                     
X                                                X     X     X                    
X       XXXXXXXXXXXXXXXXXXXXXXXXXXXXX              M    S XXXX                   
X      X                             X        XXXXXXXXXXXXXXXXXXXXXX             
X     X S S S S S S S S S S S S S S S X      X                  XX E             
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX      
""",
    name="Level 1",
    background_music=None,
    next_level=LEVEL_2
)


ROOT_LEVEL = LEVEL_1