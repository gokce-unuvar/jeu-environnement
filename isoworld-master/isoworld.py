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

import matplotlib.pyplot as plt

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

global nbTrees, nbBurntTrees, nbPredators, nbRobots, nbHumans, nbEvilRobots, nbBuilding

nbTrees = 100 #350 - 131
nbBurntTrees = 7 #15 - 7
nbPredators = 8 #6
nbRobots = 4 #4
nbHumans = 10 #7
nbEvilRobots = 0
nbBuilding = 2

history_humans = []
history_predators = []
history_robots = []
history_evil_robots = []
history_trees = []
history_burning_trees = []



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

objectMapLevels = 11 # number of levels for the objectMap. This determines how many objects you can pile upon one another.

# set scope of displayed tiles
xViewOffset = 0
yViewOffset = 0

addNoise = False

maxFps = 30 # set up maximum number of frames-per-second

verbose = False # display message in console on/off
verboseFps = True # display FPS every once in a while

#arbres
burning_trees = {}  # Dictionnaire qui stocke (x, y) -> temps depuis qu'il brûle
burning_agents= {}
burning_time = 5 * maxFps  # Durée avant que l'arbre brûlé apparaisse 
burnt_time = 10 *maxFps
proba_rep_tree = 0.0005 
proba_brule = 0.0005 #0.0005
proba_voisin_brule = 0.05 #0.05

#agents
proba_evil_brule = 0.05
proba_turn_evil = 0.01
proba_agent_brule = 0.7
proba_rep_hum = 0.003
proba_rep_pred = 0.001
proba_fabrication_robots = 0.009
proba_attack_pred = 1
human_speed = 6      # toutes les 2 frames
predator_speed = 4   # toutes les 3 frames
robot_speed = 3      # toutes les 5 frames


#earthquake
proba_earthq = 0.2
is_earthquake_active = False
earthquake_end_time = 0
earthquake_initial_delay = 50 * maxFps  # 40 secondes avant que le tremblement de terre peut etre vrai
earthquake_cooldown = 80 * maxFps     # 80 secondes entre chaque tremblement de terre
next_earthquake_time = earthquake_initial_delay  # le temps d'attente pour le prochain tremblement de terre
earthq_time = 30 *maxFps #40

#innondation
proba_flood_after_earthquake = 0.7 
flood_active = False
flood_duration = 30 * maxFps  # la durée de l'inondation
flood_spread_interval = 10  # Spread every 10 frames
flood_end_time=0
next_flood_spread = 0

last_building_count = 0
building_placed = False

#Pour les saisons
SEASONS = ["SPRING", "SUMMER", "AUTUMN", "WINTER"]
current_season_index = 0
current_season = SEASONS[current_season_index]
season_duration = 30 * maxFps  # 30 saniye (maxFps frame/saniye)
season_timer = 0

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
    image = pygame.transform.scale(image, (int(tileTotalWidthOriginal*scaleMultiplier*7), int(tileTotalHeightOriginal*scaleMultiplier*7)))
    return image

def loadImageFactory(filename):
    global tileTotalWidthOriginal,tileTotalHeightOriginal
    image = pygame.image.load(filename).convert_alpha()
    image = pygame.transform.scale(image, (int(tileTotalWidthOriginal*scaleMultiplier*6), int(tileTotalHeightOriginal*scaleMultiplier*6)))
    return image

def loadAllImages():
    global tileType, objectType, agentType, season_backgrounds, season_trees, season_man, season_woman, season_building, season_wolf, current_background, season_factory

    season_backgrounds = {
        "SPRING": pygame.transform.scale(pygame.image.load('assets/basic111x128/bg_spring.png').convert(), (screenWidth, screenHeight)),
        "SUMMER": pygame.transform.scale(pygame.image.load('assets/basic111x128/bg_summer.png').convert(), (screenWidth, screenHeight)),
        "AUTUMN": pygame.transform.scale(pygame.image.load('assets/basic111x128/bg_autumn.png').convert(), (screenWidth, screenHeight)),
        "WINTER": pygame.transform.scale(pygame.image.load('assets/basic111x128/bg_winter.png').convert(), (screenWidth, screenHeight))
    }
    current_background = season_backgrounds[current_season]

    season_trees = {
        "SPRING": 'assets/basic111x128/spring_tree.png',
        "SUMMER": 'assets/basic111x128/summer_tree.png',
        "AUTUMN": 'assets/basic111x128/autumn_tree.png',
        "WINTER": 'assets/basic111x128/winter_arbre.png'
    }
    season_man = {
        "SPRING": 'assets/basic111x128/man.png',
        "SUMMER": 'assets/basic111x128/man_summer.png',
        "AUTUMN": 'assets/basic111x128/man.png',
        "WINTER": 'assets/basic111x128/winter_man.png'
    }
    season_woman = {
        "SPRING": 'assets/basic111x128/woman.png',
        "SUMMER": 'assets/basic111x128/summer_woman.png',
        "AUTUMN": 'assets/basic111x128/woman.png',
        "WINTER": 'assets/basic111x128/winter_woman.png'
    }
    season_building = {
        "SPRING": 'assets/basic111x128/building.png',
        "SUMMER": 'assets/basic111x128/building.png',
        "AUTUMN": 'assets/basic111x128/building.png',
        "WINTER": 'assets/basic111x128/winter_building.png'
    }
    season_wolf = {
        "SPRING": 'assets/basic111x128/wolf.png',
        "SUMMER": 'assets/basic111x128/summer_wolf.png',
        "AUTUMN": 'assets/basic111x128/wolf.png',
        "WINTER": 'assets/basic111x128/winter_wolf.png'
    }
    season_factory = {
        "SPRING": 'assets/basic111x128/factory.png',
        "SUMMER": 'assets/basic111x128/factory.png',
        "AUTUMN": 'assets/basic111x128/factory.png',
        "WINTER": 'assets/basic111x128/winter_factory.png'
    }

    tileType = []
    objectType = []
    agentType = []

    tileType.append(loadImage('assets/basic111x128/platformerTile_3169.png')) # purple grass
    tileType.append(loadImage('assets/basic111x128/platformerTile_33.png')) # grey brock
    tileType.append(loadImage('assets/ext/isometric-blocks/PNG/Platformer tiles/platformerTile_18.png')) # light purple
    tileType.append(loadImage('assets/ext/isometric-blocks/PNG/Abstract tiles/abstractTile_09.png')) # dark grey brock
    tileType.append(loadImage('assets/basic111x128/abstractTile_26.png')) # water

    objectType.append(None) # default -- never drawn
    objectType.append(loadImage(season_trees[current_season]))  # normal tree
    objectType.append(loadImage('assets/basic111x128/platformerTile_18.png')) # construction block
    objectType.append(loadImage('assets/basic111x128/arbre_brule.png')) # burning tree
    objectType.append(loadImageBuilding(season_building[current_season])) #immeuble
    objectType.append(loadImageFactory(season_factory[current_season])) #usine
    objectType.append(loadImage('assets/basic111x128/arbre_mort.png')) # burnt tree


    agentType.append(None) # default -- never drawn
    agentType.append(loadImage('assets/basic111x128/player.png')) # invader -> player
    agentType.append(loadImage(season_wolf[current_season])) # wolf
    agentType.append(loadImage(season_woman[current_season])) # human
    agentType.append(loadImage('assets/basic111x128/robot.png'))
    agentType.append(loadImage('assets/basic111x128/robot_evil.png'))
    agentType.append(loadImage(season_man[current_season]))
    agentType.append(loadImage('assets/basic111x128/flame.png'))

def change_season():
    global current_season_index, current_season, current_background
    current_season_index = (current_season_index + 1) % len(SEASONS)
    current_season = SEASONS[current_season_index]
    loadAllImages()

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
roadId = 1
blockId = 2
waterId=4
#objetcs
treeId = 1
constructionBlockId = 2
burningTreeId = 3
buildingId = 4
factoryId = 5
burntTreeId = 6 #len(objectType) - 1


#agents
playerId = 1
womanId = 3
manId = 6
robotId = 4
evilRobotId = 5  # Evil robots ont une id différente
predatorId = 2
flameId = 7


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

    screen.blit(current_background, (0, 0))

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

class Player:

    def __init__(self,imageId):
        self.type = imageId
        self.reset()
        return

    def reset(self):
        self.x = randint(0,getWorldWidth()-1)
        self.y = randint(0,getWorldWidth()-1)
        while getTerrainAt(self.x,self.y) != 0 or getObjectAt(self.x,self.y) != 0 or getAgentAt(self.x,self.y) != 0 :
            self.x = randint(0,getWorldWidth()-1)
            self.y = randint(0,getWorldHeight()-1)
        setAgentAt(self.x,self.y,self.type)
        return

    def getPosition(self):
        return (self.x,self.y)

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

    def attack_predator(self, predators):
        """Si gentil, tue les predateurs avec une probabilite pour proteger les humains"""
        global nbPredators
        for predator in predators:
            if predator.x == self.x and predator.y == self.y:
                predators.remove(predator)  # tue le predateur
                nbPredators-=1
                break  # tue un predateur a la fois
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
        self.alive = True

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

    def reproduce(self, humans):
        """Les humains se reproduisent avec une probabilité"""
        global nbHumans
        if random() < proba_rep_hum and nbTrees > 15 :
                humans.append(Human(self.type))
                nbHumans+=1
        return

    def burning(self):
        """Les humains sont brules par les arbres"""
        global nbHumans
        self.type = flameId
        return

    def burnt(self,humans) :
        global nbHumans
        humans.remove(self)
        nbHumans-=1
        del burning_agents[(self.x, self.y)] #PAS SUR DE METTRE çA LA
            #mettre une case sans objet la ou l'humain etait
        setAgentAt(self.x, self.y, noAgentId)


class Robot:
    def __init__(self, imageId):
        self.type = imageId
        self.reset()
        self.evil = False  # Starts peaceful
        self.alive = True

    def reset(self):
        """Place le robot devant l'usine"""
        self.x = 5
        self.y = 32
        return

    
    def move(self):
        """Bouge aléatoirement le robot dans le monde dans une des quatre directions,sauf s'il y a un prédateur à côté (alors il va dans cette direction)."""
        xNew, yNew = self.x, self.y
        prey_near = False

        if self.evil == False :
            # Vérifie les cases autour pour aller vers un prédateur
            for neighbours in [(-1,-1), (-1,+1), (+1,0), (0,-1), (-1,0), (+1,-1), (0,+1), (+1,+1)]:
                nx = (self.x + neighbours[0] + worldWidth) % worldWidth
                ny = (self.y + neighbours[1] + worldHeight) % worldHeight
                if getAgentAt(nx, ny) == predatorId:
                    xNew = (self.x + neighbours[0] + worldWidth) % worldWidth
                    yNew = (self.y + neighbours[1] + worldHeight) % worldHeight
                    prey_near = True
                    break
        else :
            # Vérifie les cases autour pour aller vers un prédateur
            for neighbours in [(-1,-1), (-1,+1), (+1,0), (0,-1), (-1,0), (+1,-1), (0,+1), (+1,+1)]:
                nx = (self.x + neighbours[0] + worldWidth) % worldWidth
                ny = (self.y + neighbours[1] + worldHeight) % worldHeight
                if getAgentAt(nx, ny) == womanId or getAgentAt(nx, ny) == manId :
                    xNew = (self.x + neighbours[0] + worldWidth) % worldWidth
                    yNew = (self.y + neighbours[1] + worldHeight) % worldHeight
                    prey_near = True
                    break

        # Si aucun prédateur proche, déplacement aléatoire
        if not prey_near:
            if random() < 0.5:
                xNew = (self.x + [-1, +1][randint(0, 1)] + getWorldWidth()) % getWorldWidth()
            else:
                yNew = (self.y + [-1, +1][randint(0, 1)] + getWorldHeight()) % getWorldHeight()

        # Déplacement si la case est libre
        if getObjectAt(xNew, yNew) == 0:
            setAgentAt(self.x, self.y, noAgentId)
            self.x, self.y = xNew, yNew
            setAgentAt(self.x, self.y, self.type)

        return


    def turn_evil(self):
        """Peux de chance de devenir méchant et d'attaquer les humains"""
        global nbEvilRobots, nbRobots

        if not self.evil and random() < proba_turn_evil and nbRobots > 5 :
            self.evil = True
            self.type = evilRobotId  # Change appearance
            nbEvilRobots+=1
            nbRobots-=1
        return

    def attack_human(self, humans):
        """Si mechant, tue l'humain"""
        global nbHumans

        if self.evil:
            for human in humans:
                if human.x == self.x and human.y == self.y:
                    humans.remove(human)  # tue l'humain
                    nbHumans-=1
                    break  # Tue un humain a la fois
        return

    def attack_predator(self, predators):
        """Si gentil, tue les predateurs avec une probabilite pour proteger les humains"""
        global nbPredators

        if not(self.evil) and random() < proba_attack_pred :
            for predator in predators:
                if predator.x == self.x and predator.y == self.y:
                    predators.remove(predator)  # tue le predateur
                    nbPredators -=1
                    break  # tue un predateur a la fois
        return

    def fabrication(self, robots):
        """Les humains se reproduisent avec une probabilité"""
        global nbRobots
        if random() < proba_fabrication_robots and self.evil == False :     #Les robots sont sains quand ils sortent de l'usine
            #print("un nouveau ROBOT !! ")
            robots.append(Robot(self.type))
            nbRobots+=1
        return

    def burnt(self,robots) :
        global nbRobots, nbEvilRobots
        robots.remove(self)
        del burning_agents[(self.x, self.y)]
            #mettre une case sans objet la ou l'humain etait
        setAgentAt(self.x, self.y, noAgentId)
        if self.evil :
            nbEvilRobots -=1
        else :
            nbRobots -=1


class Predator:
    def __init__(self, imageId):
        self.type = imageId
        self.reset()
        self.alive = True

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
        """Bouge aléatoirement le predateur dans le monde dans une des quatre directions,
        sauf s'il y a un humain à côté (alors il va dans cette direction)."""
        xNew, yNew = self.x, self.y
        pred_near = False

        # Vérifie les cases autour pour fuir un prédateur
        for neighbours in [(-1,-1), (-1,+1), (+1,0), (0,-1), (-1,0), (+1,-1), (0,+1), (+1,+1)]:
            nx = (self.x + neighbours[0] + worldWidth) % worldWidth
            ny = (self.y + neighbours[1] + worldHeight) % worldHeight
            if getAgentAt(nx, ny) == womanId or getAgentAt(nx,ny) == manId:
                xNew = (self.x + neighbours[0] + worldWidth) % worldWidth
                yNew = (self.y + neighbours[1] + worldHeight) % worldHeight
                pred_near = True
                break

        # Si aucun prédateur proche, déplacement aléatoire
        if not pred_near:
            if random() < 0.5:
                xNew = (self.x + [-1, +1][randint(0, 1)] + getWorldWidth()) % getWorldWidth()
            else:
                yNew = (self.y + [-1, +1][randint(0, 1)] + getWorldHeight()) % getWorldHeight()

        # Déplacement si la case est libre
        if getObjectAt(xNew, yNew) == 0:
            setAgentAt(self.x, self.y, noAgentId)
            self.x, self.y = xNew, yNew
            setAgentAt(self.x, self.y, self.type)

        return



    def hunt(self, humans):
        """Tue un humain si sur la même case."""
        global nbHumans

        for human in humans :
            if human.x == self.x and human.y == self.y:
                humans.remove(human)  #Tue l'humain
                nbHumans-=1
                break  #Tue un seul a la fois
        return

    def reproduce(self, predators):
        """Les humains se reproduisent avec une probabilité"""
        global nbPredators
        if random() < proba_rep_pred:
                predators.append(Predator(self.type))
                nbPredators+=1
        return

    def burnt(self,predators) :
        global nbPredators
        predators.remove(self)
        del burning_agents[(self.x, self.y)]
            #mettre une case sans objet la ou l'humain etait
        setAgentAt(self.x, self.y, noAgentId)
        nbPredators-=1



### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### Initialise world
###
###


def initWorld():
    global nbTrees, nbBurntTrees, predators, humans, robots

    # add a pyramid-shape building
    building1TerrainMap = [
    [ 2, 2, 2, 2 ],
    [ 2, 2, 2, 2 ],
    [ 2, 2, 2, 2 ],
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
    nbTrees+=1


    mountainTerrainMap = [
        [2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2]
    ]
    mountainHeightMap = [
        [1, 1, 1, 1, 1],
        [1, 2, 2, 2, 1],
        [1, 2, 3, 2, 1],
        [1, 2, 2, 2, 1],
        [1, 1, 1, 1, 1]
    ]


    x_offset = 35
    y_offset = 31
    for x in range(len(mountainTerrainMap[0])):
        for y in range(len(mountainTerrainMap)):
            setTerrainAt(x+x_offset, y+y_offset, mountainTerrainMap[x][y])
            setHeightAt(x+x_offset, y+y_offset, mountainHeightMap[x][y])
            setObjectAt(x+x_offset, y+y_offset, -1)

    setObjectAt(x_offset+2, y_offset+2, treeId)
    nbTrees += 1


    #Ajout immeuble
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
        setObjectAt(x, y, buildingId, 9)
        for dx in range(1,building_width):
            for dy in range(1,building_height):
                setObjectAt(x + dx, y + dy, 0, 9)


    #ajout usine
    x = 5
    y = 35
    setObjectAt(x,y,factoryId, 10)

    #ajout predateurs dans le monde
    for i in range(nbPredators):
        predators.append(Predator(predatorId))

    #ajout humains dans le monde
    for i in range(nbHumans):
        if (random() <= 0.5) :
            humans.append(Human(womanId))
        else :
            humans.append(Human(manId))

    #ajout robots dans le monde

    for i in range(nbRobots) :
        robots.append(Robot(robotId))

    #ajout arbres
    for i in range(nbTrees):
        x = randint(0,getWorldWidth()-1)
        y = randint(0,getWorldHeight()-1)
        while getTerrainAt(x,y) != 0 or getObjectAt(x,y) != 0 or (x==5 and y==35):
            x = randint(0,getWorldWidth()-1)
            y = randint(0,getWorldHeight()-1)
        setObjectAt(x,y,treeId)


    #ajout arbres brules
    for i in range(nbBurntTrees):
        x = randint(0,getWorldWidth()-1)
        y = randint(0,getWorldHeight()-1)
        while getTerrainAt(x,y) != 0 or getObjectAt(x,y) != 0:
            x = randint(0,getWorldWidth()-1)
            y = randint(0,getWorldHeight()-1)
        setObjectAt(x,y,burningTreeId)
        burning_trees[(x,y)] = 0

    #ajout lac
    for x in range(13,20):
        for y in range(3,10):
            setTerrainAt(x,y,waterId)
            setObjectAt(x,y,-1)
    setTerrainAt(13,3,grassId)
    setTerrainAt(13,9,grassId)
    setTerrainAt(19,3,grassId)
    setTerrainAt(19,9,grassId)
    return

### ### ### ### ###

def initAgents():
    return


### ### ### ### ###
def stepWorld(it=0):
    global nbTrees, nbBurntTrees, nbHumans, nbEvilRobots, nbRobots, nbPredators, season_timer
    global addNoise, is_earthquake_active, earthquake_end_time, current_season, current_season_index
    global next_earthquake_time, flood_active, flood_duration, next_flood_spread, flood_end_time, last_building_count, building_placed

    if nbHumans//5 > last_building_count and nbHumans > 0:
        last_building_count = nbHumans//5
        building_placed = False
        for _ in range(100) :  # essayer differents endroits
            x,y = randint(0,worldWidth-1), randint(0,worldHeight-1)
            if getObjectAt(x,y) == 0:
                setObjectAt(x,y,buildingId,9)

                #Brûler les arbres autour (5x5)
                trees_burned = 0
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < worldWidth and 0 <= ny < worldHeight:
                            if getObjectAt(nx, ny) == treeId:
                                setObjectAt(nx, ny, burningTreeId)
                                burning_trees[(nx, ny)] = it
                                nbBurntTrees += 1
                                nbTrees -= 1
                                trees_burned += 1

                print(f"{trees_burned} arbres brûlés autour du bâtiment")
                building_placed = True
                break

    # tremblement de terre
    if not is_earthquake_active and it >= next_earthquake_time:
        if random() < proba_earthq or (nbEvilRobots+nbRobots) > 15 :
            # commencer le tremblement de terre
            addNoise = True
            is_earthquake_active = True
            earthquake_end_time = it + earthq_time
            next_earthquake_time = it + earthquake_cooldown  # Set next possible time
            #print(f"EARTHQUAKE STARTED! (Iteration: {it})")
            # tue les humains
            for human in humans:  
                if random() < 0.5:  # 50% de proba pour mourrir
                    setAgentAt(human.x, human.y, noAgentId)
                    humans.remove(human)
                    nbHumans -= 1
                    #print("A human died in the earthquake!")

            # tue les prédateurs  
            for predator in predators:
                if random() < 0.2:  # 20% de proba pour mourrir
                    setAgentAt(predator.x, predator.y, noAgentId)
                    predators.remove(predator)
                    nbPredators -= 1
                    #print("A predator died in the earthquake!")
            # tremblement de terre détruit les batiments et l'usine avec une proba
            for y in range(worldHeight):
                for x in range(worldWidth):
                    if getObjectAt(x, y, 9) == buildingId or getObjectAt(x, y, 10) == factoryId:
                        if random() < 0.7:  
                            setObjectAt(x, y, 0, 9)  # supprime le batiment
                            setObjectAt(x, y, 0, 10)  # supprime l'usine
                        
    elif is_earthquake_active and it >= earthquake_end_time:
        # la fin du tremblement de terre
        addNoise = False
        is_earthquake_active = False
        #print("EARTHQUAKE ENDED")

        if random() < proba_flood_after_earthquake:
            flood_active = True
            next_flood_spread = it + flood_spread_interval
            flood_end_time = it + flood_duration
            #print("FLOOD STARTED!")

            # initialisation de l'inondation
            for x in range(13,20):
                for y in range(3,10):
                    setTerrainAt(x,y,waterId)
                    setObjectAt(x,y,-1)
                    setHeightAt(x,y,1)

    if flood_active:
        if it >= next_flood_spread:
            next_flood_spread = it + flood_spread_interval
            water_tiles = []
            
            for x in range(worldWidth):
                for y in range(worldHeight):
                    if getTerrainAt(x, y) == waterId:
                        water_tiles.append((x, y))
            
            new_water_tiles = []
            
            for x, y in water_tiles:
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < worldWidth and 0 <= ny < worldHeight:
                        if (getTerrainAt(nx, ny) != waterId and getHeightAt(nx, ny) <= 1 and (nx, ny) not in new_water_tiles):
                            setTerrainAt(nx, ny, waterId)
                            setHeightAt(nx,ny,1)
                            setObjectAt(nx, ny, -1)
                            new_water_tiles.append((nx, ny))
                            
                            # detruit les arbres et tue les agents
                            if getObjectAt(nx, ny) == treeId:
                                setObjectAt(nx, ny, noObjectId)
                                nbTrees -= 1
         
            #print(f"Flood spread to {len(new_water_tiles)} new tiles")

        #attendre la fin de l'inondation avant de tuer les agents pour ne pas qu'elle s'arrête    
        if it >= flood_end_time:
            flood_active = False
            for x, y in water_tiles:
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < worldWidth and 0 <= ny < worldHeight:
                        agent = getAgentAt(nx, ny)
                        if agent in [womanId, manId, predatorId, evilRobotId, playerId, robotId] :
                            setAgentAt(nx, ny, noAgentId)
                            if agent == womanId or agent == manId :
                                nbHumans-=1
                            elif agent == predatorId :
                                nbPredators-=1
                            elif agent == robotId :
                                nbRobots-=1
                            elif agent ==  evilRobotId :
                                nbEvilRobots-=1

            #print("FLOOD ENDED")

#ARBRES

   #bruler les arbres a cote de l'usine
    if it % 10 == 0:
        factory_min_x, factory_max_x = 5, 8
        factory_min_y, factory_max_y = 28, 35

        for x in range(factory_min_x - 4, factory_max_x + 5):
            for y in range(factory_min_y - 4, factory_max_y + 5):
                if (factory_min_x <= x <= factory_max_x and
                    factory_min_y <= y <= factory_max_y):
                    continue

                if 0 <= x < worldWidth and 0 <= y < worldHeight:
                    if getObjectAt(x, y) == treeId and random() < 0.01 : #proba de bruler
                        setObjectAt(x, y, burningTreeId)
                        burning_trees[(x, y)] = 0
                        nbTrees -= 1
                        nbBurntTrees += 1



    if it % (maxFps / 10) == 0:
        new_trees = []  # Liste des nouveaux arbres à planter


        for x in range(worldWidth):
            for y in range(worldHeight):


                if getObjectAt(x, y) == treeId :
                    for neighbours in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
                        nx = (x + neighbours[0] + worldWidth) % worldWidth
                        ny = (y + neighbours[1] + worldHeight) % worldHeight
                        if getObjectAt(nx, ny) == burningTreeId :
                            setObjectAt(x, y, burningTreeId)
                            burning_trees[(x, y)] = it  # Enregistre le moment où il brûle
                            nbBurntTrees += 1
                            nbTrees-=1

                        elif getAgentAt(nx, ny) == evilRobotId and random()< proba_evil_brule:
                            setObjectAt(x, y, burningTreeId)
                            burning_trees[(x, y)] = it
                            nbBurntTrees +=1
                            nbTrees-=1

                    if random() < proba_brule : #arbre brule aléatoirement
                        setObjectAt(x,y,burningTreeId)
                        burning_trees[(x, y)] = it
                        nbBurntTrees+=1
                        nbTrees-=1

                    # Reproduction des arbres
                    if random() < proba_rep_tree and nbHumans < 15 :
                        for neighbours in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
                            nx = (x + neighbours[0] + worldWidth) % worldWidth
                            ny = (y + neighbours[1] + worldHeight) % worldHeight
                            if getObjectAt(nx, ny) == 0 and getTerrainAt(nx, ny) == 0:  # Vérifie que la case est vide
                                new_trees.append((nx, ny))  # Ajouter un nouvel arbre
                                nbTrees+=1
                                break  # Un seul nouvel arbre par cycle


                # Transformation des arbres en feu en cendres
                elif getObjectAt(x, y) == burningTreeId:
                    if (x, y) in burning_trees and it - burning_trees[(x, y)] >= burning_time:
                        setObjectAt(x, y, burntTreeId)
                        #del burning_trees[(x, y)]

                elif getObjectAt(x,y) ==  burntTreeId:
                    if (x, y) in burning_trees and it - burning_trees[(x, y)] >= burnt_time:
                        setObjectAt(x, y, 0)
                        del burning_trees[(x, y)]

                # Les humains brulent
                elif getAgentAt(x,y) in [playerId, womanId, manId, predatorId, robotId, evilRobotId] and random() < proba_agent_brule :

                    for neighbours in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
                        nx = (x + neighbours[0] + worldWidth) % worldWidth
                        ny = (y + neighbours[1] + worldHeight) % worldHeight
                        if getObjectAt(nx, ny) == burningTreeId :
                            setAgentAt(x, y, flameId)

                            burning_agents[(x, y)] = it  # Enregistre le moment où il brûle



        # Ajouter les nouveaux arbres
        for x, y in new_trees:
            setObjectAt(x, y, treeId)

    # Changement des saisons
    season_timer += 1
    if season_timer >= season_duration:
        season_timer = 0
        current_season_index = (current_season_index + 1) % len(SEASONS)
        current_season = SEASONS[current_season_index]
        loadAllImages()
        #print(f"Season changed to: {current_season}")

    return False

### ### ### ### ###

def stepAgents( it = 0 ):
    global nbHumans
    # move agent

    if it % human_speed == 0:
        shuffle(humans)
        for h in humans:   
            if getAgentAt(h.x,h.y) != flameId and h.alive : 
                h.move()
                h.reproduce(humans)
            else :
                h.alive = False
                #print("le 1er print marche !! ")
                if (h.x, h.y) in burning_agents and (it - burning_agents[(h.x, h.y)] >= burning_time) :
                    h.burnt(humans)

    if it % predator_speed == 0:
        shuffle(predators)
        for p in predators :
            if getAgentAt(p.x, p.y) != flameId and p.alive :
                p.move()
                p.hunt(humans)
                p.reproduce(predators)
            else :
                p.alive = False
                if (p.x, p.y) in burning_agents and (it - burning_agents[(p.x, p.y)] >= burning_time) :
                    p.burnt(predators)

    if it % robot_speed == 0:
        shuffle(robots)
        for r in robots :
            if (getAgentAt(r.x,r.y)) != flameId and r.alive :
                r.move()
                r.turn_evil()
                r.attack_predator(predators)
                r.attack_human(humans)
                r.fabrication(robots)
            else :
                r.alive = False
                if (r.x, r.y) in burning_agents and (it - burning_agents[(r.x, r.y)] >= burning_time) :
                    r.burnt(robots)

#TEST POUR L'INSTANT
        if (player.x, player.y,) in burning_agents and (it - burning_agents[(player.x, player.y)] >= burning_time) :
            player.type = flameId
        else : 
            player.type = playerId

        player.attack_predator(predators)

    return


def afficher_graphe() :
        """fonction pour créer et afficher le graphes d'évolution des populations"""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))  # 2 lignes, 1 colonne

        # GRAPHE 1 : Agents
        ax1.plot(history_humans, label="Humains", color='gold')
        ax1.plot(history_predators, label="Prédateurs", color='dimgray')
        ax1.plot(history_robots, label="Robots (gentils)", color='cornflowerblue')
        ax1.plot(history_evil_robots, label="Robots (méchants)", color='darkred')
        ax1.set_title("Évolution des agents")
        ax1.set_xlabel("Temps (itérations)\n")
        ax1.set_ylabel("Population")
        ax1.legend()
        ax1.grid(True)

        # GRAPHE 2 : Arbres
        ax2.plot(history_trees, label="Arbres sains", color='violet')
        ax2.plot(history_burning_trees, label="Arbres brûlés", color='darkorange')
        ax2.set_title("Évolution des arbres")
        ax2.set_xlabel("Temps (itérations)")
        ax2.set_ylabel("Nombre d'arbres")
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()
        plt.savefig("graphes_combines.png")  #Enregistre les deux en un seul fichier
        plt.show()


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### MAIN
###
###

timestamp = datetime.datetime.now().timestamp()

loadAllImages()

displayWelcomeMessage()

initWorld()
initAgents()

player = Player(playerId) #A CHANGER PARCE QUE PLUS DE BASIC AGENT

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

    render(it)

    stepWorld(it)

    perdu = False

    stepAgents(it)


    if (nbHumans == 0) :
        perdu = True

    history_humans.append(nbHumans)
    history_predators.append(nbPredators)
    history_robots.append(nbRobots)
    history_evil_robots.append(nbEvilRobots)
    history_trees.append(nbTrees)
    history_burning_trees.append(nbBurntTrees)


#LES TESTS
    if it % 50 == 0:
        print("nb humains : ", nbHumans)
        print("nb robots sains : ", nbRobots)
        print("nb robots evils : ", nbEvilRobots)
        print("nb predateurs : ", nbPredators)

#________________________________________

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
        #GRAPHE
        afficher_graphe()
        pygame.quit()
        sys.exit()

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
                #affichage du grpahe si touche Echap pressée
                afficher_graphe()
                userExit = True
            elif event.key == pygame.K_s:
                player.move2(0,+1)
            elif event.key == pygame.K_z:
                player.move2(0,-1)
            elif event.key == pygame.K_d:
                player.move2(+1,0)
            elif event.key == pygame.K_q:
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
