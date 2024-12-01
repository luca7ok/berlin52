import random
import sys

import pygame

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1900, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Berlin 52")

font = pygame.font.Font(None, 72)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (138, 43, 226)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

points = []
with open('input.txt') as file:
    lines = [line.rstrip() for line in file]

for line in lines:
    points.append((float(line.split()[1]), float(line.split()[2])))

chart_origin = (100, 1000)
chart_width = 1700
chart_height = 900

x_max = max(x for x, y in points)
y_max = max(y for x, y in points)


def distance(p1, p2):
    return round(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5, 2)


def total_distance(route):
    dist = 0
    for i in range(len(route) - 1):
        start = points[route[i]]
        end = points[route[(i + 1)]]
        dist = round(dist + distance(start, end), 2)
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


font = pygame.font.Font(None, 24)

running = True
best_distance, best_route = hill_climbing()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    pygame.draw.line(screen, WHITE, chart_origin, (chart_origin[0], chart_origin[1] - chart_height), 2)
    pygame.draw.line(screen, WHITE, chart_origin, (chart_origin[0] + chart_width, chart_origin[1]), 2)

    for index in range(len(points)):
        screen_x, screen_y = to_screen_coordinates(*points[index])
        if index == 0:
            pygame.draw.rect(screen, RED, (screen_x - 4, screen_y - 4, 8, 8))
        else:
            pygame.draw.rect(screen, GREEN, (screen_x - 4, screen_y - 4, 8, 8))

    for i in range(len(best_route) - 1):
        p1 = to_screen_coordinates(*points[best_route[i]])
        p2 = to_screen_coordinates(*points[best_route[i + 1]])
        pygame.draw.line(screen, PURPLE, p1, p2, 1)

    p1 = to_screen_coordinates(*points[best_route[0]])
    p2 = to_screen_coordinates(*points[best_route[-1]])
    pygame.draw.line(screen, PURPLE, p1, p2, 1)

    distance_text = font.render(f'Distance: {best_distance}', False, WHITE)
    route_text = font.render(f'Route: {best_route}', False, WHITE)
    screen.blit(distance_text, (100, 1100))
    screen.blit(route_text, (100, 1150))

    pygame.display.flip()

pygame.quit()
sys.exit()
