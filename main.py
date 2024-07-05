import math

import pygame
import random
from typing import *

POSITION = Tuple[int, int]

WIDTH = 600
HEIGHT = WIDTH

ROCK_TYPE = 0
PAPER_TYPE = 1
SCISSORS_TYPE = 2

ROCK_IMG = 'rock.png'
PAPER_IMG = 'paper.png'
SCISSORS_IMG = 'scissors.png'
IMAGES = {ROCK_TYPE: ROCK_IMG, PAPER_TYPE: PAPER_IMG, SCISSORS_TYPE: SCISSORS_IMG}


# colors:
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# clock:
REFRESH_RATE = 60


NUM_OF_ELEMENTS = 50
ELEMENT_SIZE = 20
ELEMENT_SPEED = ELEMENT_SIZE / 4


class Vector:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def angle(self):
        return math.atan2(self._y, self._x)

    @property
    def size(self):
        return (self._y ** 2 + self._x ** 2) ** 0.5

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __iadd__(self, vector):
        self._x += vector.x
        self._y += vector.y
        return self

    @classmethod
    def from_radius_and_angle(cls, r, theta):
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        return cls(x, y)


class ScreenObj:
    def __init__(self, image: str, pos: POSITION):
        self._image = pygame.transform.smoothscale(pygame.image.load(image), (ELEMENT_SIZE, ELEMENT_SIZE))
        self._rect = self._image.get_rect()
        self._rect.center = pos

    def draw(self, screen):
        screen.blit(self._image, self._rect.topleft)


class ScreenElement(ScreenObj):
    def __init__(self, my_type, pos):
        super(ScreenElement, self).__init__(IMAGES[my_type], pos)

    def update(self, elements):
        vectors = []
        for element in elements:
            if type(element) == SLAVES[type(self)]:
                vectors.append(self.calculate_vector(element, True))
            elif type(element) == MASTERS[type(self)]:
                vectors.append(self.calculate_vector(element, False))
        sum_vector = Vector(0, 0)
        for vector in vectors:
            sum_vector += vector
        self._update_pos(sum_vector.angle)
        if self.is_touch_master(elements):
            return SLAVES[type(self)](self.pos)
        else:
            return self

    def is_touch_master(self, elements):
        masters = [element for element in elements if MASTERS[type(element)] == type(self)]
        for element in masters:
            if self.is_touch(element):
                return True
        return False

    def is_touch(self, element):
        return self._rect.colliderect(element.rect)

    def _update_pos(self, angle):
        x, y = self._rect.center
        x += math.cos(angle) * ELEMENT_SPEED
        y += math.sin(angle) * ELEMENT_SPEED
        x = min(max(0, x), WIDTH)
        y = min(max(0, y), HEIGHT)
        if (x, y) == self.pos and 0 < x < WIDTH and 0 < y < HEIGHT:
            print('here')
        self._rect.center = (x, y)

    @property
    def pos(self):
        return self._rect.center

    @property
    def rect(self):
        return self._rect

    def calculate_vector(self, element, is_slave):
        x1, y1 = self.pos
        x2, y2 = element.pos
        d = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        try:
            radius = 0.1 * (-1 if is_slave else 1) / d ** 2
        except ZeroDivisionError:
            radius = 0
        angle = math.atan2(y2 - y1, x2 - x1)
        return Vector.from_radius_and_angle(radius, angle)


class Rock(ScreenElement):
    def __init__(self, pos=None):
        if not pos:
            pos = random_pos()
        super(Rock, self).__init__(ROCK_TYPE, pos)


class Paper(ScreenElement):
    def __init__(self, pos=None):
        if not pos:
            pos = random_pos()
        super(Paper, self).__init__(PAPER_TYPE, pos)


class Scissors(ScreenElement):
    def __init__(self, pos=None):
        if not pos:
            pos = random_pos()
        super(Scissors, self).__init__(SCISSORS_TYPE, pos)


MASTERS: Dict[type(ScreenElement), type(ScreenElement)] = {Rock: Scissors, Paper: Rock, Scissors: Paper}
SLAVES = {value: key for key, value in MASTERS.items()}
STRING = {Rock: 'Rock', Paper: 'Paper', Scissors: 'Scissors'}


def random_pos():
    return random.randint(0, WIDTH), random.randint(0, HEIGHT)


def check_for_win(elements):
    if len({type(element) for element in elements}) == 1:
        return STRING[type(elements[0])]
    return ''


def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    elements: List[ScreenElement] = []
    elements += [Rock() for _ in range(NUM_OF_ELEMENTS)]
    elements += [Paper() for _ in range(NUM_OF_ELEMENTS)]
    elements += [Scissors() for _ in range(NUM_OF_ELEMENTS)]
    running = True
    winner = ''
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        elements = [element.update(elements) for element in elements]
        winner = check_for_win(elements)
        if winner:
            running = False
        screen.fill(BLACK)
        for element in elements:
            element.draw(screen)
        pygame.display.flip()
        clock.tick(REFRESH_RATE)
    if winner:
        print(f'the winner is {winner}')


if __name__ == '__main__':
    main()
