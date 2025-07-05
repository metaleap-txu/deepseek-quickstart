import pygame
import random
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
SNAKE_SPEED = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow = False
        self.color = GREEN
        self.head_color = BLUE
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.next_direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        # Prevent 180-degree turns
        if len(self.positions) > 1 and (new_head[0] + x, new_head[1] + y) == self.positions[1]:
            self.next_direction = self.direction
            x, y = self.direction
            new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        else:
            self.direction = self.next_direction
        
        if new_head in self.positions[1:]:
            return True  # Game over
        
        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        
        return False  # Game continues
    
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow = False
    
    def render(self, surface):
        for i, p in enumerate(self.positions):
            color = self.head_color if i == 0 else self.color
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def render(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y =), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BLACK, rect, 1)

def show_game_over(surface, score):
    font = pygame.font.SysFont('arial', 36)
    game_over_text = font.render("Game Over!", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to restart", True, WHITE)
    
    surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
    surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    
    snake = Snake()
    food = Food()
    score = 0
    game_over = False
    paused = False
    
    # Font for score
    font = pygame.font.SysFont('arial', 20)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        snake.reset()
                        food.randomize_position()
                        score = 0
                        game_over = False
                else:
                    if event.key == pygame.K_p:
                        paused = not paused
                    elif not paused:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            if snake.direction != DOWN:
                                snake.next_direction = UP
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            if snake.direction != UP:
                                snake.next_direction = DOWN
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            if snake.direction != RIGHT:
                                snake.next_direction = LEFT
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            if snake.direction != LEFT:
                                snake.next_direction = RIGHT
        
        if game_over or paused:
            screen.fill(BLACK)
            if game_over:
                show_game_over(screen, score)
            else:
                pause_text = font.render("PAUSED - Press P to resume", True, WHITE)
                screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
            pygame.display.update()
            clock.tick(SNAKE_SPEED)
            continue
        
        # Update game state
        game_over = snake.update()
        
        # Check if snake ate food
        if snake.get_head_position() == food.position:
            snake.grow = True
            food.randomize_position()
            score += 1
            
            # Make sure food doesn't spawn on snake
            while food.position in snake.positions:
                food.randomize_position()
        
        # Render
        screen.fill(BLACK)
        draw_grid(screen)
        snake.render(screen)
        food.render(screen)
        
        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (5, 5))
        
        pygame.display.update()
        clock.tick(SNAKE_SPEED)

if __name__ == "__main__":
    main()