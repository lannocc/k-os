#!/usr/bin/env python
'''
switch.py - Optional utility for starting with DIP switches set.
'''

X = 111
Y = 199

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{X},{Y}' # before pygame import
import pygame

import time
import subprocess


WIDTH  = 123
HEIGHT = 456

SIZE = 27
WAIT = 0.1

BACK = (255, 255, 255)
TEXT = (  0,   0,   0)
ROLL = (211, 255, 222)
PUSH = (123, 222,  99)


pygame.init()
pygame.display.set_caption('DIP Switch')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont(pygame.font.get_default_font(), SIZE)
dip = pygame.Surface((WIDTH - SIZE, HEIGHT / 10))

dips = ''
mouse = None
keys = [ ]
run = False

while run is not None:
    screen.fill(BACK)

    for i in range(10):
        dip.fill(PUSH if chr(i + ord('0')) in dips else ROLL)
        screen.blit(dip, (SIZE, i * HEIGHT / 10))
        text = font.render(str(i), True, TEXT)
        screen.blit(text, (0, i * HEIGHT / 10))

    pygame.display.update()

    if run:
        cmd = ['./start.py', dips]
        print('# '+' '.join(cmd))
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{X+SIZE*2},{Y-WIDTH}'
        subprocess.run(cmd)

        pygame.event.clear()
        mouse = None
        run = False
        print('--- switch ready ---')
        continue

    time.sleep(WAIT)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = None

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BREAK:
                dips = ''
                keys = [ ]

            elif event.key == pygame.K_ESCAPE:
                if keys:
                    keys = [ ]
                else:
                    run = None

            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                run = True

            elif event.unicode >= '0' and event.unicode <= '9':
                keys.append(event.key)

                if event.unicode not in dips:
                    dips += event.unicode
                else:
                    dips = dips.replace(event.unicode, '')

        elif event.type == pygame.KEYUP:
            if event.key in keys:
                del keys[keys.index(event.key)]

                if not keys:
                    run = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse = int(event.pos[1] / HEIGHT * 10) + ord('0')

            if event.button == pygame.BUTTON_LEFT:
                if chr(mouse) not in dips:
                    dips += chr(mouse)

            elif event.button == pygame.BUTTON_RIGHT:
                if chr(mouse) in dips:
                    dips = dips.replace(chr(mouse), '')
                mouse *= -1

            else:
                mouse = None

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT \
                    or event.button == pygame.BUTTON_RIGHT:
                mouse = None

            else:
                run = True

        elif event.type == pygame.MOUSEMOTION:
            if mouse:
                mouse = int(event.pos[1] / HEIGHT * 10) + ord('0')

                if not mouse < 0:
                    if chr(mouse) not in dips:
                        dips += chr(mouse)

                else:
                    if chr(mouse) in dips:
                        dips = dips.replace(chr(mouse), '')
                    mouse *= -1

