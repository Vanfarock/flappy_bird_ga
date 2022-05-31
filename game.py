from typing import List
import pygame
import random

COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
}
GRAVITY = 80
MAX_FPS = 60
GAP_BETWEEN_PIPES = 600
PIXELS_PER_SECOND = 200

current_fps = MAX_FPS
camera_speed = PIXELS_PER_SECOND / current_fps

class Game:
    def __init__(self, width: int, height: int):    
        self.width = width
        self.height = height
        self.running = True
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        
        self.reset()

    def run(self):
        pygame.init()

        while self.running:
            self.screen.fill((0, 0, 0))
            
            self.check_events()

            self.draw()

            self.update()

            pygame.display.flip()

            self.clock.tick(MAX_FPS)
            
            global current_fps
            global camera_speed
            new_fps = self.clock.get_fps()
            if new_fps != 0:
                current_fps = new_fps
                camera_speed = PIXELS_PER_SECOND / current_fps

        pygame.quit()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.player.jump()

    def draw(self):
        self.player.draw(self.screen)

        for pipe in self.pipes:
            pipe.draw(self.screen)

    def update(self):
        self.camera.update()
        self.player.update(self.screen, self.first_pipe)
        
        self.update_internal_pipes()
        self.update_internal_players()

    def update_internal_pipes(self):
        for pipe in self.pipes:
            pipe.update(self.camera)

        if self.first_pipe.is_out():
            self.pipes.pop(0)
            self.first_pipe = self.pipes[0]
            
            last_pipe = self.pipes[len(self.pipes) - 1]
            self.pipes.append(Pipe(self.screen, self.camera, last_pipe.pos[0] + GAP_BETWEEN_PIPES))

    def update_internal_players(self):
        if self.player.is_dead:
            self.reset()
    
    def reset(self):
        self.camera = Camera()
        self.player = Player(self.screen)
        self.pipes: List[Pipe] = [Pipe(self.screen, self.camera, GAP_BETWEEN_PIPES * i) for i in range(1, 3)]
        self.first_pipe = self.pipes[0]


class Camera:
    def __init__(self):
        self.pos = (0, 0)

    def update(self):
        self.pos = (self.pos[0] + camera_speed, self.pos[1])


class Pipe:
    def __init__(self, screen: pygame.Surface, camera: Camera, start_x: int):
        height = screen.get_height()

        self.pos = (start_x, random.randint(int((height * 3) / 6), int((height * 4) / 6)))
        self.actual_pos = (self.pos[0] - camera.pos[0], self.pos[1])
        self.gap = random.randint(int(height  / 4.5), int(height / 3))
        self.width = 100
    
    def is_out(self):
        return self.actual_pos[0] + self.width < 0

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, COLORS["green"], (self.actual_pos[0], 0, self.width, self.pos[1]))
        pygame.draw.rect(screen, COLORS["green"], (self.actual_pos[0], self.pos[1] + self.gap, self.width, screen.get_height() - self.pos[1] - self.gap))

    def update(self, camera: Camera):
        self.actual_pos = (self.pos[0] - camera.pos[0], self.pos[1])


class Player:
    def __init__(self, screen: pygame.Surface):
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.size = 30;
        self.pos = (100, screen.get_height() / 2 - self.size / 2)
        self.acceleration_y = GRAVITY / current_fps
        self.speed_y = self.acceleration_y / current_fps
        self.jump_force = 200;
        
        self.score = 0
        self.last_passed_pipe = None
        self.is_dead = False

        self.sensors = []
 
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.size, self.size))

    def update(self, screen: pygame.Surface, first_pipe: Pipe):
        self.acceleration_y += GRAVITY / current_fps
        self.speed_y -= self.acceleration_y / current_fps
        self.pos = (self.pos[0], self.pos[1] - self.speed_y)

        if self.passed_pipe(first_pipe) and first_pipe != self.last_passed_pipe:
            self.last_passed_pipe = first_pipe
            self.score += 1

        if self.should_die(screen, first_pipe):
            self.is_dead = True

    def passed_pipe(self, pipe: Pipe):
        return self.pos[0] >= pipe.actual_pos[0] + pipe.width

    def should_die(self, screen: pygame.Surface, first_pipe: Pipe):
        hit_ground = self.pos[1] + self.size > screen.get_height()
        if hit_ground:
            return True

        hit_pipe = self.pos[0] + self.size > first_pipe.actual_pos[0] and (
                   self.pos[0] < first_pipe.actual_pos[0] + first_pipe.width) and (
                        self.pos[1] < first_pipe.actual_pos[1] or 
                        self.pos[1] + self.size > first_pipe.actual_pos[1] + first_pipe.gap)
        if hit_pipe:
            return True

        return False

    def jump(self):
        self.acceleration_y = GRAVITY / current_fps
        self.speed_y = self.jump_force / current_fps
