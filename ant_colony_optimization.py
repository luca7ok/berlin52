import random
import sys
import pygame
from rgb_gradient import get_linear_gradient
import os
from dotenv import load_dotenv
import time

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
pygame.display.set_caption("Berlin 52 TABU Search")

font = pygame.font.Font(None, 48)

start_time = time.time()

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
    neighbours = []
    for i in range(len(route)):
        for j in range(i + 1, len(route)):
            new_route = route[:]
            new_route[i], new_route[j] = new_route[j], new_route[i]
            neighbours.append(new_route)
    return neighbours


def ant_colony_optimization():
    pheromones = [[1 for _ in range(len(points))] for _ in range(len(points))]
    best_route = None
    best_distance = float('inf')

    for iteration in range(100):
        all_routes = []
        all_distances = []

        for ant in range(30):
            visited = [random.randint(0, len(points) - 1)]
            while len(visited) < len(points):
                current_city = visited[-1]

                probabilities = []
                for next_city in range(len(points)):
                    if next_city in visited:
                        probabilities.append(0)
                    else:
                        pheromone = pheromones[current_city][next_city]
                        heuristic = 1 / (distance(points[current_city], points[next_city]))
                        probabilities.append(pheromone * (heuristic ** 5))

                total_prob = sum(probabilities)
                probabilities = [p / total_prob for p in probabilities]
                next_city = random.choices(range(len(points)), probabilities)[0]
                visited.append(next_city)

            route_distance = total_distance(visited)
            all_routes.append(visited)
            all_distances.append(route_distance)

            if route_distance < best_distance:
                best_distance = route_distance
                best_route = visited

        for i in range(len(points)):
            for j in range(len(points)):
                pheromones[i][j] *= 0.5

        for route, dist in zip(all_routes, all_distances):
            pheromone_deposit = 100 / dist
            for i in range(len(route) - 1):
                pheromones[route[i]][route[i + 1]] += pheromone_deposit
                pheromones[route[i + 1]][route[i]] += pheromone_deposit

            pheromones[route[-1]][route[0]] += pheromone_deposit
            pheromones[route[0]][route[-1]] += pheromone_deposit

    return best_distance, best_route


def to_screen_coordinates(x, y):
    x_screen = chart_origin[0] + (x / x_max) * chart_width
    y_screen = chart_origin[1] - (y / y_max) * chart_height
    return float(x_screen), float(y_screen)


running = True
best_distance, best_route = ant_colony_optimization()
time_text = None

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
    if time_text is None:
        time_text = font.render(f'Time: {round(time.time() - start_time, 2)}', False, WHITE)
    screen.blit(time_text, (CHART_DISTANCE_X + 300, CHART_DISTANCE_Y))

    pygame.display.flip()

pygame.quit()
sys.exit()
