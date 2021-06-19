import pygame, sys
from random import randrange

pygame.init()


# System variables
width = 480
height = 320
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Game variables
color_main = (0, 0, 0)
color_bg = (255, 255, 255)
ground = 200


class Obstacle:
    width = 20
    height = 40
    x = 720

    def __init__(self, x = 720):
        self.x = x
    
    # update function is runned once per frame
    def update(self, delta):
        # Move object to left edge with speed in pixels per second
        self.x -= 400 * delta

class Player:
    width = 30
    height = 60
    x = 70
    y = ground
    target_y = ground

    def jump(self):
        if (self.y > ground - 10):
            self.target_y = ground - 150

    def update(self, delta):
        # Jumping draw
        if self.target_y < ground and self.y <= self.target_y:
            self.target_y = ground

        dir = 1 if self.target_y > self.y else (-1 if self.target_y < self.y else 0)
        self.y += dir * 150 * delta / 0.28
        
        if self.y > ground:
            self.y = ground


# Script managed variables
player = Player()
obstacles = [Obstacle()]
score = 0.0
delta = 0.0
gameover = False
scoreshown = False


while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if not scoreshown:
                print("Score: ", int(score))
            sys.exit(0)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            if gameover:
                player = Player()
                obstacles = [Obstacle()]
                score = 0.0
                delta = 0.0
                gameover = False
                scoreshown = False
            else:
                player.jump()

    # Gameover behaviour
    if gameover:
        if not scoreshown:
            print("Score: ", int(score))
            scoreshown = True
        continue

    # Update all
    dt = clock.tick() / 1000.0
    score += dt * 10.0
    player.update(dt)
    for obstacle in obstacles:
        obstacle.update(dt)

    # Check colliders
    playerRect = pygame.Rect(player.x, player.y - player.height + 5, player.width, player.height)
    for obstacle in obstacles:
        obstacleRect = pygame.Rect(obstacle.x, ground - obstacle.height, obstacle.width, obstacle.height)
        if playerRect.colliderect(obstacleRect):
            gameover = True

    # Generate new obstacles and remove old one
    delta += dt
    if delta > 1:
        delta -= 1
        for i in range(randrange(0,2)):
            obstacles.append(Obstacle(randrange(720, 1080)))
    for obstacle in obstacles:
        if obstacle.x < -100:
            obstacles.remove(obstacle)

    # Drawing
    screen.fill(color_bg)
    pygame.draw.line(screen, color_main, [0, ground - 10], [width, ground - 10], 1)
    pygame.draw.rect(screen, color_main, pygame.Rect(player.x, player.y - player.height + 5, player.width, player.height))
    for obstacle in obstacles:
        pygame.draw.rect(screen, color_main, pygame.Rect(obstacle.x, ground - obstacle.height, obstacle.width, obstacle.height))
    pygame.display.flip()
