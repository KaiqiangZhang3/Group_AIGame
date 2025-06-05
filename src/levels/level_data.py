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

# Level 1 and Level 2 have been deleted

# Define all levels first without next_level references, then set up progression later
# LEVEL_3 -> LEVEL_4 -> LEVEL_5 -> LEVEL_6 -> LEVEL_3 (loop)

LEVEL_3 = LevelData(
    layout=
"""
X                                                                                          
X
X
X
X                        S                              
X        T        o      X      T T T   S                      E
X      XXXXXXXaaaaaaaaaaaX              S             X             XXXXXXXXXX
X      X     X                          X             X             X
X      X     X                          X                           X
X      X     X                                                      X
X      X     X                                                      XXXXXXXXXXX
X      X     X
X      X     X
X      X     X
X      X     X
X P    X     XSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXTXTXTXTXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
""",
    name="Level 3",
    background_music=None
)

LEVEL_4 = LevelData(
    layout=                                                                  
"""                                                           
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                XXXXXXXXXXXXXXXXXXXXXXXXXXSSSSSSSSSSSSSSSXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
P               XXXXXSSSSSSSSSSSSSSSSXX                XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXX            XXXXX                XX                    XX                          XXXXXXXXXXXX
XXXX            XXXXX                XX                    XX                                 XXXXX
XXXX            XXXXX                XX                    XX                                 XXXXX
XXXX            XXXXX                XX                    XX                                 XXXXX
XXXX               XX                                                                         
XXXX               XX                                                                         
XXXX                                 o                     o                                      E
XXXX                                                                                          XXXXX
XX                 o                                                                          XXXXX
XX                                                         SS                                 XXXXX
XX                           o       SS                    XX              o            XXXXXXXXXXX
XX                 SS                XX          o         XX                           XXXXXXXXXXX
XX                 XX                XX                    XX                                SXXXXX
XX                 XX                XX                    XX                               SXXXXXX
XX                 XX                XX                    XXS                             SXXXXXXX
XX                 XX                XX                    XXXXS                      SXXXXXXXXXXXX
XXXXXXXX           XX                XX                    XXXXS                     SXXXXXXXXXXXXX
XXXXXXXXXSSSSSSSSSSXXSSSSSSSSSSSSSSSSXXSSSSSSSSSSSSSSSSSSSSXXXXXSSSSSSSSSSSSSSSSSSSSSXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
""",
    name="Level 4",
    background_music=None
)

LEVEL_5 = LevelData(
    layout=
"""                                                           
XS                                                             
XS                                                             
XS                                                             
XS                                                               aaaaaaaaa                           
XS                                                               SSSSSSSSS                           
XS                                                               XXXXXXXXX                           
XS                                                        o      XXXXXXXXX                  E            
XS                                                                            XXXXXXXXXXXXXXXXXXXXXXX
XS                                                             
XS                                          M                                              
XS                             o        XXXXXXXXX                                          
XS                                      XXXXXXXXX                                          
XS                                                             
XS                                                             
XS                                                             
XS            aaaaaaaa                                               
XS       o    SSSSSSSS                                               
XS            XXXXXXXX                                               
XS                                                             
XS                                                             
XS                                                             
XS                                                             
XS                                                             
XS  TT                                                                                                                      
XS  TT                                                o                                  
XS                                                             
XS                                                             
XS                                                             
XS                 SSSS        SSSS                                     S                  
XS          TTTTTTT    aaaaaaaa    TTTTTTT                           TTTTTTTTT      
XS                                                             
XS                                                             
XS                                                                                    o                      
XS                                                             
XS                                                             
XS                                                             
XS                                                                                              TT        
XS                                                                                              TT        
XS                                                             
XS                                                             
XS                                                             
XS                                                                            TTTTTTTT                         
XS                                                                            SSSSSSSS                         
XS                                                                            XXXXXXXX                         
XS                                                             
XS                                                                   o
XS                                                             
XS                                                                                                      
XS                                                             
XS                                                             
XS                                             aaaaaaaaa                             
XS                                             SSSSSSSSS                             
XS                                             XXXXXXXXX                             
XS                                      o                     
XS                                                                                
XS                                                             
XS                                                             
XS              TTTTTTTTTT                                           
XS              SSSSSSSSSS                                           
XS              XXXXXXXXXX                                           
XS              XXXXXXXXXX                                                 
XS                                                             
XS                                                             
XS                                                                                                                         
XS                                                             
XS      p                                                        
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
""",
    name="Level 5",
    background_music=None
)

# Create blank Level 6 template for user customization
LEVEL_6 = LevelData(
    layout=
"""                                                           
   SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSXX                                                                                                                                               
XXX                                    SXX                                                                                                                                              
XXX                                     SXX                                                                                                                                             
XXX                             O        SXX                                                                                                                      
XXX                                       SXX                                                                                               
XXX        O                               SXX                                                                                              
XXX                                         SXXX                                                                                            
XXX                    XX                    SXX                                                
XXX                    XX                     SXXX                                                                                                                 
XXX                    XX       O             SXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXX                    XX                       XXS                          XXXX         
XXX                    XX                       XXS                             XXXXXXXXXXXX
XXX                    XX                       XXS                 O                      XXXXXXXXXXXX
XXX                    XX                       XXS                                        XXXXXXXXXXXX
XXX                    XX                O      XXS                            O           XXXXXXXXXXXX
XXX                    XX                       XXS               SSS                      XXXXXXXXXXXX
XXX                    XX                       XXS              SXXXS                     XXXXXXXXXXXX                                                                                                       
XXX                    XX                                        SXXXS                     XXXXXXXXXXXX                                                                                                                     
XXX                    XX                                        SXXXS                     XXXXXXXXXXXX                                                                                                          
XXX                    XX                                        SXXXS                                XXXXXXXXXXXX                                                                                                
XXX                    XX       O                         O      SXXXS                                          XXXXXXXXXXXX                                                                                  
XXX                    XX                                        SXXXS                                                     XXXXXXXXXXXXXXXXXXXXXXX                                                            
XXX                    XX                                        SXXXS                       O                                        XXXXXXXXXXXX                                                            
XXX                      SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSXXXS                                                                XXXXXXXXXXXX                                                            
XXX                                                             SSXXXSS                                                               XXXXXXXXXXXX                                                            
XXX                                                                SSSSSS                                  O                        XXXXXXXXXXXX                                                            
XXXS                   XX                                             SSSSSSSSS                                                     XXXXXXXXXXXX                                                            
XXXS                   XX                                                     SSSSSSS                                               XXXXXXXXXXXX                                                            
XXXS                   XX                                                            SSSSSS                                         XXXXXXXXXXXX                                                           
XXX                   SXX                                                                  SSSS                                     XXXXXXXXXXXX                                                                                                                                                      
XXX                   SXX                                                                     SSSS                                  XXXXXXXXXXXX                                                                                                                                                        
XXX                   SXX                                                                        SS                XXS              XXXXXXXXXXXX                                                                                                                                                      
XXX                   SXX                                                                          SS              XXS              XXXXXXXXXXXX                                                                                                                                                        
XXX                    XX                                                                          SS              XXS              XXXXXXXXXXXX                                                                                                                                                        
XXX                    XX                                                                          SS              XXS              XXXXXXXXXXXX                                                                                                                                                        
XXX                    XX                                                                          SS              XX              SXXXXXXXXXXXX                                                                                                                                                        
XXX                    XX                                                                          SS              XX              SXXXXXXXXXXXX                                                                                                                                                        
XXXS                   XX                                                                          SS              XX              SXXXXXXXXXXXX                                                                                                                                                        
XXXS                   XX                                                                          SS              XX              SXXXXXXXXXXXX                                                                                                                                                        
XXXS                   XX                                                                          SS              XXS              XXXXXXXXXXXX
XXXS                   XX                                                                           SS             XXS              XXXXXXXXXXXX
XXX                    XX                                                                            SS                             XXXXXXXXXXXX
XXX                   SXX                                                                            SS                             XXXXXXXXXXXX
XXX                   SXX                                                                            SS                             XXXXXXXXXXXX
XXX                   SXX                                                                            SS                             XXXXXXXXXXXX
XXX                   SXX                                                                             SS                                   XXXXX
XXX                   SXX                                                                             SSSS                                    XX       
XXX                    XX                                                                                SSS                                  XX                                                                                                                                                                            
XXX                    XX                                                                                  SSSSS                              XX                                                                          
XXX                    XX                                                                                       SSSSSS                        XX                                                                          
XXX                    XX                                                                                             SSSS                    XX                                                                          
XXX                    XX                                                                                                 SS                  XX                                                                          
XXXS                   XX                                                                                                   SS                XX                                                                          
XXXS                   XX                                                                                                     SS              XX                                                                          
XXXS                   XX                                                                                                       SS            XX                                                                          
XXXS                   XX                                                                                                       SS            XX                                                                          
XXX                    XX                                                                                                       SS            XX                                                                          
XXX                   SXX                                                                                                       SS              XX                                                                       
XXX                   SXX                                                                                                       SS                XX                                                                      
XXX                   SXX                                                                                                       SS                XX                                                                      
XXX                   SXX                                                                                                       SS                XXXXXXX                                                                    
XXX                   SXX                                                                                                       SS                       XX                                                               
XXX                    XX                                                                                                        SS                        XX                                                                                                                                                       
XXX                    XX                                                                                                          SS                        XX                                                    
XXX                    XX                                                                                                            SS                        XX                                                  
XXX                    XX                                                                                                             SS                         XX                                                
XXX                    XX                                                                                                              SSSS                      XXX                                                 
XXX                    XX                                                                                                                  SSS                   XXXXX              XX                                 
XXXS                   XX                                                                                                                    SSS                     XX          XX                                  
XXXS                   XX                                                                                                                       SS                     XX      XX                                    
XXXS                   XX                                                                                                                         SS                     XX  XX                                      
XXXS                   XX                                                 					                                                 SS                      XX                                      
XXXS                   XX                                                                                                                       SSS                                                                                          
XXXS                   XX                                                                                                                    SSS                                                                                          
XXXS                   XX                                                                                                                 SSS                                                                                          
XXX        e           SXX                                                                                                                S                                                                                          
XXXXXXXXXXXXXXXXXXXXXXXXX                                                                                                                      S               P                                                                           
                                                                                                                                        XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
                                                                                
P                                                                             E
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
""",
    name="Level 6 - Custom",
    background_music=None
)

# Set up level progression chain (now that all levels are defined)
LEVEL_3.next_level = LEVEL_4  # Level 3 leads to Level 4
LEVEL_4.next_level = LEVEL_5  # Level 4 leads to Level 5
LEVEL_5.next_level = LEVEL_6  # Level 5 leads to Level 6
LEVEL_6.next_level = LEVEL_3  # Level 6 loops back to Level 3

# Set Level 3 as the starting level
ROOT_LEVEL = LEVEL_3

# Export all levels for access by other modules
LEVELS = [LEVEL_3, LEVEL_4, LEVEL_5, LEVEL_6]