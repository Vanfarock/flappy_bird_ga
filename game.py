from typing import List
from genetic import Genetic
import pygame
import random

COLORS = {
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (14, 120, 56),
}
GRAVITY = 80
MAX_FPS = 60
DISTANCE_BETWEEN_PIPES = 500
MIN_GAP = 100
MAX_GAP = 100
PIXELS_PER_SECOND = 1000

current_fps = MAX_FPS
camera_speed = PIXELS_PER_SECOND / current_fps

class Game:
    def __init__(self, width: int, height: int):    
        self.width = width
        self.height = height
        self.running = True
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = None
        self.genetic = Genetic()

        self.camera = None
        self.players = []
        self.pipes = []
        self.first_pipe = None

        self.best_score = 0

        self.reset()

    def run(self):
        pygame.init()

        self.font = pygame.font.Font(None, 54)
        
        gen = 1
        print("Gen ", gen)
        
        while self.running:
            self.clock.tick(MAX_FPS)
            
            self.screen.fill((0, 0, 0))
            
            self.check_events()

            self.draw()

            self.update()

            if self.should_reset():
                gen += 1
                print("Gen ", gen)
                self.reset()

            pygame.display.flip()

        pygame.quit()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.players[0].jump()

    def draw(self):
        for player in self.players:
            player.draw(self.screen)

        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        self.draw_score()

    def draw_score(self):
        offset = 30
        bestScoreText = self.font.render(f"Best score: {self.best_score}", True, COLORS["white"])
        scoreText = self.font.render(f"Score: {self.score}", True, COLORS["white"])
        self.screen.blit(bestScoreText, (self.screen.get_width() - bestScoreText.get_width() - offset, offset))
        self.screen.blit(scoreText, (self.screen.get_width() - bestScoreText.get_width() - offset, offset * 2 + bestScoreText.get_height()))

    def update(self):
        self.camera.update()
        
        for player in self.players:
            player.update(self.screen, self.first_pipe)
            
            if player.should_jump():
                player.jump()

        if len(self.players) > 0:
            self.score = self.players[0].score

        if self.score > self.best_score:
            self.best_score = self.score

        self.update_internal_pipes()
        self.update_internal_players()
        self.update_internal_clock()

    def update_internal_pipes(self):
        for pipe in self.pipes:
            pipe.update(self.camera)

        if self.first_pipe.is_out():
            self.pipes.pop(0)
            self.first_pipe = self.pipes[0]
            last_pipe = self.pipes[len(self.pipes) - 1]
            self.pipes.append(Pipe(self.screen, self.camera, last_pipe.initial_pos[0] + DISTANCE_BETWEEN_PIPES))

        # if len(self.players) > 0 and self.players[0].passed_pipe(self.first_pipe):
        #     self.first_pipe = self.pipes[1]

        # if self.pipes[0].is_out():
        #     self.pipes.pop(0)
            
        #     last_pipe = self.pipes[len(self.pipes) - 1]
        #     self.pipes.append(Pipe(self.screen, self.camera, last_pipe.initial_pos[0] + DISTANCE_BETWEEN_PIPES))

    def update_internal_players(self):
        for (i, player) in enumerate(self.players):
            if player.is_dead:
                self.genetic.fitness(i, self.camera.pos[0])
                del self.players[i]

    def update_internal_clock(self):
        global current_fps
        global camera_speed
        new_fps = self.clock.get_fps()
        if new_fps != 0:
            current_fps = new_fps
            camera_speed = PIXELS_PER_SECOND / current_fps
    
    def should_reset(self):
        return len(self.players) == 0

    def reset(self):
        self.camera = Camera()
        self.players = self.genetic.next_gen(self.screen)
        self.pipes = [Pipe(self.screen, self.camera, DISTANCE_BETWEEN_PIPES * i) for i in range(1, 10)]
        self.first_pipe = self.pipes[0]
        self.score = 0


class Camera:
    def __init__(self):
        self.pos = (0, 0)

    def update(self):
        self.pos = (self.pos[0] + camera_speed, self.pos[1])


class Pipe:
    def __init__(self, screen: pygame.Surface, camera: Camera, start_x: int):
        height = screen.get_height()

        self.initial_pos = (start_x, random.randint(MIN_GAP + 50 , height - MIN_GAP - 50))
        self.pos = (self.initial_pos[0] - camera.pos[0], self.initial_pos[1])
        self.gap = random.randint(MIN_GAP, MAX_GAP)
        self.width = 100
    
    def is_out(self):
        return self.pos[0] + self.width < 0

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, COLORS["green"], (self.pos[0], 0, self.width, self.initial_pos[1]))
        pygame.draw.rect(screen, COLORS["green"], (self.pos[0], self.initial_pos[1] + self.gap, self.width, screen.get_height() - self.initial_pos[1] - self.gap))

    def update(self, camera: Camera):
        self.pos = (self.initial_pos[0] - camera.pos[0], self.initial_pos[1])


class Player:
    def __init__(self, screen: pygame.Surface, cofactors: 'list[float]'):
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.size = 30
        self.pos = (50, screen.get_height() / 2 - self.size / 2)
        self.acceleration_y = GRAVITY / current_fps
        self.speed_y = self.acceleration_y / current_fps
        self.jump_force = 250
        
        self.score = 0
        self.last_passed_pipe = None
        self.is_dead = False

        # [0] - Left pipe sensor
        # [1] - Top pipe sensor
        # [2] - Bottom right pipe sensor
        self.sensors = []
        self.cofactors = cofactors
        self.fitness = 0
 
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.size, self.size))

    def update(self, screen: pygame.Surface, first_pipe: Pipe):
        self.acceleration_y += GRAVITY / current_fps
        self.speed_y -= self.acceleration_y / current_fps
        self.pos = (self.pos[0], self.pos[1] - self.speed_y)

        self.sensors = self.update_sensors(first_pipe)

        if self.passed_pipe(first_pipe) and first_pipe != self.last_passed_pipe:
            self.last_passed_pipe = first_pipe
            self.score += 1

        if self.should_die(screen, first_pipe):
            self.is_dead = True

    def new_score(self, first_pipe: Pipe):
        self.score += 1
        self.last_passed_pipe = first_pipe

    def should_jump(self):
        return self.sensors[0] * self.cofactors[0] + self.sensors[1] * self.cofactors[1] + self.sensors[2] * self.cofactors[2] > 0

    def update_sensors(self, first_pipe: Pipe) -> 'list[int]':
        sensors = []

        # [0] - Left pipe sensor
        sensors.append(first_pipe.pos[0] - (self.pos[0] + self.size))

        # [1] - Top pipe sensor
        sensors.append(first_pipe.pos[1] - self.pos[1])

        # [2] - Bottom right pipe sensor
        sensors.append((first_pipe.pos[1] + first_pipe.gap) - (self.pos[1] + self.size))

        return sensors

    def passed_pipe(self, pipe: Pipe):
        return self.pos[0] + self.size >= pipe.pos[0]

    def should_die(self, screen: pygame.Surface, first_pipe: Pipe):
        hit_ground = self.pos[1] + self.size > screen.get_height()
        if hit_ground:
            return True

        hit_pipe = self.pos[0] + self.size > first_pipe.pos[0] and (
                   self.pos[0] < first_pipe.pos[0] + first_pipe.width) and (
                        self.pos[1] < first_pipe.pos[1] or 
                        self.pos[1] + self.size > first_pipe.pos[1] + first_pipe.gap)
        if hit_pipe:
            return True

        return False

    def jump(self):
        self.acceleration_y = GRAVITY / current_fps
        self.speed_y = self.jump_force / current_fps
