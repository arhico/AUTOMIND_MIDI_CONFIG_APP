
import pygame.gfxdraw
import pygame
import math
from automindMidiConfig import *
from automindMidiConfig import MINIMUM_GRIDBOX

def globalFontUpdate(fontFile, size, fontResolution=None):
    return pygame.freetype.Font(fontFile, size)

# filenames = next(walk(FONTS_PATH), (None, None, []))[2]  # [] if no file

globalFont = globalFontUpdate(TEXT_FAMILY, TEXT_SIZE)

clock = pygame.time.Clock()
class rootObjectsContainerClass(object):
    def __init__(self, screen, clock, objects) -> None:
        self.screen = screen
        self.objects = []
        self.clock = clock
        for object in range(len(objects)):
            self.objects.append(objects[object])
    def update(self, framerate):
        for object in self.objects:
            for internalObj in object:
                try:
                    internalObj.update()
                except:
                    pass
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pygame.display.flip()
        self.clock.tick(framerate)

class gridClass(object):
    def __init__(self, gridSize = (GRID_SIZE_PX_X, GRID_SIZE_PX_Y), screenSize = (SCREEN_W, SCREEN_H)):
        super(gridClass, self).__init__()
        self.grid = {}
        self.gridSize = gridSize
        self.quantizedScreensize = (0,0)
        self.quantizedScreensize, self.gridDimensions = self.generateGrid(screenSize)
        self.screen = None
        self.borderPx = GRID_CELL_BORDER_PX
        print(f"Generated Grid Elements: {(self.grid.__len__())}, Grid Size: {self.gridDimensions}")
    def update(self):
        if RENDER_GRID:
            self.renderGrid()
        if RENDER_FREE_CELLS:
            for point in self.grid:
                self.grid[point].renderPoint()
    def generateGrid(self, screenSize):
        quantizedScreenSizeFromGrid = 0
        gridSize = self.gridSize
        gridDimensions = [0,0]
        for xIdxSweep in range(0, math.floor(screenSize[0]/self.gridSize[0])):
            gridDimensions[0] = xIdxSweep
            for yIdxSweep in range(0, math.floor(screenSize[1]/self.gridSize[1])):
                gridDimensions[1] = yIdxSweep
                self.grid[(xIdxSweep,yIdxSweep)] = (gridPointClass(self.gridSize, (xIdxSweep, yIdxSweep), (xIdxSweep * gridSize[0], yIdxSweep * gridSize[1])))
        quantizedScreenSizeFromGrid = (math.ceil((xIdxSweep + 1) * gridSize[0]), math.ceil((yIdxSweep + 1) * gridSize[1]))
        gridDimensions = [dimension+1 for dimension in gridDimensions]
        return quantizedScreenSizeFromGrid, tuple(gridDimensions)
    def renderGrid(self):
        selection = [0,0]
        for vertLine in range(0,self.gridDimensions[0] + 1):
            x = vertLine * self.gridSize[0] 
            y1 = 0
            y2 = self.quantizedScreensize[1]
            pygame.gfxdraw.vline(self.screen, x,  y1, y2,  GRID_COLOR)
            selection[0] += 1 # x sweep
        selection[0] = selection[1] = 0
        for horLine in range(0,self.gridDimensions[1] + 1):
            pygame.gfxdraw.hline(self.screen,  0, self.quantizedScreensize[0], horLine * self.gridSize[1],  GRID_COLOR)
            selection[1] += 1 # x sweep
    def setPygameSurface(self, screen):
        self.screen = screen
        for point in self.grid:
            self.grid[point].screen = screen

def findFirstFreePlace(grid, gridBoxInput, sourceGroupMapping = None):
    gridBox = (0,0)
    if not sourceGroupMapping is None:
        gridBox = (gridBoxInput[0] * sourceGroupMapping[0], gridBoxInput[1] * sourceGroupMapping[1])
    else:
        gridBox = gridBoxInput
    print(f'Initiated finding {gridBoxInput} with mapping: {sourceGroupMapping}')
    for topLeftStartingGridPoint in grid.grid:
        gridPointsToOccupy = [] 
        sourceKey = (topLeftStartingGridPoint[0], topLeftStartingGridPoint[1])
        newKey = [sourceKey[0], sourceKey[1]]
        breakToNext = False
        for idxX in range(0,gridBox[0]): # X SWEEP
            newKey[0] = sourceKey[0] + idxX
            if not tuple(newKey) in grid.grid:
                breakToNext = True
            for idxY in range(0,gridBox[1]):
                if breakToNext:
                    newKey = [sourceKey[0], sourceKey[1]]
                    break
                newKey[1] = sourceKey[1] + idxY
                if not tuple(newKey) in grid.grid:
                    breakToNext = True
                    break
                if not idxY % gridBoxInput[1] and not idxX % gridBoxInput[0]:
                    gridPointsToOccupy.append((sourceKey[0]+idxX,sourceKey[1]+idxY))
        if breakToNext:
            continue
        print(f"Grid found free space @ {sourceKey}, coords: {grid.grid[topLeftStartingGridPoint].screenCoords} px")
        return gridPointsToOccupy

class gridPointClass(object):
    def __init__(self, gridSize, indexes, coords):
        super(gridPointClass, self).__init__()
        self.screen = None
        self.gridSize = gridSize
        coordsRounder = (int(coords[0]),int(coords[1]))
        self.screenCoords = coordsRounder
        self.index = indexes
        self.occupied = False
        self.lowpass = lowpassAssymetrical()
    def renderPoint(self):
        if RENDER_FREE_CELLS_PIXELS_AT_CENTER:
            offset = [self.gridSize[0], self.gridSize[1]]
        else:
            offset = [0,0]
        if not self.screen is None:
            # # if self.occupied:
            # if 1:
            #     mult = 50
            # else:
            #     mult = 10
            pygame.gfxdraw.pixel(self.screen, int(self.screenCoords[0]+offset[0]/2), int(self.screenCoords[1] + offset[1]/2),self.lowpass.update((colorRandom()),0.95))
    # def lowpass():
        # lp = 

grids = gridClass()
screenFlags = pygame.SRCALPHA
screen = pygame.display.set_mode(grids.quantizedScreensize, flags=screenFlags, depth=32)
grids.setPygameSurface(screen)

pygame.display.set_caption(APP_NAME)
def getSequentialSensorId():
    global privateAutomindTouchSensorCounter
    privateAutomindTouchSensorCounter += 1
    return privateAutomindTouchSensorCounter - 1

def getSequentialFaderId():
    global privateFadersCounter
    privateFadersCounter += 1
    return privateFadersCounter - 1

def calcDistance(coord1, coord2):
    diff1 = coord2[0] - coord1[0]
    diff2 = coord2[1] - coord1[1]
    return math.sqrt(pow(diff1, 2) + pow(diff2, 2))

class rootObject(object):
    def __init__(self, screen, globalText, grid, gridTopLeftCoords, gridBox, font, colors, objType = None):
        super().__init__()
        self.type = objType
        try:
            self.gridSize = grid.gridSize
        except:
            self.gridSize = None
        # self.ignoreOccupiedGridpoints = False
        self.incapsulatedObjects = []
        self.interactive = False
        self.id = None
        self.colors = colors
        self.needUpdate = True
        self.gridTopLeftCoords = gridTopLeftCoords
        self.occupiedGridPoints = []
        self.activityObj = {}
        match objType:
            case "guiLed":
                self.doesOccupyGridPoints = False
            case "guiScrollbar":
                self.doesOccupyGridPoints = False
            case _:
                self.doesOccupyGridPoints = True
        self.screenCoords = []
        self.screenCenterOffsettedCoords = []
        self.grid = grid
        self.screen = screen
        self.active = False
        self.activePrevious = False
        self.value = 0
        self.rangeBounds = DEFAULT_RANGE_BOUNDS
        self.hover = None
        self.changed = False
        self.text = [self.type]
        self.activeToggle = False
        self.font = font
        self.globalText = globalText
        self.hoverPrevious = None
        self.selected = [None,[]]
        self.selectedPrev = 0
        self.gridBox = gridBox
        self.screenSize = [(self.gridBox[0]) * self.gridSize[0], (self.gridBox[1]) * self.gridSize[1]]
        self.colors = colors
        self.highlightColorMults = HOVER_COLOR_MULTS
        self.demo = False
        self.activationJustStartedHelperBool = False
        self.lowpass = lowpassAssymetrical()
        self.borderPx = self.grid.borderPx
        self.hashPrevious = ""
        self.maxDropListLen = 0
        self.maxHoverCont = 0
        self.scrollable = False
        if not self.gridTopLeftCoords is None and self.doesOccupyGridPoints:
            self.updateInternalData()
    def changesDetector(self):
        if self.type == "guiLed" or self.type == "guiScrollbar":
            return
        selectionChanged = listChanged = False
        
        curName = ""
        try:
            curName = str(list(self.text.keys()))
        except:
            pass
            # try:
            #     curName = self.text[0]
            # except:
            #     curName = self.type
        
        if str(self.text) != str(self.hashPrevious) and self.type != "guiBrickInfo":
            self.changed = True
            listChanged = True
            self.hashPrevious = str(self.text)
        
        if self.selected != self.selectedPrev:
            selectionChanged = True
            self.changed = True
            self.selectedPrev = self.selected.copy()
        if listChanged:
            if curName in guiBricksNames:
                self.globalText[NOTIF_TITLE]=[f"{round((time.time()-START_TIME)*1000)}: Initialized"]
            else:
                self.globalText[NOTIF_TITLE]=[f"{round((time.time()-START_TIME)*1000)}: {curName} list changed"]
            try:
                checkValueStillHere = list(self.text).index(self.selected[1][self.selected[0]])
                if checkValueStillHere != -1:
                    self.selected[0] = checkValueStillHere
                    self.selectedPrev = self.selected.copy()
                    print(f"Previous selection detected in changed list! {self.selected[0]}")
            except:
                print(f"Failed to reselect previous item! {self.selected[0]}")
                self.selected[0] = None
        if selectionChanged:
            if curName in guiBricksNames:
                self.globalText[NOTIF_TITLE]=[f"{round((time.time()-START_TIME)*1000)}: Initialized"]
            else:
                self.globalText[NOTIF_TITLE]=[f"{round((time.time()-START_TIME)*1000)}: {curName} selection changed"]
    def updateInternalData(self):
        self.screenCoords = [self.gridTopLeftCoords[0] * self.grid.gridSize[0], self.gridTopLeftCoords[1] * self.grid.gridSize[1]]
        if self.occupiedGridPoints.__len__() == 0 and self.doesOccupyGridPoints == True:
            point = []
            for x in range(0,self.gridBox[0]):
                for y in range(0,self.gridBox[1]):
                    point = [self.gridTopLeftCoords[0]+x, self.gridTopLeftCoords[1]+y]
                    self.occupiedGridPoints.append(self.grid.grid.pop(tuple(point)))
                    # print(f'{self.type} occupied point {point}')
        self.screenCenterOffsettedCoords = [int(self.screenCoords[0] + self.screenSize[0]/2), int(self.screenCoords[1] + self.screenSize[1]/2)]
        self.changesDetector()
        if self.active:
            self.activeToggle = not self.activeToggle
        # for obj in self.activityObj:
        #     self.activityObj[obj].update()
        # try:
        #     self.activityObj['guiScrollbar'].update()
        # except:
        #     pass
        if self.interactive:
            self.mouseInteractionSolver()
        
    def mouseInteractionSolver(self, receiveDataFrom = None, sendDataTo = None):
        x, y = pygame.mouse.get_pos()
        mousePressed = pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]
        if not mousePressed:
            self.activationJustStartedHelperBool = False
            self.active = False
        if mousePressed and not self.hover is None and not self.active:
            self.active = True
            self.activationJustStartedHelperBool = True
            textCheck = self.text
            if self.hover > self.maxHoverCont - 1:
                return
            if textCheck is None or isinstance(textCheck, str):
                self.selected = [self.hover,[]]
            elif isinstance(textCheck, list):
                    self.selected =[self.hover, textCheck]
            elif isinstance(textCheck, dict):
                selectionList = []
                for key in textCheck:
                    # selectionList.append(key)
                    for item in textCheck[key]:
                        selectionList.append(item)
                self.selected = [self.hover, selectionList]
            # print(f'{self.type},{self.id},{self.gridTopLeftCoords},{self.screenCoords},{self.screenCenterOffsettedCoords}')          
        if not mousePressed and x > self.screenCoords[0] + self.borderPx[0] and x < (self.screenCoords[0] + self.screenSize[0]) and y > self.screenCoords[1] + self.borderPx[1] and y < (self.screenCoords[1] + self.screenSize[1]): 
            self.hover = math.floor((y - self.borderPx[1]*3 - self.screenCoords[1])/self.grid.gridSize[1])
            # if not sendDataTo is None:
            #     sendDataTo[0] = ""
            #     sendDataTo[0] = str(self.screenCoords)
            #     print(sendDataTo)
        else:
            if not self.active:
                self.hover = None
        if not receiveDataFrom is None:
            self.text = receiveDataFrom
    def computeActiveIncrement(self):
        if self.active:
            if self.activationJustStartedHelperBool:
                self.activationJustStartedHelperBool = False
                pygame.mouse.get_rel()
                self.lastActiveCoord = pygame.mouse.get_pos()
            else:
                increment = int(pygame.mouse.get_rel()[1])
                self.valIncrement(increment)
    def valIncrement(self, increment):
        self.value -= (abs(self.value - self.quantizedVal) * 300 + 1) * (increment / 1000 * ( (self.rangeBounds[1] - self.rangeBounds[0])) )/ (20)
        if self.value < self.rangeBounds[0]:
            self.value = self.rangeBounds[0]
        if self.value > self.rangeBounds[1]:
            self.value = self.rangeBounds[1]
        self.quantizedVal = int(self.value + 0.5)

# STATUS BOX, SETTINGS ON RIGHT MOUSE CLICK, CHECKBOX, MENU ITEM, DROPLIST

class guiLed(rootObject):
    def __init__(self, screen, grid, gridTopLeftCoords, gridBox=MINIMUM_GRIDBOX, colors = LED_COLORS, objType="guiLed"):
        super().__init__(screen=screen, globalText=None, grid=grid, gridTopLeftCoords=gridTopLeftCoords, gridBox=gridBox, font=None, colors=colors, objType=objType)
        self.ledTimeoutFrames = LED_TIMEOUT_FRAMES
        self.updateInternalData()
        
        # self.ledIsRound = False
    def update(self, changed):
        self.renderLed(changed)
        if changed:
            return False
    def renderLed(self, changed):
        if changed == True:
            self.ledTimeoutFrames = LED_TIMEOUT_FRAMES
        if self.ledTimeoutFrames > 0:
            self.ledTimeoutFrames-=1
            clrIdx = 1
            coeff = 0.01
        else:
            clrIdx = 0
            coeff = 0.2
        pygame.gfxdraw.box(self.screen, (self.screenCoords[0]+self.grid.borderPx[0]+BRICKS_OUTLINE_RADIUS_PX+BRICKS_OUTLINE_WIDTH_PX, self.screenCoords[1]+self.grid.borderPx[1], LED_SIZE_PX[0], LED_SIZE_PX[1]), self.lowpass.update(self.colors[clrIdx],coeff))

class guiScrollbar(rootObject):
    def __init__(self, screen, grid, gridTopLeftCoords, gridBox=MINIMUM_GRIDBOX, colors = SENSOR_COLOR, objType="guiScrollbar"):
        super().__init__(screen=screen, globalText=None, grid=grid, gridTopLeftCoords=gridTopLeftCoords, gridBox=gridBox, font=None, colors=colors, objType=objType)
        # self.ledTimeoutFrames = LED_TIMEOUT_FRAMES
        self.updateInternalData()
        
        # self.ledIsRound = False
    def update(self, changed = False):
        self.renderScrollbar(changed)
        # if changed:
        #     return False
    def renderScrollbar(self, changed = False):
        # if changed == True:
        #     self.ledTimeoutFrames = LED_TIMEOUT_FRAMES
        # if self.ledTimeoutFrames > 0:
        #     self.ledTimeoutFrames-=1
        #     clrIdx = 1
        #     coeff = 0.01
        # else:
        #     clrIdx = 0
        # #     coeff = 0.2
        # pygame.gfxdraw.box(self.screen,
        #                    (self.screenCoords[0]-self.grid.borderPx[0]-BRICKS_OUTLINE_RADIUS_PX-BRICKS_OUTLINE_WIDTH_PX,
        #                     self.screenCoords[1]+self.grid.borderPx[1],
        #                     self.gridBox[0]*self.gridSize[0],
        #                     self.gridBox[1]*self.gridSize[1]), self.colors[0])
        
        
        pygame.gfxdraw.box(self.screen, (self.screenCoords[0]+self.grid.borderPx[0]+BRICKS_OUTLINE_RADIUS_PX+BRICKS_OUTLINE_WIDTH_PX, self.screenCoords[1]+self.grid.borderPx[1]*2, LED_SIZE_PX[0], LED_SIZE_PX[1]*4), (self.colors[1]))


class guiBrickGlobalText(rootObject):
    def __init__(self, screen, globalText, grid, gridTopLeftCoords = None, gridBox = (20, DEFAULT_STATUS_BOX_GRID_H), objType="statusBox") -> None:
        super().__init__(screen,globalText, grid, gridTopLeftCoords, gridBox, globalFont, DEFAULT_COLORS, objType=objType)
        self.activityObj['guiLed'] = (guiLed(self.screen, grid=self.grid, gridBox=(int(gridBox[0]/12), 1), gridTopLeftCoords=(self.gridTopLeftCoords[0],self.gridTopLeftCoords[1])))
        # self.activityObj.append(guiScrollbar(self.screen, grid=self.grid, gridBox=(int(gridBox[0]/12), 1), gridTopLeftCoords=(self.gridTopLeftCoords[0],self.gridTopLeftCoords[1])))
    def update(self):
        self.updateInternalData()
        self.renderStatusBox(self.globalText)
    def renderStatusBox(self, text, fill=None):
        rectValue = (self.screenCoords[0] + self.grid.borderPx[0], self.screenCoords[1] + self.grid.borderPx[1], self.screenSize[0] - 2*self.grid.borderPx[0], self.screenSize[1] - 2*self.grid.borderPx[1])
        scaledFillRect = [rectValue[0],rectValue[1],rectValue[2],rectValue[3]]
        fillOffset = self.grid.borderPx
        if self.interactive:
            if not self.hover is None: 
                coloring = self.colors[1]
            else:
                coloring = self.colors[0]
        else:
            coloring = self.colors[2]
        curColor = self.lowpass.update(coloring,0.6)
        pygame.draw.rect(self.screen,curColor,rectValue,BRICKS_OUTLINE_WIDTH_PX,border_radius=BRICKS_OUTLINE_RADIUS_PX)
        if not fill is None:
            if isinstance(fill, float):
                if fill > 1.0:
                    fill = 1.0
                if fill < 0:
                    fill = 0
                scaledFillRect[0] += fillOffset[0] * 2
                scaledFillRect[2] -= 2*fillOffset[0] * 2
                scaledFillRect[1] += (self.screenSize[1] - 2 * fillOffset[1])*(1.0-fill)
                scaledFillRect[1] = int(scaledFillRect[1])
                scaledFillRect[3] *= fill
                scaledFillRect[3] = int(scaledFillRect[3])
                pygame.draw.rect(self.screen,curColor,tuple(scaledFillRect), 0, border_radius=int(BRICKS_OUTLINE_RADIUS_PX*0.8))
            else:
                scaledFillRect[0] += fillOffset[0] * 2
                scaledFillRect[1] += fillOffset[0] * 2
                scaledFillRect[2] -= 2*fillOffset[0] * 2
                scaledFillRect[3] -= 2*fillOffset[0] * 2
                pygame.draw.rect(self.screen,curColor,scaledFillRect, 0, border_radius=int(BRICKS_OUTLINE_RADIUS_PX*0.8))
        self.changed = self.activityObj['guiLed'].update(self.changed)
        textHorLimit = int(self.screenSize[0]/PIXELS_PER_SYMBOL - 1)
        maxHoverCont = 0
        keyBg = None
        cnt = 0
        # if self.type != "guiBrickListInteractive":
        if 1:
            if self.gridBox[0] >= 2 and self.gridBox[1] >= 2 and not text is None:
                if isinstance(text, dict):
                    maxHoverCont = text.keys().__len__()
                    for x in text:
                        maxHoverCont += text[x].__len__()
                        self.maxHoverCont = maxHoverCont
                    for key in text:
                        if self.hover == cnt and self.hover < maxHoverCont:
                            keyBg = (255,0,0)
                        if cnt < self.maxDropListLen and cnt < text.__len__():
                            self.font.render_to(self.screen, (rectValue[0] + int(self.grid.gridSize[0]/3),rectValue[1] + int(self.grid.gridSize[1] * cnt) + int(self.grid.gridSize[1]/3)), str(key)[:textHorLimit],fgcolor=colorInvert(BG_COLOR), bgcolor=(keyBg))
                            cnt+=1
                            for item in text[key]:
                                bgColor = None
                                if self.interactive:
                                    if not self.selected[0] == cnt:
                                        if self.hover == cnt and self.hover < maxHoverCont:
                                            bgColor = (self.colors[1])
                                    else:
                                        bgColor = colorInvert(self.colors[1])
                                        
                                self.font.render_to(self.screen, (rectValue[0] + int(self.grid.gridSize[0]),rectValue[1] + int(self.grid.gridSize[1] * cnt) + int(self.grid.gridSize[1]/3)), str(item)[:textHorLimit], fgcolor=colorInvert(BG_COLOR), bgcolor=bgColor)
                                cnt+=1
                                if cnt >= self.maxDropListLen:
                                    return
                    return
                if isinstance(text, list):
                    maxHoverCont = text.__len__()
                    while cnt < self.gridBox[1] and cnt < maxHoverCont:
                        self.font.render_to(self.screen, (rectValue[0] + int(self.grid.gridSize[0]/3),rectValue[1] + int(self.grid.gridSize[1] * cnt) + int(self.grid.gridSize[1]/3)), str(text[cnt]), colorInvert(BG_COLOR))
                        cnt+=1
                    return
                self.font.render_to(self.screen, (rectValue[0] + int(self.grid.gridSize[0]/3),rectValue[1] + int(self.grid.gridSize[1] * cnt) + int(self.grid.gridSize[1]/3)), str(self.text), colorInvert(BG_COLOR))
        # if self.type == "guiBrickListInteractive":
        #     if isinstance(text, dict):
        #         if self.text.keys().__len__():
        #             for key in self.text.keys():
        #                 if not self.hover is None:
        #                     if self.hover == cnt:
        #                         keyBg = DEFAULT_COLORS[1]
        #                 self.font.render_to(self.screen, (rectValue[0] + int(self.grid.gridSize[0]/3),rectValue[1] + int(self.grid.gridSize[1] * cnt) + int(self.grid.gridSize[1]/3)), str(self.text.keys())[:textHorLimit],fgcolor=colorInvert(BG_COLOR), bgcolor=(keyBg))
        #                 cnt+=1
        #             if self.activeToggle:
        #                 # Show list
        #                 self.changed = True
        #                 pass

@staticmethod
def generateFakeList():
    with open("./assets/engWords.txt") as word_file:
        valid_words = list(word_file.read().split())
    key = str(random.choice(valid_words))
    # fakeDic = {}
    # fakeDic[key] =  [random.choice(valid_words)]
    fakeList = []
    iters = random.randint(0,10)
    for x in range(iters):
        # fakeDic[key].append(random.choice(valid_words))
        fakeList.append(random.choice(valid_words))
    # print(fakeDic)
    # return fakeDic
    return fakeList

class guiBrickList(guiBrickGlobalText):
    def __init__(self, screen, globalText, grid, gridTopLeftCoords = None, gridBox=MINIMUM_GRIDBOX, objType="guiBrickList") -> None:
        super().__init__(screen, globalText, grid, gridTopLeftCoords, gridBox, objType)
        self.maxDropListLen = self.gridBox[1] - 1
    def update(self):
        self.updateInternalData()
        self.renderStatusBox(self.text)

class guiBrickInteractive(guiBrickList):
    def __init__(self, screen, globalText, grid, gridTopLeftCoords=None, gridBox=MINIMUM_GRIDBOX, objType="guiBrickInteractive") -> None:
        super().__init__(screen, globalText, grid, gridTopLeftCoords, gridBox, objType)
        self.interactive = True
    def update(self):
        self.mouseInteractionSolver(receiveDataFrom=self.value,sendDataTo=self.globalText)

class guiBrickListInteractive(guiBrickList):
    def __init__(self, screen, globalText, grid, gridTopLeftCoords=None, gridBox=MINIMUM_GRIDBOX, objType="guiBrickListInteractive") -> None:
        super().__init__(screen, globalText, grid, gridTopLeftCoords, gridBox, objType)
        self.interactive = True

# class guiBrickDropListInteractive(guiBrickListInteractive):
#     def __init__(self, screen, globalText, grid, gridTopLeftCoords=None, gridBox=MINIMUM_GRIDBOX, objType="guiBrickDropListInteractive") -> None:
#         super().__init__(screen, globalText, grid, gridTopLeftCoords, gridBox, objType)
#         self.virtualListGridBounds = (self.gridBox[0],self.grid.gridDimensions[1])
#         # self.maxDropListLen = self.gridBox[1] - 1
#         self.maxDropListLen = self.grid.gridDimensions[1] - self.gridTopLeftCoords[1] - 1
#         # self.dropListExpanded = False
#         self.scrollable = False
#         # print(self.maxDropListLen)
 
class guiBrickListInteractiveScrollable(guiBrickListInteractive): # FIXME don't scroll, just inserted scrollbar
    def __init__(self, screen, globalText, grid, gridTopLeftCoords=None, gridBox=MINIMUM_GRIDBOX, objType="guiBrickListInteractiveScrollable") -> None:
        super().__init__(screen, globalText, grid, gridTopLeftCoords, gridBox, objType)
        self.scrollable = True
        self.activityObj['guiScrollbar'] = guiScrollbar(screen, grid=grid, gridBox=(1, gridBox[1]), gridTopLeftCoords=(gridTopLeftCoords[0]+self.gridBox[0]-1,gridTopLeftCoords[1]))
    def update(self):
        super().update()
        self.activityObj['guiScrollbar'].update()

class guiBrickInteractiveFader(guiBrickListInteractive):
    def __init__(self, screen, globalText, grid, gridTopLeftCoords=None, gridBox=MINIMUM_GRIDBOX, objType="guiBrickListInteractive") -> None:
        super().__init__(screen, globalText, grid, gridTopLeftCoords, gridBox, objType)

# class guiBrickInteractiveFader(guiBrickInteractive):
#     def __init__(self, screen, grid, gridTopLeftCoords=None, gridBox=FADER_GRIDBOX, objType="guiBrickInteractiveFader") -> None:
#         super().__init__(screen, grid, gridTopLeftCoords, gridBox, objType)
#         # self.colors = [DEFAULT_SENSOR_COLOR]
    # def update(self):
    #     self.mouseInteractionSolver(receiveDataFrom=None,sendDataTo=self.globalText)
    #     self.updateInternalData()
    #     self.computeActiveIncrement()
    #     self.renderStatusBox(self.value, 0.2)

def gridObjectCreate(objectType, objectsList, screen, globalText, gridPointer, gridBx = (None, None), gridMapping = None):
    if not gridBx[0] is None and not gridBx[1] is None:
        gridBox = [int(gridBx[0]), int(gridBx[1])]
    else:
        gridBox = gridBx
    grmap = gridMapping
    pointsToOccupy = findFirstFreePlace(gridPointer, gridBox, grmap)
    if pointsToOccupy is None:
        print(f"Failed to fit! Skipping {objectType} with gridBox {gridBox},")
        return
    # for point in pointsToOccupy:
    #     print(f'{objectType}:{point}:{gridPointer.grid[tuple(point)].screenCoords}')
    for gridCoordinates in pointsToOccupy:
        match objectType:
            case "guiBrickListInteractiveScrollable":
                objectsList.append(guiBrickListInteractiveScrollable(screen, globalText, gridPointer, gridCoordinates, gridBox=gridBox))
            case "guiBrickListInteractive":
                objectsList.append(guiBrickListInteractive(screen, globalText, gridPointer, gridCoordinates, gridBox=gridBox))
                
            case "guiBrickList":
                objectsList.append(guiBrickList(screen, globalText, gridPointer, gridCoordinates, gridBox=gridBox))
            case "guiBrickInfo":
                objectsList.append(guiBrickList(screen, globalText, gridPointer, gridCoordinates, gridBox=gridBox, objType="guiBrickInfo"))
            # case "guiBrickListInteractive":
            #     objectsList.append(guiBrickListInteractive(screen,globalText, gridPointer, gridCoordinates, gridBox=gridBox))
            case "guiBrickInteractive":
                objectsList.append(guiBrickInteractive(screen,globalText, gridPointer, gridCoordinates, gridBox=gridBox))
            case "guiBrickInteractiveFader":
                objectsList.append(guiBrickInteractiveFader(screen, gridPointer, gridCoordinates, gridBox=gridBx))
            case "statusBox":
                objectsList.append(guiBrickGlobalText(screen,globalText, gridPointer, gridCoordinates, gridBox=gridBox))
            case _:
                pass
    # print(f'free points: {gridPointer.grid.keys()}')
    return objectsList.__len__() - 1