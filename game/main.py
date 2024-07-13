#! /usr/bin/env -vS python

import pygame
import os.path
import random


pygame.init()

SCREEN_WIDTH = 1280.0
SCREEN_HEIGHT = 720.0
GAME_TITLE = 'Space Blasto'
BGCOLOR = 'olivedrab'
BGIMG = 'lawn-bg-dark-2560x1440.jpg'  # 'grass-field-med-1920x1249.jpg'  # 'lawn-bg-dark-2560x1440.jpg'
ASSET_PATH = 'assets'  # Relative path with no trailing slash.
DEBUG = False


# MONSTER DATA
monsters = []
monster = {'name': 'red-flower-floaty',
           'img':  'red-flower-66x64.png',
           'w': 66.0,
           'h': 64.0,
           'color': 'red1',
           'x': 240.0,
           'y': 300.0,
           'xv': -0.03,
           'yv': 0.01,
           }
monsters.append(monster)
monster = {'name': 'red-flower-drifty',
           'img':  'red-flower-66x64.png',
           'w': 66.0,
           'h': 64.0,
           'color': 'orangered',
           'x': 240.0,
           'y': 300.0,
           'xv': 0.032,
           'yv': -0.033,
           }
monsters.append(monster)
monster = {'name': 'goldie',
           'img':  'gold-retriever-160x142.png',
           'w': 160.0,
           'h': 142.0,
           'color': 'gold',
           'x': 500.0,
           'y': 300.0,
           'xv': 0.042,
           'yv': -0.03,
           }
monsters.append(monster)
monster = {'name': 'fishy',
           'img':  'goldfish-280x220.png',
           'w': 280.0,
           'h': 220.0,
           'color': 'darkgoldenrod1',
           'x': 840.0,
           'y': 300.0,
           'xv': -0.07,
           'yv': -0.15,
           }
monsters.append(monster)
monster = {'name': 'grumpy',
           'img':  'grumpy-cat-110x120.png',
           'w': 110.0,
           'h': 120.0,
           'color': 'blanchedalmond',
           'x': 780.0,
           'y': 300.0,
           'xv': 0.11,
           'yv': 0.04,
           }
monsters.append(monster)


# PROP DATA
prop_templates = []
prop_template = {'name': 'red-flower',
           'img':  'red-flower-66x64.png',
           'w': 66.0,
           'h': 64.0,
           'color': 'purple',
           'x': 640.0,
           'y': 360.0,
           'spray_count': 40,
           'spray_radius': 600.0,
           }
prop_templates.append(prop_template)


# DISPLAY SURFACE
display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)

# INITIALIZE MONSTERS
for monster in monsters:
    if DEBUG:
        monster['surface'] = pygame.Surface(monster['w'], monster['h'])
        monster['surface'].fill(monster['color'])
    else:
        imgpath = os.path.join(ASSET_PATH, monster['img'])
        monster['surface'] = pygame.image.load(imgpath).convert_alpha()

    monster['rect'] = monster['surface'].get_rect(center=(monster['x'], monster['y']))


# INITIALIZE PROPS - 'SPRAY' REPLICATED PROPS (randomly within specified radius)
props = []
for prop_t in prop_templates:
    for index in range(prop_t['spray_count']):  # We will use the index for a unique prop name. Not critical.
        # We must create a NEW prop dictionary object each time, otherwise they would all be the same reference.
        prop = {'img': prop_t['img'],  # Copy the unchanging attributes from the template before handling dynamic ones.
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

        prop['rect'] = prop['surface'].get_rect(center=(prop['x'], prop['y']))

        props.append(prop)


# ###############################################    MAIN EXECUTION    #################################################

bgpath = os.path.join(ASSET_PATH, BGIMG)
bg_surface = pygame.image.load(bgpath)

running = True
while running:
    # #### ####   EVENT LOOP    #### ####
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # ################################################    PHYSICS    ###################################################
    # Calculations for new object positions, collisions, velocity changes and update of related object state.
    # CALCULATIONS FOR NEW POSITIONS, BOUNCING
    for monster in monsters:

        # **************************************************************************************************************
        # * IDEA: For position updates, we might be able to do this to ANY of the named corners or sides.
        # The rect is designed to update all the related values and then the surface uses the updated rect
        # however it needs to when it is time to blit. It would be irrelevant as to what particular point
        # was used to update the position of the entire rect. SO, while we will still look closely at Vectors,
        # this may take us closer to what we want, regarding the stuff I am trying below.
        # I am trying to update the position of the rect and was looking for a .centerx and a .centery or
        # or something similar, but since I can update and reference at the same time ( or even more accurately,
        # reference and update at the same time), I SHOULD be able to do this:
        # monster['rect'].left += monster['xv']
        # monster['rect'].top += monster['yv']
        # **************************************************************************************************************

        # TODO: We might want to change this logic. Currently we move before collision detect etc. and treat
        # it like prep for the next iteration. Just doesn't feel right and some of our bounces show it happening
        # too far from the edge. This might be why we never fully hit the edge sometimes. Regardsless of the bounce
        # issue, this just does not feel like the right order of things. But we still need to strategically figure
        # out our major processing steps and their order, so this is working great for an early pass.
        # THEN AGAIN, from one perspective, it makes sense that before we draw, we account for the motion that
        # does exist. This motion was taking place while the last frame was displaying (statically) .. each frame
        # is a snapshot of a slice of time, but that time keeps moving, so the motion keeps moving, so one might
        # logically say that accounting for that movement which HAS OCCURRED, since the last frame was frozen is
        # a good FIRST THING to do, before drawing THE CURRENT FRAME.
        # This means that our objects will never be displayed in their x, y start positions defined in the initial
        # config data. (We could add an initialization step prior to the main loop that DID display them in this
        # initial state, and that would be great, but we are discussing the structure of the main loop and when
        # we update values vs. when we paint the current state of values.
        # Right now, I'm OK with calculation physics and new values prior to painting. It sort of does not matter,
        # but it DOES. There are factors and edge-cases where it does matter, so this is still in flux, but for now,
        # the current structure is logical to me. I have coded such tight real-time loops before in BOTH ways,
        # with state updates both before and alternately after the primary actions using the state. It depends what
        # you are doing. Some state might need to be updated before and then some after. What is important, is to
        # continually re-asses your design patterns and how it all works currently and how the structure and
        # design patterns will affect you down the road as the app evolves.
        # So I will keep the calcs before the drawing for now.

        # NOTE: We must copy and modify rect position values and re-assign rect.center with a composed tuple,
        # because our intuitive (and per docs) attempts to reference and assign at the same time some rect
        # position values, failed. LONG-TERM, looking at vectors, SHORT-TERM, using this intermediate tuple is fine.
        monster['x'] += monster['xv']
        monster['y'] += monster['yv']
        # monster['rect'].left += monster['xv']  # Did not work
        # monster['rect'].top += monster['yv']  # Did not work
        # SOLUTION: Use intermediate variables (hence a copy and not a reference) and re-assign rect.center with tuple.
        newx = monster['x']
        newy = monster['y']
        monster['rect'].topleft = (newx, newy)
        # DEBUG OUTPUT
        # PROBLEM TO ANALYZE: * * * THE RECT VALUES ARE ALWAYS INT * * *
        # * * * RELATED CONCLUSION - DON'T USE RECT FOR SOURCE OF TRUTH. 'x' and 'y' are the correct design.
        # * * * SOURCE OF TRUTH MUST BE FLOATS. RECTS ARE --ONLY-- INTS. PURPOSE OF RECTS IS Surface positioning.
        # * * * RECTS are not intended to hold WORLD source of truth data/position. (Which needs to be floats etc.)
        print(f"x, y        {monster['x']}, {monster['y']}")  # ----  DEBUG  ----
        print(f"left, top   {monster['rect'].left}, {monster['rect'].top}")  # ----  DEBUG  ----
        # SUMMARY: The current solution has the source of truth as the 'x' and 'y' attributes of the object.
        # My goal is to have the source of truth (for position etc.) to be encapsulated in the 'rect' attribute,
        # which is a PyGame rect object. We want to only update and reference the rect. The x and y can be used for
        # initial position or similar, but it is redundant to update x and y after we have a rect instantiated inside
        # the 'rect' attribute. Where I am currently stuck is being able to reference and update the values inside the
        # rect in the same real-time/simultaneous manner I can do with the scalar values inside 'x' and 'y'. The docs
        # and intuition imply I can do that, but tests so far have failed.
        # Again, I need to look at vectors for some of these use-cases, but I STILL feel I can acheive my goal of
        # ONLY using the rect.



        # Bounce off LEFT wall in X Axis
        if monster['rect'].left < 0:
            monster['rect'].left = 0  # Stop at the LEFT edge instead of passing it.
            monster['xv'] = monster['xv'] * -1  # Reverse X-Axis speed/velocity
        # Bounce off RIGHT wall in X Axis
        if monster['rect'].right > SCREEN_WIDTH:
            monster['rect'].right = SCREEN_WIDTH  # Stop at the RIGHT edge instead of passing it.
            monster['xv'] = monster['xv'] * -1  # Reverse X-Axis speed/velocity

        # Bounce off TOP wall in Y Axis
        if monster['rect'].top < 0:
            monster['rect'].top = 0  # Stop at the TOP edge instead of passing it.
            monster['yv'] = monster['yv'] * -1  # Reverse Y-Axis speed/velocity
        # Bounce off BOTTOM wall in Y Axis
        if monster['rect'].bottom > SCREEN_HEIGHT:
            monster['rect'].bottom = SCREEN_HEIGHT  # Stop at the BOTTOM edge instead of passing it.
            monster['yv'] = monster['yv'] * -1  # Reverse Y-Axis speed/velocity


    #display_surface.fill(BGCOLOR)  # Normally we always re-draw the BG.

    # Paint the BG image every time. Paint the bg_surface (blit it) onto the main display_surface at coords (0, 0)
    display_surface.blit(bg_surface, (0, 0))

    # ##################################################    DRAW    ####################################################

    # DRAW PROPS
    for prop in props:
        prop['rect'] = prop['surface'].get_rect(topleft=(prop['x'], prop['y']))  # TODO: Refactor to center
        display_surface.blit(prop['surface'], prop['rect'])

    # DRAW MONSTERS
    for monster in monsters:
        display_surface.blit(monster['surface'], monster['rect'])

    # pygame.display.update()  # update entire surface or use  .flip() which will update only part of the surface.
    pygame.display.flip()  # Similar to update but not entire screen. TODO: Clarify


pygame.quit()


##
#


# TUTORIAL VIDEO  (Notice some comments have a Video Timing Marker: Vid28:46)
# This video is over 11 hours long and covers about 5 different games and a lot of PyGame details.
# https://www.youtube.com/watch?v=8OMghdHP-zs

# DOCS:
# https://pyga.me/docs/

# PyGame vs Arcade:
# https://aircada.com/pygame-vs-arcade/

# Named Colors:
# https://pyga.me/docs/ref/color_list.html

# GENERAL NOTES:

# "Surface" v.s. a "display surface". They are very similar. "display surface" is the main surface we draw on.
# The ONE we see. We can attach multiple "Surface" objects to the one official "display surface".

# Technically a speed is an absolute value, but a velocity (in one dimension, as we are currently dealing with it)
# is just a speed with a positive or negative sign. (A speed with direction indicated.)
# A velocity is both a speed and a direction, and direction has dimensions, one, two or three, usually.

# ----------------------------------------------------------------------------------------------------------------------

# Rectangles (FRects)  (rectangles with a size and position)

# CORNERS  (assign a tuple of coordinates):
# topleft              midtop              topright
# midleft                 center             midright
# bottomleft             midbottom          bottomright

# SIDES  (assign a single axis value):
#                        top
# left                                        right
#                       bottom

# CREATE standalone OR CREATE from SURFACE
# pygame.FRect(pos, size)  # standalone
# surface.get_frect(point=pos)

# GITHUB EXPERIMENT: Changing email and username to match those previously used. Trying to solve issue with
# contribution tracking. This comment will be pushed to test the fix. FIXED. The contribution was immediately
# recognized. See the GitHub info page on how contributions tracked. Email/username MUST be correct. See the specs.
# This issue has been fixed and this comment will soon be removed.

