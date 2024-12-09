import random
import sys
import pygame
from rgb_gradient import get_linear_gradient
import os
from dotenv import load_dotenv

pygame.init()
pygame.font.init()
load_dotenv()

WIDTH = int(os.getenv('WIDTH'))
HEIGHT = int(os.getenv('HEIGHT'))
chart_width = int(os.getenv('CHART_WIDTH'))
chart_height = int(os.getenv('CHART_HEIGHT'))
CHART_ORIGIN_X = int(os.getenv('CHART_ORIGIN_X'))
CHART_ORIGIN_Y = int(os.getenv('CHART_ORIGIN_Y'))
chart_origin = (CHART_ORIGIN_X, CHART_ORIGIN_Y)
CHART_DISTANCE_X = int(os.getenv('CHART_DISTANCE_X'))
CHART_DISTANCE_Y = int(os.getenv('CHART_DISTANCE_Y'))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Berlin 52 Hill Climbing")

font = pygame.font.Font(None, 48)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
intermediate_colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (138, 43, 226)]
gradient = get_linear_gradient(colors=intermediate_colors, nb_colors=52, return_format='rgb')

points = []
with open('input.txt') as file:
    lines = [line.rstrip() for line in file]

for line in lines:
    points.append((float(line.split()[1]), float(line.split()[2])))

x_max = max(x for x, y in points)
y_max = max(y for x, y in points)


def distance(p1, p2):
    return round(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5, 2)


def total_distance(route):
    dist = 0
    for i in range(len(route) - 1):
        p1 = points[route[i]]
        p2 = points[route[(i + 1)]]
        dist = round(dist + distance(p1, p2), 2)
    dist += distance(points[route[0]], points[route[-1]])
    return dist


def generate_neighbors(route):
    new_route = route[:]
    i, j = random.sample(range(len(route)), 2)
    new_route[i], new_route[j] = new_route[j], new_route[i]
    return new_route


def hill_climbing():
    current_route = list(range(len(points)))
    random.shuffle(current_route)
    current_distance = total_distance(current_route)
    while True:
        neighbour_route = generate_neighbors(current_route)
        neighbour_distance = total_distance(neighbour_route)
        if neighbour_distance < current_distance:
            current_route = neighbour_route
            current_distance = neighbour_distance
        else:
            break
    return current_distance, current_route


def to_screen_coordinates(x, y):
    x_screen = chart_origin[0] + (x / x_max) * chart_width
    y_screen = chart_origin[1] - (y / y_max) * chart_height
    return int(x_screen), int(y_screen)


running = True
best_distance, best_route = hill_climbing()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                running = False
    screen.fill(BLACK)

    pygame.draw.line(screen, WHITE, chart_origin, (chart_origin[0], chart_origin[1] - chart_height), 2)
    pygame.draw.line(screen, WHITE, chart_origin, (chart_origin[0] + chart_width, chart_origin[1]), 2)

    for i in range(len(points)):
        screen_x, screen_y = to_screen_coordinates(*points[i])
        if points[i] == points[best_route[0]]:
            pygame.draw.rect(screen, RED, (screen_x - 4, screen_y - 4, 8, 8))
        else:
            pygame.draw.rect(screen, WHITE, (screen_x - 4, screen_y - 4, 8, 8))

    for i in range(len(best_route) - 1):
        p1 = to_screen_coordinates(*points[best_route[i]])
        p2 = to_screen_coordinates(*points[best_route[i + 1]])
        pygame.draw.line(screen, gradient[i], p1, p2, 1)

    p1 = to_screen_coordinates(*points[best_route[0]])
    p2 = to_screen_coordinates(*points[best_route[-1]])
    pygame.draw.line(screen, gradient[51], p1, p2, 1)

    distance_text = font.render(f'Distance: {round(best_distance, 2)}', False, WHITE)
    screen.blit(distance_text, (CHART_DISTANCE_X, CHART_DISTANCE_Y))

    pygame.display.flip()

pygame.quit()
sys.exit()
