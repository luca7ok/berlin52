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


def create_population(size):
    population = []
    for _ in range(size):
        individual = list(range(len(points)))
        random.shuffle(individual)
        population.append(individual)
    return population


def selection(population, fitness_list):
    tournament = random.sample(list(zip(population, fitness_list)), 3)
    winner = min(tournament, key=lambda x: x[1])
    return winner[0]


def crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size

    child[start:end] = parent1[start:end]
    child_indices = {v: i for i, v in enumerate(child) if v is not None}
    for gene in parent2:
        if gene not in child_indices:
            idx = child.index(None)
            child[idx] = gene

    return child


def mutate(individual):
    for i in range(len(individual)):
        if random.random() < 0.01:
            j = random.randint(0, len(individual) - 1)
            individual[i], individual[j] = individual[j], individual[i]


def genetic_algorithm(population_size, generations):
    population = create_population(population_size)
    best_individual = min(population, key=total_distance)
    best_distance = total_distance(best_individual)

    for generation in range(generations):
        fitness_list = [total_distance(ind) for ind in population]
        new_population = []

        for _ in range(population_size // 2):
            parent1 = selection(population, fitness_list)
            parent2 = selection(population, fitness_list)
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent2, parent1)
            mutate(child1)
            mutate(child2)
            new_population.extend([child1, child2])

        population = new_population
        current_best = min(population, key=total_distance)
        current_distance = total_distance(current_best)

        if current_distance < best_distance:
            best_individual = current_best[:]
            best_distance = current_distance

    return best_distance, best_individual


def to_screen_coordinates(x, y):
    x_screen = chart_origin[0] + (x / x_max) * chart_width
    y_screen = chart_origin[1] - (y / y_max) * chart_height
    return float(x_screen), float(y_screen)


running = True
best_distance, best_route = genetic_algorithm(100,500)

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
