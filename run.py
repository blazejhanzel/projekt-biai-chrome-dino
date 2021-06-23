import pygame, sys
import neat
import os
import math
from random import randrange

pygame.init()

# System variables
width = 1080
height = 720
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Game variables
color_main = (0, 0, 0)
color_bg = (255, 255, 255)
ground = 400

# Sprites and images
dinoImg = pygame.image.load("Assets/Dino/DinoJump.png")
cactusImg = [pygame.image.load("Assets/Cactus/SmallCactus1.png"), pygame.image.load("Assets/Cactus/SmallCactus2.png"), pygame.image.load("Assets/Cactus/SmallCactus3.png")]
birdImg = pygame.image.load("Assets/Bird.png")


class Bird:
    width = 40
    height = 20
    x = 1080
    y = ground - height
    img = birdImg

    def __init__(self, x=1080):
        self.x = x
        self.width = self.img.get_rect().w
        self.height = self.img.get_rect().h
        self.y = ground - self.height - randrange(50, 150)

    def update(self, delta):
        self.x -= 400 * delta


class Obstacle:
    width = 20
    height = 40
    x = 720
    y = ground - height
    img = cactusImg[randrange(0,2)]

    def __init__(self, x=1400):
        self.x = x
        self.img = cactusImg[randrange(0,2)]
        self.width = self.img.get_rect().w
        self.height = self.img.get_rect().h
        self.y = ground - self.height

    # update function is runned once per frame
    def update(self, delta):
        # Move object to left edge with speed in pixels per second
        self.x -= 400 * delta


class Player:
    width = 88
    height = 94
    x = 70
    y = ground
    target_y = ground
    isJumping = False
    isDucking = False

#    def __init__(self):
#        self.rect = pygame.Rect(self.x, self.y, img.get_width(), img.get_height())

    def jump(self):
        if self.y > ground - 10 and not self.isDucking:
            self.target_y = ground - 300
            self.isJumping = True

    def duckOn(self):
        if not self.isJumping:
            self.y = ground + 47
            self.isDucking = True
    
    def duckOff(self):
        if self.isDucking:
            self.y = ground
            self.isDucking = False

    def update(self, delta):
        # Jumping draw
        if self.target_y < ground and self.y <= self.target_y:
            self.target_y = ground
            self.isJumping = False

        dir = 1 if self.target_y > self.y else (-1 if self.target_y < self.y else 0)
        self.y += dir * 225 * delta / 0.28

        if self.y > ground:
            self.y = ground


def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def remove(index):
    players.pop(index)
    ge.pop(index)
    nets.pop(index)


def eval_genomes(genomes, config):
    print("Wszyscy zgineli, nowa gra")
    global obstacles, players, ge, nets
    # Script managed variables
    players = []
    obstacles = [Obstacle()]
    ge = []
    nets = []

    score = 0.0
    delta = 0.0
    nearestobstacle = Obstacle(2000)
    gameover = False
    scoreshown = False

    for genome_id, genome in genomes:
        players.append(Player())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not scoreshown:
                    print("Score: ", int(score))
                sys.exit(0)

        # Update all
        dt = clock.tick() / 1000.0
        score += dt * 10.0

        for player in players:
            player.update(dt)
        for obstacle in obstacles:
            obstacle.update(dt)

        if len(players) == 0:
            print("Score: ", int(score))
            break

        if obstacles:
            nearestobstacle = obstacles[0]
            nearestobstacleRect = pygame.Rect(obstacles[0].x, ground - obstacles[0].height, obstacles[0].width, obstacles[0].height)

        # Check colliders
        for obstacle in obstacles:
            obstacleRect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)

            if obstacle.x < nearestobstacle.x:
                nearestobstacle = obstacle
                nearestobstacleRect = obstacleRect

            for i, player in enumerate(players):
                playerRect = pygame.Rect(player.x, player.y - player.height + 5, player.width, player.height)
                if playerRect.colliderect(obstacleRect):
                    ge[i].fitness -= 1
                    # gameover = True
                    remove(i)

        for i, player in enumerate(players):
            output = nets[i].activate((player.y,
                                       distance((player.x, player.y), nearestobstacleRect.midtop),
                                       nearestobstacleRect.x, nearestobstacleRect.y, nearestobstacleRect.w, nearestobstacleRect.h))
            # print(distance((playerRect.x, playerRect.y), nearestobstacleRect.midtop))
            # if output[0] > 0.5 and playerRect.y == player.y:
            if output[0] > 0.5:
                player.jump()
            if output[1] > 0.5:
                player.duckOn()
            if output[2] > 0.5:
                player.duckOff()

        # Generate new obstacles and remove old one
        delta += dt
        if delta > 1:
            delta -= 1
            # for i in range(randrange(0, 1)):
        for obstacle in obstacles:
            if obstacle.x < -100:
                obstacles.remove(obstacle)
                rnd = randrange(0, 2)
                if rnd is 0:
                    obstacles.append(Obstacle(randrange(1080, 1700)))
                else:
                    obstacles.append(Bird(randrange(1080, 1700)))

        # Drawing
        screen.fill(color_bg)
        pygame.draw.line(screen, color_main, [0, ground - 10], [width, ground - 10], 1)
        for player in players:
            # pygame.draw.rect(screen, color_main,
                            #  pygame.Rect(player.x, player.y - player.height + 5, player.width, player.height))
            screen.blit(dinoImg, (player.x, player.y - player.height + 5))
        for obstacle in obstacles:
            screen.blit(obstacle.img, (obstacle.x, obstacle.y))
            # pygame.draw.rect(screen, color_main,
            #                  pygame.Rect(obstacle.x, ground - obstacle.height, obstacle.width, obstacle.height))
        pygame.display.flip()


def run(config_file):
    global p
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    # p.add_reporter(neat.StdOutReporter(True))
    # stats = neat.StatisticsReporter()
    # p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    p.run(eval_genomes, 50)
    # loop()

    # show final stats
    # print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.txt')
    run(config_path)
