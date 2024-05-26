import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 700, 500
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7
FONT = pygame.font.SysFont("times new roman", 30)
WINNING_SCORE = 10

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong AI Game")


class GameInformation:
    def __init__(self, left_hits, right_hits, left_score, right_score):
        self.left_hits = left_hits
        self.right_hits = right_hits
        self.left_score = left_score
        self.right_score = right_score

class Paddle:
    PADDLECOLOR = WHITE
    MS = 4  

    def __init__(self, x, y, width, height):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, window):
        pygame.draw.rect(window, self.PADDLECOLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.MS
        else:
            self.y += self.MS

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

class Ball:
    MAX_MS = 5  
    COLOR = WHITE

    def __init__(self, x, y, radius):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.radius = radius
        angle = random_angle(-30, 30, [0])
        self.x_MS = self.MAX_MS * math.cos(angle) * (1 if random.random() < 0.5 else -1)
        self.y_MS = self.MAX_MS * math.sin(angle)


    def draw(self, window):
        pygame.draw.circle(window, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_MS
        self.y += self.y_MS

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        angle = random_angle(-30, 30, [0])
        self.x_MS = self.MAX_MS * math.cos(angle) * (1 if random.random() < 0.5 else -1)
        self.y_MS = self.MAX_MS * math.sin(angle)

def random_angle(min_angle, max_angle, excluded_angles):
    angle = 0
    while angle in excluded_angles:
        angle = math.radians(random.randrange(min_angle, max_angle))
    return angle

class Game:
    def __init__(self, window, window_width, window_height):
        self.window = window
        self.window_width = window_width
        self.window_height = window_height
        self.left_paddle = Paddle(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0
        self.game_over = False

    def draw(self, show_hits=False):
        self.window.fill(BLACK)
        self.left_paddle.draw(self.window)
        self.right_paddle.draw(self.window)
        self.ball.draw(self.window)

        if show_hits:
            total_hits = self.left_hits + self.right_hits
            hits_text = FONT.render(f"{total_hits}", 1, WHITE)
            hits_text_position = (WIDTH // 2 - hits_text.get_width() // 2, 20)
            self.window.blit(hits_text, hits_text_position)
        else:
            left_score_text = FONT.render(f"{self.left_score}", 1, WHITE)
            right_score_text = FONT.render(f"{self.right_score}", 1, WHITE)
            self.window.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, 20))
            self.window.blit(right_score_text, (WIDTH * 3/4 - right_score_text.get_width() // 2, 20))


        for i in range(10, HEIGHT, HEIGHT // 20):
            if i % 2 == 1:
                continue
            pygame.draw.rect(self.window, WHITE, (WIDTH // 2 - 5, i, 10, HEIGHT // 20))

        pygame.display.update()

    def move_paddle(self, left, up):
        if left:
            paddle = self.left_paddle
        else:
            paddle = self.right_paddle
        
        if up:
            if paddle.y - paddle.MS >= 0:  
                paddle.move(up=True)
        else:
            if paddle.y + paddle.height + paddle.MS <= HEIGHT:  
                paddle.move(up=False)

    def handle_collisions(self):
        if self.ball.y + self.ball.radius >= HEIGHT or self.ball.y - self.ball.radius <= 0:
            self.ball.y_MS *= -1

        if self.ball.x_MS < 0:
            if self.ball.y >= self.left_paddle.y and self.ball.y <= self.left_paddle.y + self.left_paddle.height:
                if self.ball.x - self.ball.radius <= self.left_paddle.x + self.left_paddle.width:
                    self.ball.x_MS *= -1
                    self.left_hits += 1 
                    middle_y = self.left_paddle.y + self.left_paddle.height / 2
                    difference_y = middle_y - self.ball.y
                    reduction = (self.left_paddle.height / 2) / self.ball.MAX_MS
                    self.ball.y_MS = difference_y / reduction * -1

        elif self.ball.x_MS > 0:
            if self.ball.y >= self.right_paddle.y and self.ball.y <= self.right_paddle.y + self.right_paddle.height:
                if self.ball.x + self.ball.radius >= self.right_paddle.x:
                    self.ball.x_MS *= -1
                    self.right_hits += 1 
                    middle_y = self.right_paddle.y + self.right_paddle.height / 2
                    difference_y = middle_y - self.ball.y
                    reduction = (self.right_paddle.height / 2) / self.ball.MAX_MS
                    self.ball.y_MS = difference_y / reduction * -1

    def check_score(self):
        if self.ball.x < 0:
            self.right_score += 1
            self.ball.reset()
        elif self.ball.x > WIDTH:
            self.left_score += 1
            self.ball.reset()

        if self.left_score >= WINNING_SCORE or self.right_score >= WINNING_SCORE:
            self.game_over = True

    def reset(self):
        self.left_paddle.reset()
        self.right_paddle.reset()
        self.ball.reset()
        self.left_score = 0
        self.right_score = 0
        self.game_over = False

    def loop(self):
        self.ball.move()
        self.handle_collisions()
        
        if self.ball.x < 0:
            self.ball.reset()
            self.right_score += 1
        elif self.ball.x > self.window_width:
            self.ball.reset()
            self.left_score += 1
            
        game_info = GameInformation(
            self.left_hits, self.right_hits, self.left_score, self.right_score)

        return game_info

def main():
    game = Game(WINDOW, WIDTH, HEIGHT)
    clock = pygame.time.Clock()

if __name__ == '__main__':
    main()
