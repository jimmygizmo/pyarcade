#! /usr/bin/env -vS python

import pygame
from typing import TypedDict
import os.path
import random


# ###############################################    CONFIGURATION    ##################################################

SCREEN_WIDTH = 1280.0
SCREEN_HEIGHT = 720.0
TICKRATE = 60
GAME_TITLE = 'Space Blasto'
BGCOLOR = 'olivedrab'
BGIMG = 'lawn-bg-dark-2560x1440.jpg'  # 'grass-field-med-1920x1249.jpg'  # 'lawn-bg-dark-2560x1440.jpg'
ASSET_PATH = 'assets'  # Relative path with no trailing slash.
DEBUG = False


# Using a TypedDict to satisfy MyPy recommendations for type-hinting/strong-typing.
# TypeDict for MONSTER
Monster = TypedDict('Monster', {
        'name': str,
        'img': str,
        'w': int,
        'h': int,
        'color': str,
        'x': float,
        'y': float,
        'v': pygame.math.Vector2,
        'xv': float,
        'yv': float,
        'surface': pygame.Surface,
        'rect': pygame.FRect,
        })

# MONSTER DATA - Initial state for a handful of entities that move, experience physics and interact. W/initial motion.
monsters = []
monster: Monster = {'name': 'red-flower-floaty',
           'img':  'red-flower-66x64.png',
           'w': 66,
           'h': 64,
           'color': 'red1',
           'x': 240.0,
           'y': 300.0,
           'v': None,
           'xv': -0.73,
           'yv': 0.49,
           'surface': None,
           'rect': None,
           }
monsters.append(monster)
monster: Monster = {'name': 'red-flower-drifty',
           'img':  'red-flower-66x64.png',
           'w': 66,
           'h': 64,
           'color': 'orangered',
           'x': 240.0,
           'y': 300.0,
           'v': None,
           'xv': 0.132,
           'yv': -0.033,
           'surface': None,
           'rect': None,
           }
monsters.append(monster)
monster: Monster = {'name': 'goldie',
           'img': 'gold-retriever-160x142.png',
           'w': 160,
           'h': 142,
           'color': 'gold',
           'x': 500.0,
           'y': 300.0,
           'v': None,
           'xv': 3.2,
           'yv': 3.9,
           'surface': None,
           'rect': None,
           }
monsters.append(monster)
monster: Monster = {'name': 'fishy',
           'img':  'goldfish-280x220.png',
           'w': 280,
           'h': 220,
           'color': 'darkgoldenrod1',
           'x': 840.0,
           'y': 300.0,
           'v': None,
           'xv': -2.07,
           'yv': -3.15,
           'surface': None,
           'rect': None,
           }
monsters.append(monster)
monster: Monster = {'name': 'grumpy',
           'img':  'grumpy-cat-110x120.png',
           'w': 110,
           'h': 120,
           'color': 'blanchedalmond',
           'x': 780.0,
           'y': 300.0,
           'v': None,
           'xv': 2.11,
           'yv': 1.04,
           'surface': None,
           'rect': None,
           }
monsters.append(monster)


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
prop_template: PropTemplate = {'name': 'red-flower',
           'img':  'red-flower-66x64.png',
           'w': 66,
           'h': 64,
           'color': 'crimson',
           'x': 640.0,
           'y': 360.0,
           'spray_count': 40,
           'spray_radius': 600.0,
           'surface': None,
           'rect': None,
           }
prop_templates.append(prop_template)
prop_template: PropTemplate = {'name': 'blue-flower',
           'img':  'blue-flower-160x158.png',
           'w': 160,
           'h': 158,
           'color': 'darkturquoise',
           'x': 510.0,
           'y': 160.0,
           'spray_count': 10,
           'spray_radius': 480.0,
           'surface': None,
           'rect': None,
           }
prop_templates.append(prop_template)

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
        # Instantiate the velocity vector with the TRUTH xv and yv values. This initial stub may soon change.
        monster['v'] = pygame.math.Vector2(monster['xv'], monster['yv'])
    else:
        imgpath = os.path.join(ASSET_PATH, monster['img'])
        monster['surface'] = pygame.image.load(imgpath).convert_alpha()
        # Instantiate the velocity vector with the TRUTH xv and yv values. This initial stub may soon change.
        monster['v'] = pygame.math.Vector2(monster['xv'], monster['yv'])

    monster['rect'] = monster['surface'].get_frect(center=(monster['x'], monster['y']))


# INITIALIZE PROPS - 'SPRAY' REPLICATED PROPS (randomly within specified radius, to specified count)
props = []
for prop_t in prop_templates:
    for index in range(prop_t['spray_count']):  # We will use the index for a unique prop name. Not critical.
        # We must create a NEW prop dictionary object each time, otherwise they would all be the same reference.
        prop: Prop = {'img': prop_t['img'],  # Copy the unchanging attributes from the template before handling dynamic ones.
                'w': prop_t['w'],
                'h': prop_t['h'],
                'color': prop_t['color'],
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
clock = pygame.time.Clock()

while running:
    clock.tick(TICKRATE)
    # #### ####   EVENT LOOP    #### ####
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # ##################################################    DRAW    ####################################################

    # REDRAW THE BG
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
    # Calculations for new object positions, collisions, velocity changes and update of related object state.
    # CALCULATIONS FOR NEW POSITIONS, BOUNCING

    for monster in monsters:


        # MOVE TRUE POSITION PER VELOCITY - Maintain the source of truth as FLOAT values in the primary data structure.
        # monster['x'] += monster['xv']
        # monster['y'] += monster['yv']
        # newx = monster['x']
        # newy = monster['y']
        # monster['rect'].center = (newx, newy)

        # NEW WAY USING VECTORS - While moving experimentally towards using the FRect for a less-accurate truth:

        # We still need to maintain the truth values .. but, with FRect accuracy to 4 or 5 decimal places (float does
        # remain much more accurat than that .. but 4 or 5 in FRect may be sufficient) .. then with that AND also
        # the convenience of vectors, the plan is to EXPLORE the use of the rect to maintain truth. This will
        # relegate x, y, xv, yv attributes to being initial state only and then after that the objects rect will be
        # the source of truth. THIS WILL BE AN EXPERIMENT AT FIRST. We can always go back to maintaining truth in
        # the fully-float-capable object data structures. Do we need accuracies on the scale of one-ten-thousandth of
        # a pixel and greater? In some applications, absolutely! But in games? Maybe most of the time we do not need
        # that accuracy and the many types of convenience of FRect/Rect in PyGame-CE will lead to the decision to
        # use the FRect as source of truth (in most cases.) I can see things going that way, at least initially. I may
        # leave concisely-commented stubs in place where one can easily go back to maintaining a much more accurate
        # source of truth (on position and velocity, mostly, we are talking about here.)
        monster['x'] += monster['xv']
        monster['y'] += monster['yv']
        # Then we can very simply update position and don't necessarily need the above step to maintain the orig. truth.
        # print(monster['v'])  # ----  DEBUG  ----
        monster['rect'].center += monster['v']


        # Bounce off LEFT wall in X Axis
        if monster['rect'].left <= 0:
            monster['rect'].left = 0  # Great! We don't touch the TRUTH VALUE. We do bound the Surface on screen.
            monster['xv'] = monster['xv'] * -1
            # Experimental transition to using vectors: We need to update the vector here too:
            # IMPORTANT: Can/should we update using methods rather than instantiate a new/replacement object?
            monster['v'] = pygame.math.Vector2(monster['xv'], monster['yv'])

        # Bounce off RIGHT wall in X Axis
        if monster['rect'].right >= SCREEN_WIDTH:
            monster['rect'].right = SCREEN_WIDTH  # Great! We don't touch the TRUTH VALUE. We do bound the Surface.
            monster['xv'] = monster['xv'] * -1
            # Experimental transition to using vectors: We need to update the vector here too:
            # IMPORTANT: Can/should we update using methods rather than instantiate a new/replacement object?
            monster['v'] = pygame.math.Vector2(monster['xv'], monster['yv'])

        # Bounce off TOP wall in Y Axis
        if monster['rect'].top <= 0:
            monster['rect'].top = 0  # Great! We don't touch the TRUTH VALUE. We do bound the Surace on screen.
            monster['yv'] = monster['yv'] * -1
            # Experimental transition to using vectors: We need to update the vector here too:
            # IMPORTANT: Can/should we update using methods rather than instantiate a new/replacement object?
            monster['v'] = pygame.math.Vector2(monster['xv'], monster['yv'])
        # Bounce off BOTTOM wall in Y Axis
        if monster['rect'].bottom >= SCREEN_HEIGHT:
            monster['rect'].bottom = SCREEN_HEIGHT  # Great! We don't touch the TRUTH VALUE. We do bound the Surface.
            monster['yv'] = monster['yv'] * -1
            # Experimental transition to using vectors: We need to update the vector here too:
            # IMPORTANT: Can/should we update using methods rather than instantiate a new/replacement object?
            monster['v'] = pygame.math.Vector2(monster['xv'], monster['yv'])


pygame.quit()


##
#


# ###################################################    NOTES    ######################################################




##
#
