"""Snake: a classic arcade game built with pygame."""
import random
import sys

import pygame

CELL = 20
COLS, ROWS = 30, 20
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + 40   # extra space for the score
FPS_START = 8

BLACK, WHITE = (20, 20, 20), (240, 240, 240)
GREEN, DARK_GREEN = (80, 200, 120), (40, 140, 80)
RED, GRAY = (230, 70, 70), (60, 60, 60)

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
KEYS = {pygame.K_UP: UP, pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT,
        pygame.K_w: UP, pygame.K_s: DOWN, pygame.K_a: LEFT, pygame.K_d: RIGHT}


class Snake:
    def __init__(self):
        self.body = [(COLS // 2 - i, ROWS // 2) for i in range(3)]
        self.direction = RIGHT
        self.pending = RIGHT
        self.grow = 0

    @property
    def head(self):
        return self.body[0]

    def turn(self, direction):
        # Ignore a reversal straight into the snake's own neck.
        if (direction[0] + self.direction[0],
                direction[1] + self.direction[1]) != (0, 0):
            self.pending = direction

    def move(self):
        self.direction = self.pending
        x, y = self.head
        dx, dy = self.direction
        self.body.insert(0, (x + dx, y + dy))
        if self.grow:
            self.grow -= 1
        else:
            self.body.pop()

    def hit_wall(self):
        x, y = self.head
        return not (0 <= x < COLS and 0 <= y < ROWS)

    def hit_self(self):
        return self.head in self.body[1:]


def random_food(snake, rng=random):
    free = [(x, y) for x in range(COLS) for y in range(ROWS)
            if (x, y) not in snake.body]
    return rng.choice(free)


class Game:
    def __init__(self, rng=random):
        self.rng = rng
        self.reset()

    def reset(self):
        self.snake = Snake()
        self.food = random_food(self.snake, self.rng)
        self.score = 0
        self.over = False

    def update(self):
        if self.over:
            return
        self.snake.move()
        if self.snake.hit_wall() or self.snake.hit_self():
            self.over = True
        elif self.snake.head == self.food:
            self.score += 1
            self.snake.grow += 2
            self.food = random_food(self.snake, self.rng)

    @property
    def speed(self):
        return FPS_START + self.score // 3

    def draw(self, screen, font):
        screen.fill(BLACK)
        for x in range(COLS):
            for y in range(ROWS):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(screen, (28, 28, 28),
                                     (x * CELL, y * CELL, CELL, CELL))
        fx, fy = self.food
        pygame.draw.circle(screen, RED, (fx * CELL + CELL // 2,
                                         fy * CELL + CELL // 2), CELL // 2 - 2)
        for i, (x, y) in enumerate(self.snake.body):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color,
                             (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2),
                             border_radius=5)
        pygame.draw.rect(screen, GRAY, (0, ROWS * CELL, WIDTH, 40))
        text = f"Score: {self.score}   Speed: {self.speed}"
        if self.over:
            text = f"Game over! Score: {self.score}   Press R or Esc"
        screen.blit(font.render(text, True, WHITE), (10, ROWS * CELL + 8))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    font = pygame.font.Font(None, 30)
    clock = pygame.time.Clock()
    game = Game()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game.over:
                    game.reset()
                elif event.key in KEYS:
                    game.snake.turn(KEYS[event.key])
        game.update()
        game.draw(screen, font)
        pygame.display.flip()
        clock.tick(game.speed)


if __name__ == "__main__":
    main()
