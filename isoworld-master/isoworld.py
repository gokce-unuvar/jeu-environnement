#
# Symbiotica


#
# Requirements: Python3, Pygame
#
# Credits for third party resources used in this project:
# - Assets: https://www.kenney.nl/ (great assets by Kenney Vleugels with *public domain license*)
# - https://www.uihere.com/free-cliparts/space-invaders-extreme-2-video-game-arcade-game-8-bit-space-invaders-3996521
#
# Random bookmarks:
# - scaling images: https://stackoverflow.com/questions/43196126/how-do-you-scale-a-design-resolution-to-other-resolutions-with-pygame
# - thoughts on grid worlds: http://www-cs-students.stanford.edu/~amitp/game-programming/grids/
# - key pressed? https://stackoverflow.com/questions/16044229/how-to-get-keyboard-input-in-pygame
# - basic example to display tiles: https://stackoverflow.com/questions/20629885/how-to-render-an-isometric-tile-based-world-in-python
# - pygame key codes: https://www.pygame.org/docs/ref/key.html
# - pygame capture key combination: https://stackoverflow.com/questions/24923078/python-keydown-combinations-ctrl-key-or-shift-key
# - methods to initialize a 2D array: https://stackoverflow.com/questions/2397141/how-to-initialize-a-two-dimensional-array-in-python
# - bug with SysFont - cf. https://www.reddit.com/r/pygame/comments/1fhq6d/pygamefontsysfont_causes_my_script_to_freeze_why/
#       myfont = pygame.font.SysFont(pygame.font.get_default_font(), 16)
#       myText = myfont.render("Hello, World", True, (0, 128, 0))
#       screen.blit(myText, (screenWidth/2 - text.get_width() / 2, screenHeight/2 - text.get_height() / 2))
#       ... will fail.
#
# TODO list
# - double buffer
# -.multiple agents


import sys
import datetime
from random import *
import math
import time

import pygame
from pygame.locals import *

###

versionTag = "2025-04-10_15h06"

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
###
### PARAMETERS: simulation
###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# all values are for initialisation. May change during runtime.
nbTrees = 100 #350
nbBurningTrees = 7 #15
nbPredators = 5
nbRobots = 5
nbHumans = 5
nbEvilRobots = 0
nbBuilding = 2

# These could be used later for visuals, or logic, or just to distinguish different agents
noAgentId = 0
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
###
### PARAMETERS: rendering
###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# display screen dimensions
screenWidth = 1400 # 1400 - 930
screenHeight = 900 #900 - 640

# world dimensions (ie. nb of cells in total)
worldWidth = 50#64
worldHeight = 50#64

# set surface of displayed tiles (ie. nb of cells that are rendered) -- must be superior to worldWidth and worldHeight
viewWidth = 50#32
viewHeight = 50#32

scaleMultiplier = 0.25 # re-scaling of loaded images

objectMapLevels = 10 # number of levels for the objectMap. This determines how many objects you can pile upon one another.

# set scope of displayed tiles
xViewOffset = 0
yViewOffset = 0

addNoise = False

maxFps = 30 # set up maximum number of frames-per-second

verbose = False # display message in console on/off
verboseFps = True # display FPS every once in a while

burning_trees = {}  # Dictionnaire qui stocke (x, y) -> temps depuis qu'il brûle
burn_time = 5 * maxFps  # Durée avant que l'arbre brûlé apparaisse (ex: 5 secondes)
burnt_time = 10 *maxFps
tree_reproduction_chance = 0.005  # 1% de chance par cycle de reproduction
proba_brule = 0.001
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
###
### setting up Pygame/SDL
###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

pygame.init()
#pygame.key.set_repeat(5,5)
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((screenWidth, screenHeight), DOUBLEBUF)
pygame.display.set_caption('Symbiotica')

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
###
### CORE/USER: Image management
###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def loadImage(filename):
    global tileTotalWidthOriginal,tileTotalHeightOriginal,scaleMultiplier
    image = pygame.image.load(filename).convert_alpha()
    image = pygame.transform.scale(image, (int(tileTotalWidthOriginal*scaleMultiplier), int(tileTotalHeightOriginal*scaleMultiplier)))
    return image

def loadImageBuilding(filename):
    global tileTotalWidthOriginal,tileTotalHeightOriginal
    image = pygame.image.load(filename).convert_alpha()
    image = pygame.transform.scale(image, (int(tileTotalWidthOriginal*1.5), int(tileTotalHeightOriginal*1.5)))
    return image

def loadAllImages():
    global tileType, objectType, agentType

    tileType = []
    objectType = []
    agentType = []

    tileType.append(loadImage('assets/basic111x128/platformerTile_3169.png')) # grass 
    tileType.append(loadImage('assets/ext/isometric-blocks/PNG/Platformer tiles/platformerTile_33.png')) # brick
    tileType.append(loadImage('assets/ext/isometric-blocks/PNG/Platformer tiles/platformerTile_18.png')) # je l'ai modifie 
    tileType.append(loadImage('assets/ext/isometric-blocks/PNG/Abstract tiles/abstractTile_09.png')) # grey brock

    objectType.append(None) # default -- never drawn
    objectType.append(loadImage('assets/basic111x128/summer_tree.png')) # normal tree 
    objectType.append(loadImage('assets/basic111x128/platformerTile_18.png')) # construction block
    objectType.append(loadImage('assets/basic111x128/arbre_brule.png')) # burning tree
    objectType.append(loadImageBuilding('assets/basic111x128/building.png')) #immeuble
    objectType.append(loadImageBuilding('assets/basic111x128/factory.png')) #usine
    objectType.append(loadImage('assets/basic111x128/baby.png')) # burnt tree

    agentType.append(None) # default -- never drawn
    agentType.append(loadImage('assets/basic111x128/player.png')) # invader -> player
    agentType.append(loadImage('assets/basic111x128/wolf.png')) # purple ghost -> wolf
    agentType.append(loadImage('assets/basic111x128/woman.png')) # baby -> human
    agentType.append(loadImage('assets/basic111x128/robot.png'))
    agentType.append(loadImage('assets/basic111x128/evil_robot.png'))


def resetImages():
    global tileTotalWidth, tileTotalHeight, tileTotalWidthOriginal, tileTotalHeightOriginal, scaleMultiplier, heightMultiplier, tileVisibleHeight
    tileTotalWidth = tileTotalWidthOriginal * scaleMultiplier  # width of tile image, as stored in memory
    tileTotalHeight = tileTotalHeightOriginal * scaleMultiplier # height of tile image, as stored in memory
    tileVisibleHeight = tileVisibleHeightOriginal * scaleMultiplier # height "visible" part of the image, as stored in memory
    heightMultiplier = tileTotalHeight/2 # should be less than (or equal to) tileTotalHeight
    loadAllImages()
    return

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
###
### CORE: objects parameters
###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# spritesheet-specific -- as stored on the disk ==> !!! here, assume 128x111 with 64 pixels upper-surface !!!
# Values will be updated *after* image loading and *before* display starts
tileTotalWidthOriginal = 111  # width of tile image
tileTotalHeightOriginal = 128 # height of tile image
tileVisibleHeightOriginal = 64 # height "visible" part of the image, i.e. top part without subterranean part

###

tileType = []
objectType = []
agentType = []

noObjectId = noAgentId = 0
#tiles
grassId = 0
blockId = 2

#objetcs
treeId = 1
burningTreeId = 3
building = 4
factory = 5
burntTreeId = 6 #len(objectType) - 1
#agents
playerId = 1
humanId = 3
robotId = 4
evilRobotId = 5  # Evil robot will have a different ID
predatorId = 2


###

# re-scale reference image size -- must be done *after* loading sprites
resetImages()

###

terrainMap = [x[:] for x in [[0] * worldWidth] * worldHeight]
heightMap  = [x[:] for x in [[0] * worldWidth] * worldHeight]
objectMap = [ [ [ 0 for i in range(worldWidth) ] for j in range(worldHeight) ] for k in range(objectMapLevels) ]
agentMap   = [x[:] for x in [[0] * worldWidth] * worldHeight]

###

# set initial position for display on screen
xScreenOffset = screenWidth/2 - tileTotalWidth/2
yScreenOffset = 3*tileTotalHeight # border. Could be 0.

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### CORE: get/set methods
###
###

def displayWelcomeMessage():

    print ("")
    print ("=-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-=")
    print ("=-=                 Symbiotica                  =-=")
    print ("=-=                                             =-=")
    print ("=-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-=")
    print (">> v.",versionTag)
    print ("")

    print ("Screen resolution : (",screenWidth,",",screenHeight,")")
    print ("World surface     : (",worldWidth,",",worldHeight,")")
    print ("View surface      : (",viewWidth,",",viewHeight,")")
    print ("Verbose all       :",verbose)
    print ("Verbose fps       :",verboseFps)
    print ("Maximum fps       :",maxFps)
    print ("")

    print ("# Hotkeys:")
    print ("\tcursor keys : move around (use shift for tile-by-tile move)")
    print ("\tv           : verbose mode")
    print ("\tf           : display frames-per-second")
    print ("\to           : decrease view surface")
    print ("\tO           : increase view surface")
    print ("\te           : decrease scaling")
    print ("\tE           : increase scaling")
    print ("\tESC         : quit")
    print ("")

    return

def getWorldWidth():
    return worldWidth

def getWorldHeight():
    return worldHeight

def getViewWidth():
    return viewWidth

def getViewHeight():
    return viewHeight

def getTerrainAt(x,y):
    return terrainMap[y][x]

def setTerrainAt(x,y,type):
    terrainMap[y][x] = type

def getHeightAt(x,y):
    return heightMap[y][x]

def setHeightAt(x,y,height):
    heightMap[y][x] = height

def getObjectAt(x,y,level=0):
    if level < objectMapLevels:
        return objectMap[level][y][x]
    else:
        print ("[ERROR] getObjectMap(.) -- Cannot return object. Level does not exist.")
        return 0

def setObjectAt(x,y,type,level=0): # negative values are possible: invisible but tangible objects (ie. no display, collision)
    if level < objectMapLevels:
        objectMap[level][y][x] = type
    
    else:
        print ("[ERROR] setObjectMap(.) -- Cannot set object. Level does not exist.")
        return 0

def getAgentAt(x,y):
    return agentMap[y][x]

def setAgentAt(x,y,type):
    agentMap[y][x] = type

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### CORE: rendering
###
###

def render( it = 0 ):
    global xViewOffset, yViewOffset

    pygame.draw.rect(screen, (0,0,0), (0, 0, screenWidth, screenHeight), 0) # overkill - can be optimized. (most sprites are already "naturally" overwritten)
    #pygame.display.update()

    for y in range(getViewHeight()):
        for x in range(getViewWidth()):
            # assume: north-is-upper-right

            xTile = ( xViewOffset + x + getWorldWidth() ) % getWorldWidth()
            yTile = ( yViewOffset + y + getWorldHeight() ) % getWorldHeight()

            heightNoise = 0
            if addNoise == True: # add sinusoidal noise on height positions
                if it%int(math.pi*2*199) < int(math.pi*199):
                    # v1.
                    heightNoise = math.sin(it/23+yTile) * math.sin(it/7+xTile) * heightMultiplier/10 + math.cos(it/17+yTile+xTile) * math.cos(it/31+yTile) * heightMultiplier
                    heightNoise = math.sin(it/199) * heightNoise
                else:
                    # v2.
                    heightNoise = math.sin(it/13+yTile*19) * math.cos(it/17+xTile*41) * heightMultiplier
                    heightNoise = math.sin(it/199) * heightNoise

            height = getHeightAt( xTile , yTile ) * heightMultiplier + heightNoise

            xScreen = xScreenOffset + x * tileTotalWidth / 2 - y * tileTotalWidth / 2
            yScreen = yScreenOffset + y * tileVisibleHeight / 2 + x * tileVisibleHeight / 2 - height

            screen.blit( tileType[ getTerrainAt( xTile , yTile ) ] , (xScreen, yScreen)) # display terrain

            for level in range(objectMapLevels):
                if getObjectAt( xTile , yTile , level)  > 0: # object on terrain?
                    screen.blit( objectType[ getObjectAt( xTile , yTile, level) ] , (xScreen, yScreen - heightMultiplier*(level+1) ))

            if getAgentAt( xTile, yTile ) != 0: # agent on terrain?
                screen.blit( agentType[ getAgentAt( xTile, yTile ) ] , (xScreen, yScreen - heightMultiplier ))
            
            #print(f"Agent at ({xTile}, {yTile}): {getAgentAt( xTile, yTile )}")  # Debugging print
            
    return

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### Agents
###
###

class BasicAgent:

    def __init__(self,imageId):
        self.type = imageId
        self.reset()
        return

    def reset(self):
        self.x = randint(0,getWorldWidth()-1)
        self.y = randint(0,getWorldWidth()-1)
        while getTerrainAt(self.x,self.y) != 0 or getObjectAt(self.x,self.y) != 0 or getAgentAt(self.x,self.y) != 0:
            self.x = randint(0,getWorldWidth()-1)
            self.y = randint(0,getWorldHeight()-1)
        setAgentAt(self.x,self.y,self.type)
        return

    def getPosition(self):
        return (self.x,self.y)

    def move(self):
        xNew = self.x
        yNew = self.y
        if random() < 0.5:
            xNew = ( self.x + [-1,+1][randint(0,1)] + getWorldWidth() ) % getWorldWidth()
        else:
            yNew = ( self.y + [-1,+1][randint(0,1)] + getWorldHeight() ) % getWorldHeight()
        if getObjectAt(xNew,yNew) == 0: # dont move if collide with object (note that negative values means cell cannot be walked on)
            setAgentAt(self.x,self.y,noAgentId)
            self.x = xNew
            self.y = yNew
            setAgentAt(self.x,self.y,self.type)
        if verbose == True:
            print ("agent of type ",str(self.type),"located at (",self.x,",",self.y,")")
        return


    def move2(self,xNew,yNew):
        success = False
        if getObjectAt( (self.x+xNew+worldWidth)%worldWidth , (self.y+yNew+worldHeight)%worldHeight ) == 0: # dont move if collide with object (note that negative values means cell cannot be walked on)
            setAgentAt( self.x, self.y, noAgentId)
            self.x = ( self.x + xNew + worldWidth ) % worldWidth
            self.y = ( self.y + yNew + worldHeight ) % worldHeight
            setAgentAt( self.x, self.y, self.type)
            success = True
        if verbose == True:
            if success == False:
                print ("agent of type ",str(self.type)," cannot move.")
            else:
                print ("agent of type ",str(self.type)," moved to (",self.x,",",self.y,")")
        return


    def getType(self):
        return self.type


#agents = []
predators = []
humans = []
robots = []


class Human:
    def __init__(self, imageId):
        self.type = imageId
        self.reset()

    def reset(self):
        """Place l'humain aléatoirement dans le monde"""
        self.x = randint(0, getWorldWidth() - 1)
        self.y = randint(0, getWorldHeight() - 1)
        while getTerrainAt(self.x, self.y) != 0 or getObjectAt(self.x, self.y) != 0 or getAgentAt(self.x, self.y) != 0:
            self.x = randint(0, getWorldWidth() - 1)
            self.y = randint(0, getWorldHeight() - 1)
        setAgentAt(self.x, self.y, self.type)
        return

    def move(self):
        """Bouge aléatoirement l'humain dans le monde dans une des quatre directions"""
        xNew, yNew = self.x, self.y
        if random() < 0.5:
            xNew = (self.x + [-1, +1][randint(0, 1)] + getWorldWidth()) % getWorldWidth()
        else:
            yNew = (self.y + [-1, +1][randint(0, 1)] + getWorldHeight()) % getWorldHeight()

        if getObjectAt(xNew, yNew) == 0:  # Can only move if no obstacle
            setAgentAt(self.x, self.y, noAgentId)
            self.x, self.y = xNew, yNew
            setAgentAt(self.x, self.y, self.type)
        return


    def reproduce(self, humans, reproduction_chance=0.01):
        """Les humains se reproduisent avec une probabilité"""
        if random() < reproduction_chance:
            new_x = (self.x + [-1, 0, 1][randint(0, 2)] + getWorldWidth()) % getWorldWidth()
            new_y = (self.y + [-1, 0, 1][randint(0, 2)] + getWorldHeight()) % getWorldHeight()
            if getAgentAt(new_x, new_y) == 0:  # Only reproduce if space is free
                humans.append(Human(self.type))
                humans[-1].x, humans[-1].y = new_x, new_y
                setAgentAt(new_x, new_y, self.type)
        return 


class Robot:
    def __init__(self, imageId):
        self.type = imageId
        self.reset()
        self.evil = False  # Starts peaceful

    def reset(self):
        """Place le robot aléatoirement dans le monde"""
        self.x = randint(0, getWorldWidth() - 1)
        self.y = randint(0, getWorldHeight() - 1)
        while getTerrainAt(self.x, self.y) != 0 or getObjectAt(self.x, self.y) != 0 or getAgentAt(self.x, self.y) != 0:
            self.x = randint(0, getWorldWidth() - 1)
            self.y = randint(0, getWorldHeight() - 1)
        setAgentAt(self.x, self.y, self.type)
        return

    def move(self):
        """Bouge aléatoirement le robot dans le monde dans une des quatre directions."""
        xNew, yNew = self.x, self.y
        if random() < 0.5:
            xNew = (self.x + [-1, +1][randint(0, 1)] + getWorldWidth()) % getWorldWidth()
        else:
            yNew = (self.y + [-1, +1][randint(0, 1)] + getWorldHeight()) % getWorldHeight()

        if getObjectAt(xNew, yNew) == 0:  # Can only move if no obstacle
            setAgentAt(self.x, self.y, noAgentId)
            self.x, self.y = xNew, yNew
            setAgentAt(self.x, self.y, self.type)
        return

    def turn_evil(self, probability=0.005):
        """Peux de chance de devenir méchant et d'attaquer les humains"""
        if not self.evil and random() < probability:
            self.evil = True
            self.type = evilRobotId  # Change appearance
        return

    def attack_human(self, humans):
        """Si mechant, tue l'humain"""
        if self.evil:
            for human in humans:
                if human.x == self.x and human.y == self.y:
                    humans.remove(human)  # tue l'humain
                    break  # Tue un humain a la fois
        return

    def attack_predator(self, predators, probability = 0.5):
        """Si gentil, tue les predateurs avec une probabilite pour proteger les humains"""
        if not self.evil and random() < probability :
            for predator in predators:
                if predator.x == self.x and predator.y == self.y:
                    predators.remove(predator)  # tue le predateur
                    break  # tue un predateur a la fois
        return

    def reproduce(self, robots, reproduction_chance=0.00002):
        """Les humains se reproduisent avec une probabilité"""
        if random() < reproduction_chance:
            new_x = 31
            new_y = 31
            if getAgentAt(new_x, new_y) == 0:  # Only reproduce if space is free
                robots.append(Robot(self.type))
                robots[-1].x, robots[-1].y = new_x, new_y
                setAgentAt(new_x, new_y, self.type)
        return        

class Predator:
    def __init__(self, imageId):
        self.type = imageId
        self.reset()

    def reset(self):
        """Place le predateur aléatoirement dans le monde"""
        self.x = randint(0, getWorldWidth() - 1)
        self.y = randint(0, getWorldHeight() - 1)
        while getTerrainAt(self.x, self.y) != 0 or getObjectAt(self.x, self.y) != 0 or getAgentAt(self.x, self.y) != 0:
            self.x = randint(0, getWorldWidth() - 1)
            self.y = randint(0, getWorldHeight() - 1)
        setAgentAt(self.x, self.y, self.type)
        return

    def move(self):
        """Bouge aléatoirement le predateur dans le monde dans une des quatre directions"""
        xNew, yNew = self.x, self.y
        if random() < 0.5:
            xNew = (self.x + [-1, +1][randint(0, 1)] + getWorldWidth()) % getWorldWidth()
        else:
            yNew = (self.y + [-1, +1][randint(0, 1)] + getWorldHeight()) % getWorldHeight()

        if getObjectAt(xNew, yNew) == 0:  # Can only move if no obstacle
            setAgentAt(self.x, self.y, noAgentId)
            self.x, self.y = xNew, yNew
            setAgentAt(self.x, self.y, self.type)
        return

    def hunt(self, humans):
        """Tue un humain si sur la même case."""
        for human in humans:
            if human.x == self.x and human.y == self.y:
                humans.remove(human)  # Tue l'humain
                break  # Tue un seul a la fois
        return

    def reproduce(self, predators, reproduction_chance=0.02):
        """Les humains se reproduisent avec une probabilité"""
        if random() < reproduction_chance:
            new_x = (self.x + [-1, 0, 1][randint(0, 2)] + getWorldWidth()) % getWorldWidth()
            new_y = (self.y + [-1, 0, 1][randint(0, 2)] + getWorldHeight()) % getWorldHeight()
            if getAgentAt(new_x, new_y) == 0:  # Only reproduce if space is free
                predators.append(Predator(self.type))
                predators[-1].x, predators[-1].y = new_x, new_y
                setAgentAt(new_x, new_y, self.type)
        return



### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### Initialise world
###
###

def initWorld():
    global nbTrees, nbBurningTrees, predators, humans, robots
    '''
    # add a pyramid-shape building
    building1TerrainMap = [
    [ 2, 2, 2, 2 ],
    [ 2, 3, 3, 2 ],
    [ 2, 3, 3, 2 ],
    [ 2, 2, 2, 2 ]
    ]
    building1HeightMap = [
    [ 1, 1, 1, 1 ],
    [ 1, 2, 2, 1 ],
    [ 1, 2, 2, 1 ],
    [ 1, 1, 1, 1 ]
    ]
    
    x_offset = 3
    y_offset = 3
    for x in range( len( building1TerrainMap[0] ) ):
        for y in range( len( building1TerrainMap ) ):
            setTerrainAt( x+x_offset, y+y_offset, building1TerrainMap[x][y] )
            setHeightAt( x+x_offset, y+y_offset, building1HeightMap[x][y] )
            setObjectAt( x+x_offset, y+y_offset, -1 ) # add a virtual object: not displayed, but used to forbid agent(s) to come here.
    '''
    # add another pyramid-shape building with a tree on top
    building2TerrainMap = [
    [ 0, 2, 2, 2, 2, 2, 0 ],
    [ 2, 2, 2, 2, 2, 2, 2 ],
    [ 2, 2, 2, 2, 2, 2, 2 ],
    [ 2, 2, 2, 2, 2, 2, 2 ],
    [ 2, 2, 2, 2, 2, 2, 2 ],
    [ 2, 2, 2, 2, 2, 2, 2 ],
    [ 2, 2, 2, 2, 2, 2, 2 ],
    [ 2, 2, 2, 2, 2, 2, 2 ],
    [ 0, 2, 2, 2, 2, 2, 0 ]
    ]
    building2HeightMap = [
    [ 0, 1, 1, 1, 1, 1, 0 ],
    [ 1, 1, 1, 1, 1, 1, 1 ],
    [ 1, 2, 2, 2, 2, 2, 1 ],
    [ 1, 2, 3, 3, 3, 2, 1 ],
    [ 1, 2, 3, 4, 3, 2, 1 ],
    [ 1, 2, 3, 3, 3, 2, 1 ],
    [ 1, 2, 2, 2, 2, 2, 1 ],
    [ 1, 1, 1, 1, 1, 1, 1 ],
    [ 0, 1, 1, 1, 1, 1, 0 ]
    ]
    x_offset = 4
    y_offset = 13
    for x in range( len( building2TerrainMap[0] ) ):
        for y in range( len( building2TerrainMap ) ):
            setTerrainAt( x+x_offset, y+y_offset, building2TerrainMap[y][x] )
            setHeightAt( x+x_offset, y+y_offset, building2HeightMap[y][x] )
            setObjectAt( x+x_offset, y+y_offset, -1 ) # add a virtual object: not displayed, but used to forbid agent(s) to come here.
    setObjectAt( x_offset+3, y_offset+4, treeId )
    '''
    for c in [(20,2),(30,2),(30,12),(20,12)]: # position des poteaux orange
        for level in range(0,objectMapLevels):
            setObjectAt(c[0],c[1],blockId,level)
    for i in range(9):
        setObjectAt(21+i,2,blockId,objectMapLevels-1)
        setObjectAt(21+i,12,blockId,objectMapLevels-1)
        setObjectAt(20,3+i,blockId,objectMapLevels-1)
        setObjectAt(30,3+i,blockId,objectMapLevels-1)
    '''
    #ajout immeuble
    building_width =  5 # Largeur 
    building_height = 2 #et hauteur de l'immeuble en nombre de cases

    for i in range(nbBuilding):
        x = randint(0, getWorldWidth() - building_width)
        y = randint(0, getWorldHeight() - building_height)

        # Vérifie que toutes les cases sont libres
        while any(getTerrainAt(x + dx, y + dy) != 0 or getObjectAt(x + dx, y + dy) != 0 
                for dx in range(building_width) for dy in range(building_height)):
            x = randint(0, getWorldWidth() - building_width)
            y = randint(0, getWorldHeight() - building_height)

        # Place l'immeuble sur toutes ses cases
        setObjectAt(x, y, building, 7)
        for dx in range(1,building_width):
            for dy in range(1,building_height):
                setObjectAt(x + dx, y + dy, 0, 7)


    #ajout usine
    x = 5
    y = 35
    setObjectAt(x,y,factory, 9)

    


    #ajout predateurs dans le monde
    for i in range(nbPredators):
        predators.append(Predator(predatorId))
    
    #ajout humains dans le monde
    for i in range(nbHumans):
        humans.append(Human(humanId))

    #ajout robots dans le monde

    for i in range(nbRobots):
        robots.append(Robot(robotId))

    #ajout arbres
    for i in range(nbTrees):
        x = randint(0,getWorldWidth()-1)
        y = randint(0,getWorldHeight()-1)
        while getTerrainAt(x,y) != 0 or getObjectAt(x,y) != 0:
            x = randint(0,getWorldWidth()-1)
            y = randint(0,getWorldHeight()-1)
        setObjectAt(x,y,treeId)


    #ajout arbres brules
    for i in range(nbBurningTrees):
        x = randint(0,getWorldWidth()-1)
        y = randint(0,getWorldHeight()-1)
        while getTerrainAt(x,y) != 0 or getObjectAt(x,y) != 0:
            x = randint(0,getWorldWidth()-1)
            y = randint(0,getWorldHeight()-1)
        setObjectAt(x,y,burningTreeId)
        burning_trees[(x,y)] = 0

    return

### ### ### ### ###

def initAgents():
    return

### ### ### ### ###
def stepWorld(it=0):
    if it % (maxFps / 10) == 0:
        new_trees = []  # Liste des nouveaux arbres à planter

        for x in range(worldWidth):
            for y in range(worldHeight):
                # Propagation du feu
                if getObjectAt(x, y) == treeId:
                    for neighbours in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
                        nx = (x + neighbours[0] + worldWidth) % worldWidth
                        ny = (y + neighbours[1] + worldHeight) % worldHeight
                        if getObjectAt(nx, ny) == burningTreeId or getAgentAt(nx, ny) == evilRobotId:
                            setObjectAt(x, y, burningTreeId)
                            burning_trees[(x, y)] = it  # Enregistre le moment où il brûle
                    if random() < proba_brule : #arbre brule aléatoirement
                        setObjectAt(x,y,burningTreeId)
                        burning_trees[(x, y)] = it

                    # Reproduction des arbres
                    if random() < tree_reproduction_chance:
                        for neighbours in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
                            nx = (x + neighbours[0] + worldWidth) % worldWidth
                            ny = (y + neighbours[1] + worldHeight) % worldHeight
                            if getObjectAt(nx, ny) == 0 and getTerrainAt(nx, ny) == 0:  # Vérifie que la case est vide
                                new_trees.append((nx, ny))  # Ajouter un nouvel arbre
                                break  # Un seul nouvel arbre par cycle

                                       
                # Transformation des arbres en feu en cendres
                elif getObjectAt(x, y) == burningTreeId:
                    if (x, y) in burning_trees and it - burning_trees[(x, y)] >= burn_time:
                        setObjectAt(x, y, burntTreeId)
                        #del burning_trees[(x, y)]
                
                elif getObjectAt(x,y) ==  burntTreeId:
                    if (x, y) in burning_trees and it - burning_trees[(x, y)] >= burnt_time:
                        setObjectAt(x, y, 0)
                        del burning_trees[(x, y)]
                
        # Ajouter les nouveaux arbres
        for x, y in new_trees:
            setObjectAt(x, y, treeId)


### ### ### ### ###

def stepAgents( it = 0 ):
    # move agent
    if it % (maxFps/10) == 0:
        #shuffle(agents)
        shuffle(predators)
        shuffle(humans)
        shuffle(robots)
        for h in humans:   # shuffle agents in in-place (i.e. agents is modified)
            h.move()
        for p in predators :
            p.move()
        for r in robots :
            r.move()
    return


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### MAIN
###
###


# Example of how to use these classes in a simulation loop
#humans = [Human(humanId) for _ in range(5)]  # Start with 5 humans
#robots = [Robot(robotId) for _ in range(3)]  # Start with 3 robots
#predators = [Predator(predatorId) for _ in range(2)]  # Start with 2 predators

for _ in range(100):  # Simulate 100 time steps
    for human in humans:
        human.move()
        #IF NBARBRE < 31 (PAR EXEMPLE) THEN HUMAINS PEUVENT PAS SE REPRODUIRE
        human.reproduce(humans)

    for robot in robots:
        robot.move()
        robot.turn_evil()
        robot.attack_human(humans)
        robot.attack_predator(predators)
        robot.reproduce(robots)

    for predator in predators:
        predator.move()
        predator.hunt(humans)
        predator.reproduce(predators)


timestamp = datetime.datetime.now().timestamp()

loadAllImages()

displayWelcomeMessage()

initWorld()
initAgents()

player = BasicAgent(playerId) #A CHANGER PARCE QUE PLUS DE BASIC AGENT

print ("initWorld:",datetime.datetime.now().timestamp()-timestamp,"second(s)")
timeStampStart = timeStamp = datetime.datetime.now().timestamp()

it = itStamp = 0

userExit = False

while userExit == False:

    if it != 0 and it % 100 == 0 and verboseFps:
        print ("[fps] ", ( it - itStamp ) / ( datetime.datetime.now().timestamp()-timeStamp ) )
        timeStamp = datetime.datetime.now().timestamp()
        itStamp = it

    #screen.blit(pygame.font.render(str(currentFps), True, (255,255,255)), (screenWidth-100, screenHeight-50))


#
    render(it)

    stepWorld(it)

    '''
    perdu = False
    for a in agents:
        if a.getPosition() == player.getPosition():
            perdu = True
            break
    '''
    stepAgents(it)

    '''
    for a in agents:
        if a.getPosition() == player.getPosition():
            perdu = True
            break

    if perdu == True:
        print ("")
        print ("#### #### #### #### ####")
        print ("####                ####")
        print ("####     PERDU !    ####")
        print ("####                ####")
        print ("#### #### #### #### ####")
        print ("")
        print (">>> Score:",it,"--> BRAVO! ")
        print ("")
        pygame.quit()
        sys.exit()
    
    #reproduction des ghosts
    if it % 10 == 0:
        agents.append(BasicAgent(ghostId))
    '''
    # continuous stroke
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ):
        xViewOffset  = (xViewOffset - 1 + getWorldWidth() ) % getWorldWidth()
        if verbose:
            print("View at (",xViewOffset ,",",yViewOffset,")")
    elif keys[pygame.K_RIGHT] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ):
        xViewOffset = (xViewOffset + 1 ) % getWorldWidth()
        if verbose:
            print("View at (",xViewOffset ,",",yViewOffset,")")
    elif keys[pygame.K_DOWN] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ):
        yViewOffset = (yViewOffset + 1 ) % getWorldHeight()
        if verbose:
            print("View at (",xViewOffset,",",yViewOffset,")")
    elif keys[pygame.K_UP] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ):
        yViewOffset = (yViewOffset - 1 + getWorldHeight() ) % getWorldHeight()
        if verbose:
            print("View at (",xViewOffset,",",yViewOffset,")")

    # single stroke
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                userExit = True
            elif event.key == pygame.K_q:
                player.move2(0,+1)
            elif event.key == pygame.K_z:
                player.move2(0,-1)
            elif event.key == pygame.K_d:
                player.move2(+1,0)
            elif event.key == pygame.K_s:
                player.move2(-1,0)
            elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                addNoise = not(addNoise)
                print ("noise is",addNoise) # easter-egg
            elif event.key == pygame.K_v:
                verbose = not(verbose)
                print ("verbose is",verbose)
            elif event.key == pygame.K_f:
                verboseFps = not(verboseFps)
                print ("verbose FPS is",verboseFps)
            elif event.key == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                xViewOffset  = (xViewOffset - 1 + getWorldWidth() ) % getWorldWidth()
                if verbose:
                    print("View at (",xViewOffset ,",",yViewOffset,")")
            elif event.key == pygame.K_RIGHT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                xViewOffset = (xViewOffset + 1 ) % getWorldWidth()
                if verbose:
                    print("View at (",xViewOffset ,",",yViewOffset,")")
            elif event.key == pygame.K_DOWN and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                yViewOffset = (yViewOffset + 1 ) % getWorldHeight()
                if verbose:
                    print("View at (",xViewOffset,",",yViewOffset,")")
            elif event.key == pygame.K_UP and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                yViewOffset = (yViewOffset - 1 + getWorldHeight() ) % getWorldHeight()
                if verbose:
                    print("View at (",xViewOffset,",",yViewOffset,")")
            elif event.key == pygame.K_o and not( pygame.key.get_mods() & pygame.KMOD_SHIFT ) :
                if viewWidth > 1:
                    viewWidth = int(viewWidth / 2)
                    viewHeight = int(viewHeight / 2)
                    print (viewWidth)
                if verbose:
                    print ("View surface is (",viewWidth,",",viewHeight,")")
            elif event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                if viewWidth < worldWidth :
                    viewWidth = viewWidth * 2
                    viewHeight = viewHeight * 2
                if verbose:
                    print ("View surface is (",viewWidth,",",viewHeight,")")
            elif event.key == pygame.K_e and not( pygame.key.get_mods() & pygame.KMOD_SHIFT ) :
                if scaleMultiplier > 0.125:
                    scaleMultiplier = scaleMultiplier / 2
                if scaleMultiplier < 0.125:
                    scaleMultiplier = 0.125
                resetImages()
                if verbose:
                    print ("scaleMultiplier is ",scaleMultiplier)
            elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                if scaleMultiplier < 1.0:
                    scaleMultiplier = scaleMultiplier * 2
                if scaleMultiplier > 1.0:
                    scaleMultiplier = 1.0
                resetImages()
                if verbose:
                    print ("scaleMultiplier is ",scaleMultiplier)

    pygame.display.flip()
    fpsClock.tick(maxFps) # recommended: 30 fps

    it += 1

fps = it / ( datetime.datetime.now().timestamp()-timeStampStart )
print ("[Quit] (", fps,"frames per second )")

pygame.quit()
sys.exit()
