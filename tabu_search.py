import random
import sys
import pygame
from rgb_gradient import get_linear_gradient

pygame.init()

WIDTH, HEIGHT = 1900, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Berlin 52 TABU Search")

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
        p1 = points[route[i]]
        p2 = points[route[(i + 1)]]
        dist = round(dist + distance(p1, p2), 2)
    dist += distance(points[route[0]], points[route[-1]])
    return dist


def generate_neighbors(route):
    neighbours = []
    for i in range(len(route)):
        for j in range(i + 1, len(route)):
            new_route = route[:]
            new_route[i], new_route[j] = new_route[j], new_route[i]
            neighbours.append(new_route)
    return neighbours


def tabu_search(max_iterations, tabu_size):
    current_route = list(range(len(points)))
    random.shuffle(current_route)
    current_distance = total_distance(current_route)

    tabu_list = []
    best_route = current_route[:]
    best_distance = current_distance

    for iteration in range(max_iterations):
        neighbours = generate_neighbors(current_route)
        neighbours = [n for n in neighbours if n not in tabu_list]
        if not neighbours:
            break

        best_neighbour = min(neighbours, key=total_distance)
        best_neighbour_distance = total_distance(best_neighbour)

        if best_neighbour_distance < best_distance:
            best_route = best_neighbour[:]
            best_distance = best_neighbour_distance

        current_route = best_neighbour[:]
        current_distance = best_neighbour_distance

        tabu_list.append(current_route[:])
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0)
        return best_distance, best_route


def to_screen_coordinates(x, y):
    x_screen = chart_origin[0] + (x / x_max) * chart_width
    y_screen = chart_origin[1] - (y / y_max) * chart_height
    return float(x_screen), float(y_screen)



running = True
best_distance, best_route = tabu_search(100000, 100)

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
    screen.blit(distance_text, (100, 1100))

    pygame.display.flip()

pygame.quit()
sys.exit()
