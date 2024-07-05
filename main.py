import datetime
import math
import pygame
import random
from typing import *
import cv2

POSITION = Tuple[int, int]

pygame.display.init()

# Set the screen size to the current display size
WIDTH = 1000#pygame.display.Info().current_w - 100
HEIGHT = 500#pygame.display.Info().current_h - 100

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
REFRESH_RATE = 30


NUM_OF_ELEMENTS = 50
ELEMENT_SIZE = 30
ELEMENT_SPEED = ELEMENT_SIZE / 4

GRAVITY_CONSTANT = 300

ARROW_HEAD_LENGTH = 3


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

    @classmethod
    def center_vector(cls, pos):
        avg_size = GRAVITY_CONSTANT * min(NUM_OF_ELEMENTS/3, 10)
        x1, y1 = WIDTH // 2, HEIGHT // 2
        x2, y2 = pos
        d = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        radius = - avg_size * (d / (WIDTH * HEIGHT)) ** 2
        a = math.atan2(y2 - y1, x2 - x1)
        return cls.from_radius_and_angle(radius, a)

    def draw(self, screen, pos, color=WHITE):
        start_x, start_y = pos
        end_x, end_y = start_x + self._x*100000, start_y + self._y*100000
        # Calculate the direction of the vector
        length = math.sqrt((end_x-start_x) ** 2 + (end_y-start_y) ** 2)
        if length > ARROW_HEAD_LENGTH:
            # Normalize the vector
            dx = (end_x-start_x) / length
            dy = (end_y-start_y) / length
            # Calculate the points of the arrowhead
            arrowhead_left = (end_x - ARROW_HEAD_LENGTH * dx + ARROW_HEAD_LENGTH * dy,
                              end_y - ARROW_HEAD_LENGTH * dy - ARROW_HEAD_LENGTH * dx)
            arrowhead_right = (end_x - ARROW_HEAD_LENGTH * dx - ARROW_HEAD_LENGTH * dy,
                               end_y - ARROW_HEAD_LENGTH * dy + ARROW_HEAD_LENGTH * dx)
            # Draw the vector
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 1)
            # Draw the arrowhead
            pygame.draw.polygon(screen, color, [(end_x, end_y), arrowhead_left, arrowhead_right])


class ScreenObj:
    def __init__(self, image: str, pos: POSITION):
        self._image = pygame.transform.smoothscale(pygame.image.load(image), (ELEMENT_SIZE, ELEMENT_SIZE))
        self._rect = self._image.get_rect()
        self._pos = pos
        self._rect.center = pos

    def draw(self, screen):
        screen.blit(self._image, self._rect.topleft)


class ScreenElement(ScreenObj):
    def __init__(self, my_type, pos):
        super(ScreenElement, self).__init__(IMAGES[my_type], pos)
        self._vectors = []
        self._sum_vector = Vector(0, 0)
        self._center_vector = Vector(0, 0)

    def update(self, elements):
        vectors = []
        masters, slaves = 0, 0
        for element in elements:
            if type(element) == MASTERS[type(self)]:
                masters += 1
            elif type(element) == SLAVES[type(self)]:
                slaves += 1
        for element in elements:
            if type(element) == SLAVES[type(self)]:
                vectors.append(self.calculate_vector(element, True, masters, slaves))
            elif type(element) == MASTERS[type(self)]:
                vectors.append(self.calculate_vector(element, False, masters, slaves))
            elif type(element) == type(self):
                vectors.append(self.calculate_vector(element, True, NUM_OF_ELEMENTS, NUM_OF_ELEMENTS))
        sum_vector = Vector(0, 0)
        for vector in vectors:
            sum_vector += vector
        self._center_vector = Vector.center_vector(self.pos)
        sum_vector += self._center_vector
        self._vectors = vectors
        self._sum_vector = sum_vector
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
        x, y = self._pos
        x += math.cos(angle) * ELEMENT_SPEED
        y += math.sin(angle) * ELEMENT_SPEED
        x = min(max(0, x), WIDTH)
        y = min(max(0, y), HEIGHT)
        self._pos = (x, y)
        self._rect.center = self._pos

    @property
    def pos(self):
        return self._rect.center

    @property
    def rect(self):
        return self._rect

    def calculate_vector(self, element, is_slave, masters, slaves):
        x1, y1 = self.pos
        x2, y2 = element.pos
        d = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        try:
            radius = (-slaves / (masters+0.01) if is_slave else masters / (slaves+0.01)) / d ** 2
        except ZeroDivisionError:
            radius = 0
        angle = math.atan2(y2 - y1, x2 - x1)
        return Vector.from_radius_and_angle(radius, angle)

    def draw(self, screen):
        super(ScreenElement, self).draw(screen)
        # for vector in self._vectors:
        #     vector.draw(screen, self.pos)
        # self._sum_vector.draw(screen, self.pos, GREEN)
        self._center_vector.draw(screen, self.pos, RED)


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


# def create_video(screen, video_writer):
#     success = False
#     while not success:
#         try:
#             pygame.image.save(screen, 'screenshot.png')
#             image = cv2.imread("screenshot.png")
#             video_writer.write(image)
#             success = True
#         except pygame.error:
#             print('error')


def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    index = 0
    while running:
        winner = ''
        loop_counter = 0
        elements: List[ScreenElement] = []
        elements += [Rock() for _ in range(NUM_OF_ELEMENTS)]
        elements += [Paper() for _ in range(NUM_OF_ELEMENTS)]
        elements += [Scissors() for _ in range(NUM_OF_ELEMENTS)]
        # fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        # video_writer = cv2.VideoWriter(f"video{index}.avi", fourcc, 30.0, (WIDTH, HEIGHT))
        a = datetime.datetime.now()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill(BLACK)
            elements = [element.update(elements) for element in elements]
            winner = check_for_win(elements)
            if winner:
                running = False
            for element in elements:
                element.draw(screen)
            pygame.display.flip()
            # create_video(screen, video_writer)
            loop_counter += 1
            clock.tick(REFRESH_RATE)
        print(datetime.datetime.now() - a)
        if winner:
            print(f'the winner is {winner}, {loop_counter}')
            running = True
        # video_writer.release()
        index += 1


if __name__ == '__main__':
    main()
