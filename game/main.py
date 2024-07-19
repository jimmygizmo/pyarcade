#! /usr/bin/env -vS python
import math

import pygame
from typing import TypedDict
import os.path
import random
import collections


# ###############################################    CONFIGURATION    ##################################################

SCREEN_WIDTH = 1280.0
SCREEN_HEIGHT = 720.0
TICKRATE = 60  # (frame rate) - 0/None gives maximum/unlimited. Depends on code but recently saw 500-1000 FPS.
GAME_TITLE = 'Space Blasto'
BGCOLOR = 'olivedrab'
BGIMG = 'lawn-bg-dark-2560x1440.jpg'  # 'grass-field-med-1920x1249.jpg'  # 'lawn-bg-dark-2560x1440.jpg'
ASSET_PATH = 'assets'  # Relative path with no trailing slash.
DEBUG = False
# List of tuples of the phase name and the phase duration in phase units (currently 1 second) TODO: Fix. FRAMES!!!!!
ENVIRO_PHASES = collections.deque(  # More efficient at popping from the left side of a list.
    [('peace', 800), ('rogue', 160), ('chaos', 400), ('frozen', 60), ('rogue', 50), ('frozen', 110)]
)  # p, r, c, f
# ANOTHER PERSPECTIVE: ephases are sort of motion-modification macros on a timer schedule that repeats (currently.)
ACID_MODE = False  # Suppress background re-painting. This makes objects leave psychedelic trails for a fun effect.


# Using a TypedDict to satisfy MyPy recommendations for type-hinting/strong-typing.
# TypeDict for MONSTER
Monster = TypedDict('Monster', {
        'name': str,  # Monster short name
        'img': str,  # Filename of PNG (with transparency)
        'w': int,  # PNG pixel width
        'h': int,  # PNG pixel height
        'color': str,  # Debug mode color of rectangle
        'x': float,  # Initial position X value
        'y': float,  # Initial position Y value
        'v': pygame.math.Vector2,  # Velocity
        'd': pygame.math.Vector2,  # Direction
        's': float,  # Initial/default speed
        'p': float,  # Enviro: Peace (speed)
        'r': float,  # Enviro: Rogue (speed)
        'c': float,  # Enviro: Chaos (speed)
        'f': float,  # Enviro: Frozen (speed)
        'surface': pygame.Surface,  # The PyGame-CE Surface object - Displays the image and more
        'rect': pygame.FRect,  # The PyGame-CE FRect object - Positions the Surface and more
        })

# MONSTER DATA - Initial state for a handful of entities that move, experience physics and interact. W/initial motion.
monsters = []

monster1: Monster = {'name': 'red-flower-floaty',
           'img':  'red-flower-66x64.png',
           'w': 66,
           'h': 64,
           'color': 'red1',
           'x': 240.0,
           'y': 300.0,
           'v': pygame.math.Vector2(),  # placeholder instance (mypy)
           'd': pygame.math.Vector2((-0.624, 0.782)),  # placeholder instance (mypy)
           's': 100.0,
           'p': 100.0,
           'r': 100.0,
           'c': 350.0,
           'f': 2.0,
           'surface': pygame.Surface((0, 0)),  # placeholder instance (mypy)
           'rect': pygame.FRect(),  # placeholder instance (mypy)
           }
monsters.append(monster1)
monster2: Monster = {'name': 'red-flower-drifty',
           'img':  'red-flower-66x64.png',
           'w': 66,
           'h': 64,
           'color': 'orangered',
           'x': 240.0,
           'y': 300.0,
           'v': pygame.math.Vector2(),  # placeholder instance (mypy)
           'd': pygame.math.Vector2((0.137, -0.991)),  # placeholder instance (mypy)
           's': 100.0,
           'p': 100.0,
           'r': 100.0,
           'c': 420.0,
           'f': 3.0,
           'surface': pygame.Surface((0, 0)),  # placeholder instance (mypy)
           'rect': pygame.FRect(),  # placeholder instance (mypy)
           }
monsters.append(monster2)
monster3: Monster = {'name': 'goldie',
           'img': 'gold-retriever-160x142.png',
           'w': 160,
           'h': 142,
           'color': 'gold',
           'x': 500.0,
           'y': 300.0,
           'v': pygame.math.Vector2(),  # placeholder instance (mypy)
           'd': pygame.math.Vector2((1.0, 1.0)),  # placeholder instance (mypy)
           's': 141.0,
           'p': 160.0,
           'r': 880.0,
           'c': 1290.0,
           'f': 10.0,
           'surface': pygame.Surface((0, 0)),  # placeholder instance (mypy)
           'rect': pygame.FRect(),  # placeholder instance (mypy)
           }
monsters.append(monster3)
monster4: Monster = {'name': 'fishy',
           'img':  'goldfish-280x220.png',
           'w': 280,
           'h': 220,
           'color': 'darkgoldenrod1',
           'x': 840.0,
           'y': 300.0,
           'v': pygame.math.Vector2(),  # placeholder instance (mypy)
           'd': pygame.math.Vector2((-0.994, -0.114)),  # placeholder instance (mypy)
           's': 80.0,
           'p': 90.0,
           'r': 100.0,
           'c': 700.0,
           'f': 2850.0,
           'surface': pygame.Surface((0, 0)),  # placeholder instance (mypy)
           'rect': pygame.FRect(),  # placeholder instance (mypy)
           }
monsters.append(monster4)
monster5: Monster = {'name': 'grumpy',
           'img':  'grumpy-cat-110x120.png',
           'w': 110,
           'h': 120,
           'color': 'blanchedalmond',
           'x': 780.0,
           'y': 300.0,
           'v': pygame.math.Vector2(),  # placeholder instance (mypy)
           'd': pygame.math.Vector2((0.261, 0.966)),  # placeholder instance (mypy)
           's': 90.0,
           'p': 80.0,
           'r': 50.0,
           'c': 2170.0,
           'f': 40.0,
           'surface': pygame.Surface((0, 0)),  # placeholder instance (mypy)
           'rect': pygame.FRect(),  # placeholder instance (mypy)
           }
monsters.append(monster5)


# TypedDict for PROP_TEMPLATE
PropTemplate = TypedDict('PropTemplate', {
        'name': str,
        'img': str,
        'w': int,
        'h': int,
        'color': str,
        'x': float,
        'y': float,
        'spray_count': int,
        'spray_radius': float,
        'surface': pygame.Surface,
        'rect': pygame.FRect,
        })

# PROP DATA - Initial state for a handful of non-moving props. Includes specs for random instantiation (spraying).
prop_templates = []
prop_template1: PropTemplate = {'name': 'red-flower',
           'img':  'red-flower-66x64.png',
           'w': 66,
           'h': 64,
           'color': 'crimson',
           'x': 640.0,
           'y': 360.0,
           'spray_count': 40,
           'spray_radius': 600.0,
           'surface': pygame.Surface((0, 0)),  # placeholder instance (mypy)
           'rect': pygame.FRect(),  # placeholder instance (mypy)
           }
prop_templates.append(prop_template1)
prop_template2: PropTemplate = {'name': 'blue-flower',
           'img':  'blue-flower-160x158.png',
           'w': 160,
           'h': 158,
           'color': 'darkturquoise',
           'x': 510.0,
           'y': 160.0,
           'spray_count': 10,
           'spray_radius': 480.0,
           'surface': pygame.Surface((0, 0)),  # placeholder instance (mypy)
           'rect': pygame.FRect(),  # placeholder instance (mypy)
           }
prop_templates.append(prop_template2)

# TypedDict for PROP. Props are generated dynamically, when we "spray" props from their template.
Prop = TypedDict('Prop', {
        'name': str,
        'img': str,
        'w': int,
        'h': int,
        'color': str,
        'x': float,
        'y': float,
        'surface': pygame.Surface,
        'rect': pygame.FRect,
        })


# ###############################################    INITIALIZATION    #################################################

pygame.init()

# INITIALIZE THE MAIN DISPLAY SURFACE (SCREEN / WINDOW)
display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)

# INITIALIZE MONSTERS
for monster in monsters:
    if DEBUG:
        monster['surface'] = pygame.Surface((monster['w'], monster['h']))
        monster['surface'].fill(monster['color'])
    else:
        imgpath = os.path.join(ASSET_PATH, monster['img'])
        monster['surface'] = pygame.image.load(imgpath).convert_alpha()

    monster['rect'] = monster['surface'].get_frect(center=(monster['x'], monster['y']))


# INITIALIZE PROPS - 'SPRAY' REPLICATED PROPS (randomly within specified radius, to specified count)
props = []
for prop_t in prop_templates:
    for index in range(prop_t['spray_count']):  # We will use the index for a unique prop name. Not critical.
        # We must create a NEW prop dictionary object each time, otherwise they would all be the same reference.
        prop: Prop = {'name': '',  # placeholder (mpypy)
                'img': prop_t['img'],  # Copy the unchanging attributes from the template before handling dynamic ones.
                'w': prop_t['w'],
                'h': prop_t['h'],
                'color': prop_t['color'],
                'x': 0.0,  # placeholder (mpypy)
                'y': 0.0,  # placeholder (mpypy)
                'surface': pygame.Surface((0, 0)),  # placeholder instance (mypy)
                'rect': pygame.FRect(),  # placeholder instance (mypy)
                }

        diameter = 2.0 * prop_t['spray_radius']  # This variable makes it easier to read/understand. Inline for perf.
        prop['name'] = prop_t['name'] + "-" + str(index)
        x_offset = random.uniform(0.0, diameter) - prop_t['spray_radius']  # uniform() gives a random float value
        y_offset = random.uniform(0.0, diameter) - prop_t['spray_radius']  # uniform() includes the limits
        prop['x'] = prop_t['x'] + x_offset
        prop['y'] = prop_t['y'] + y_offset

        if DEBUG:
            prop['surface'] = pygame.Surface((prop['w'], prop['h']))
            prop['surface'].fill(prop['color'])
        else:
            imgpath = os.path.join(ASSET_PATH, prop['img'])
            prop['surface'] = pygame.image.load(imgpath).convert_alpha()

        prop['rect'] = prop['surface'].get_frect(center=(prop['x'], prop['y']))

        props.append(prop)


# ###############################################    MAIN EXECUTION    #################################################

bgpath = os.path.join(ASSET_PATH, BGIMG)

if DEBUG:
    bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_surface.fill(BGCOLOR)
else:
    bg_surface = pygame.image.load(bgpath)

running = True
ephase = None
ephase_name = None
ephase_count = 0  # 0, not None since we will likly first/always do an arithmetic check on it, not an existence check.
clock = pygame.time.Clock()

#   * * * * * * * * * * * * * * * * * * * *
#   * * * * * *    MAIN LOOP    * * * * * *
#   * * * * * * * * * * * * * * * * * * * *
while running:
    delta_time = clock.tick(TICKRATE) / 1000  # Seconds elapsed for a single frame (e.g. - 60 Frm/sec = 0.017 sec/Frm)
    # print(f"delta_time - duration of one frame - (seconds): {delta_time}")  # ----  DEBUG  ----
    # print(f"FPS - frames per second: {clock.get_fps()}")  # ----  DEBUG  ----
    # #### ####   EVENT LOOP    #### ####
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ENVIRONMENT PHASE PROCESSING - Rotate enviro sequence. Modify monster behavior per their enviro-reaction profiles.
    if ephase is None:
        ephase = ENVIRO_PHASES[0]
        ephase_name = ephase[0]
        ephase_count = ephase[1]
        # print(f"EPHASE name: {ephase_name}    EPHASE count: {ephase_count}")  # ----  DEBUG  ----
        cut_ephase = ENVIRO_PHASES.popleft()
        ENVIRO_PHASES.append(cut_ephase)
        # print(f"ENVIRO_PHASES: {ENVIRO_PHASES}")  # ----  DEBUG  ----
    else:
        # APPLY THE EFFECTS HERE - MONSTERS CHANGE THEIR SPEEDS
        for monster in monsters:
            if ephase_name == 'peace':
                monster['s'] = monster['p']
            elif ephase_name == 'rogue':
                monster['s'] = monster['r']
            elif ephase_name == 'chaos':
                monster['s'] = monster['c']
            elif ephase_name == 'frozen':
                monster['s'] = monster['f']
            else:
                monster['s'] = 10000.0  # Extremely fast, for debugging. A bad ephase name, causes extreme monster speed.

        ephase_count -= 1  # Decrement the counter. TODO: SECONDS?? FRAMES??
        if ephase_count < 1:
            ephase = None


    # ##################################################    DRAW    ####################################################

    # REDRAW THE BG
    if ACID_MODE is False:
        display_surface.blit(bg_surface, (0, 0))

    # DRAW PROPS
    for prop in props:
        display_surface.blit(prop['surface'], prop['rect'])

    # DRAW MONSTERS
    for monster in monsters:
        display_surface.blit(monster['surface'], monster['rect'])

    # pygame.display.update()  # update entire surface or use  .flip() which will update only part of the surface.
    pygame.display.flip()  # Similar to update but not entire screen. TODO: Clarify


    # ################################################    PHYSICS    ###################################################

    for monster in monsters:
        # ***************************
        # WORKING ON THIS MYPY ERROR:
        # delta_vector = pygame.Vector2(monster['d'] * monster['s'])  # SEEN AS A tuple[float, float] - SAME
        delta_vector = monster['d'] * monster['s'] * delta_time
        # MYPY ERROR HERE - TRICKY ONE:
        # main.py:365: error: Incompatible types in assignment (expression has type "Vector2",
        #     variable has type "tuple[float, float]")  [assignment]
        monster['rect'].center += delta_vector
        # ***************************

        # Bounce off LEFT wall in X Axis
        if monster['rect'].left <= 0:
            monster['rect'].left = 0
            monster['d'].x *= -1
            monster['surface'] = pygame.transform.flip(monster['surface'], True, False)

        # Bounce off RIGHT wall in X Axis
        if monster['rect'].right >= SCREEN_WIDTH:
            monster['rect'].right = SCREEN_WIDTH
            monster['d'].x *= -1
            monster['surface'] = pygame.transform.flip(monster['surface'], True, False)

        # Bounce off TOP wall in Y Axis
        if monster['rect'].top <= 0:
            monster['rect'].top = 0
            monster['d'].y *= -1

        # Bounce off BOTTOM wall in Y Axis
        if monster['rect'].bottom >= SCREEN_HEIGHT:
            monster['rect'].bottom = SCREEN_HEIGHT
            monster['d'].y *= -1


pygame.quit()


##
#


# ###################################################    NOTES    ######################################################




##
#
