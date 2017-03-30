import random
import pygame
import sys
import os
from pygame.locals import *

FPS1 = 15
FPS = 10
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
ACTWINDOWWIDTH = 640
ACTWINDOWHEIGHT = WINDOWHEIGHT
CELLSIZE = 30
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
HIGHSCORE = 0

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0  # syntactic sugar: index of the worm's head

up = pygame.image.load("up.png")
left = pygame.image.load("left.png")
right = pygame.image.load("right.png")
down = pygame.image.load("down.png")

upRect = up.get_rect()
leftRect = left.get_rect()
rightRect = right.get_rect()
downRect = down.get_rect()


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, WINDOWWIDTH, WINDOWHEIGHT, CELLWIDTH, CELLHEIGHT, ACTWINDOWWIDTH, \
        ACTWINDOWHEIGHT, CELLSIZE, up, down, left, right, HIGHSCORE

    pygame.init()

    WINDOWWIDTH = pygame.display.Info().current_w
    WINDOWHEIGHT = pygame.display.Info().current_h
    ACTWINDOWWIDTH = int(2*WINDOWWIDTH/3)
    ACTWINDOWHEIGHT = WINDOWHEIGHT
    CELLWIDTH = int(ACTWINDOWWIDTH / CELLSIZE)
    CELLHEIGHT = int(ACTWINDOWHEIGHT / CELLSIZE) - 1

    ACTWINDOWWIDTH -= (ACTWINDOWWIDTH % CELLSIZE)
    ACTWINDOWHEIGHT -= (ACTWINDOWHEIGHT % CELLSIZE)

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 30)

    up = up.convert_alpha()
    left = left.convert_alpha()
    right = right.convert_alpha()
    down = down.convert_alpha()
    if os.path.exists("score.txt"):
        with open("score.txt","r") as f:
            x = f.read()
            x = int(x)
            if HIGHSCORE < x:
                HIGHSCORE = x
    else:
        HIGHSCORE = 0

    if showStartScreen() == 0:
        return
    while True:
        runGame()
        if showGameOverScreen() == 0:
            break


def runGame():
    # Set a random start point.
    global FPS
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()

    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or event.type == KEYDOWN:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                x, y = event.pos  # get the position of the touch and check which direction has been chosen
                if (getDirection(x, y) == LEFT) and direction != RIGHT:
                    direction = LEFT
                elif (getDirection(x, y) == RIGHT) and direction != LEFT:
                    direction = RIGHT
                elif (getDirection(x, y) == UP) and direction != DOWN:
                    direction = UP
                elif (getDirection(x, y) == DOWN) and direction != UP:
                    direction = DOWN

        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == 0 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == 0 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            return  # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return  # game over

        # check if worm has eaten an apply
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation()  # set a new apple somewhere
            if (len(wormCoords) - 2) != 0 and (len(wormCoords) - 2) % 10 == 0 and FPS < 50:
                FPS += 5
        else:
            del wormCoords[-1] # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords, direction)
        drawApple(apple)
        drawScore(len(wormCoords) - 3)
        drawArrows()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawPressKeyMsg():

    pressKeySurf = BASICFONT.render('Touch the screen to play.', True, WHITE)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.centerx = int(WINDOWWIDTH / 2)
    pressKeyRect.centery = int(9 * WINDOWHEIGHT / 10)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def drawArrows():

    a = ACTWINDOWWIDTH + int((WINDOWWIDTH - ACTWINDOWWIDTH) / 2)
    b = int(2 * WINDOWHEIGHT / 3)
    x, y = left.get_size()

    leftRect.midright = (a - int((a - ACTWINDOWWIDTH)/4), b)
    rightRect.midleft = (a + int((a - ACTWINDOWWIDTH)/4), b)
    upRect.midbottom = (a, b - int(y / 2))
    downRect.midtop = (a, b + int(y / 2))

    DISPLAYSURF.blit(up, upRect)
    DISPLAYSURF.blit(left, leftRect)
    DISPLAYSURF.blit(right, rightRect)
    DISPLAYSURF.blit(down, downRect)


def getDirection(x, y):
    if upRect.collidepoint(x, y):
        return UP
    if leftRect.collidepoint(x, y):
        return LEFT
    if rightRect.collidepoint(x, y):
        return RIGHT
    if downRect.collidepoint(x, y):
        return DOWN


def checkForKeyPress():

    ev = pygame.event.get()
    if len(ev) == 0:
        return 2

    for e in ev:

        if e.type == QUIT or e.type == KEYDOWN:
            terminate()
        if e.type == MOUSEBUTTONDOWN:
            return 1


def showStartScreen():

    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        c = checkForKeyPress()
        if c == 1:
            pygame.event.get()  # clear event queue
            return 1
        elif c == 0:
            return 0
        pygame.display.update()
        FPSCLOCK.tick(FPS1)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(1, CELLWIDTH - 1), 'y': random.randint(1, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue
    with open("score.txt", "w") as f:
        f.write("{}".format(HIGHSCORE))

    while True:
        c = checkForKeyPress()
        if c == 1:
            pygame.event.get()  # clear event queue
            return 1
        elif c == 0:
            return 0


def drawScore(score):
    global HIGHSCORE, FPS
    scoreSurf = BASICFONT.render('Score: %s' % score, True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.centerx = ACTWINDOWWIDTH + int((WINDOWWIDTH - ACTWINDOWWIDTH)/2)
    scoreRect.centery = WINDOWHEIGHT / 10
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    if HIGHSCORE < score:
        HIGHSCORE = score
    scoreSurf = BASICFONT.render('HighScore: %s' % HIGHSCORE, True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.centerx = ACTWINDOWWIDTH + int((WINDOWWIDTH - ACTWINDOWWIDTH) / 2)
    scoreRect.centery = 2 * WINDOWHEIGHT / 10
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords, direction):
    x = wormCoords[0]['x'] * CELLSIZE
    y = wormCoords[0]['y'] * CELLSIZE
    if direction == UP:
        pygame.draw.polygon(DISPLAYSURF, DARKGREEN, ((x + int(CELLSIZE / 2), y), (x, y + int(CELLSIZE / 2)),
                                                     (x, y + CELLSIZE - 1), (x + CELLSIZE - 1, y + CELLSIZE - 1),
                                                     (x + CELLSIZE - 1, y + int(CELLSIZE / 2))))
        pygame.draw.polygon(DISPLAYSURF, GREEN, ((x + int(CELLSIZE / 2), y + 4), (x + 4, y + int(CELLSIZE / 2)),
                                                 (x + 4, y + CELLSIZE - 5), (x + CELLSIZE - 5, y + CELLSIZE - 5),
                                                 (x + CELLSIZE - 5, y + int(CELLSIZE / 2))))
    elif direction == DOWN:
        pygame.draw.polygon(DISPLAYSURF, DARKGREEN, ((x, y), (x + CELLSIZE - 1, y),
                                                     (x + CELLSIZE - 1, y + int(CELLSIZE / 2)),
                                                     (x + int(CELLSIZE / 2), y + CELLSIZE - 1),
                                                     (x, y + int(CELLSIZE / 2))))
        pygame.draw.polygon(DISPLAYSURF, GREEN, ((x + 4, y + 4), (x + CELLSIZE - 5, y + 4),
                                                 (x + CELLSIZE - 5, y + int(CELLSIZE / 2)),
                                                 (x + int(CELLSIZE / 2), y + CELLSIZE - 5),
                                                 (x + 4, y + int(CELLSIZE / 2))))
    elif direction == LEFT:
        pygame.draw.polygon(DISPLAYSURF, DARKGREEN, ((x, y + int(CELLSIZE / 2)),
                                                     (x + int(CELLSIZE / 2), y + CELLSIZE - 1),
                                                     (x + CELLSIZE - 1, y + CELLSIZE - 1), (x + CELLSIZE - 1, y),
                                                     (x + int(CELLSIZE / 2), y)))
        pygame.draw.polygon(DISPLAYSURF, GREEN, ((x + 4, y + int(CELLSIZE / 2)),
                                                 (x + int(CELLSIZE / 2), y + CELLSIZE - 5),
                                                 (x + CELLSIZE - 5, y + CELLSIZE - 5), (x + CELLSIZE - 5, y + 4),
                                                 (x + int(CELLSIZE / 2), y + 4)))
    elif direction == RIGHT:
        pygame.draw.polygon(DISPLAYSURF, DARKGREEN, ((x, y), (x + int(CELLSIZE / 2), y),
                                                     (x + CELLSIZE - 1, y + int(CELLSIZE / 2)),
                                                     (x + int(CELLSIZE / 2), y + CELLSIZE - 1), (x, y + CELLSIZE - 1)))
        pygame.draw.polygon(DISPLAYSURF, GREEN, ((x + 4, y + 4), (x + int(CELLSIZE / 2), y + 4),
                                                 (x + CELLSIZE - 5, y + int(CELLSIZE / 2)),
                                                 (x + int(CELLSIZE / 2), y + CELLSIZE - 5), (x + 4, y + CELLSIZE - 5)))
    for coord in wormCoords[1:]:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    pygame.draw.line(DISPLAYSURF, WHITE, (CELLSIZE, CELLSIZE), (CELLSIZE, ACTWINDOWHEIGHT - CELLSIZE))
    pygame.draw.line(DISPLAYSURF, WHITE, (ACTWINDOWWIDTH, CELLSIZE), (ACTWINDOWWIDTH, ACTWINDOWHEIGHT - CELLSIZE))
    pygame.draw.line(DISPLAYSURF, WHITE, (CELLSIZE, CELLSIZE), (ACTWINDOWWIDTH, CELLSIZE))
    pygame.draw.line(DISPLAYSURF, WHITE, (CELLSIZE, ACTWINDOWHEIGHT - CELLSIZE),
                     (ACTWINDOWWIDTH, ACTWINDOWHEIGHT - CELLSIZE))


if __name__ == '__main__':
    main()