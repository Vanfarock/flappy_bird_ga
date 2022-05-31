import random
import game
import pygame

class Genetic:
    POPULATION_SIZE = 100
    MUTATION_FACTOR = 0.005
    DISTANCE_FACTOR = 1
    SCORE_FACTOR = 10

    def __init__(self):
        self.players: list[game.Player] = []

    def next_gen(self, screen: pygame.Surface) -> 'list[game.Player]':
        if len(self.players) == 0:
            self.players = self.first_gen(screen)
            return self.players.copy()

        crossed_gen = self.crossover(screen)
        self.mutate(crossed_gen)

        self.players = crossed_gen
        
        return self.players.copy()

    def first_gen(self, screen: pygame.Surface) -> 'list[game.Player]':
        players = []
        for _ in range(Genetic.POPULATION_SIZE):
            # [0] - Ground sensor
            # [1] - Left pipe sensor
            # [2] - Right pipe sensor
            # [3] - Top pipe sensor
            # [4] - Bottom right pipe sensor
            parameters = [
                random.randint(0, screen.get_height()),
                random.randint(0, screen.get_width()),
                random.randint(0, screen.get_width()),
                random.randint(0, screen.get_height()),
                random.randint(0, screen.get_height())]
            players.append(game.Player(screen, parameters))
        return players

    def crossover(self, screen: pygame.Surface) -> 'list[game.Player]':
        next_gen_players = []
        
        best_players = self.players.copy()
        best_players.sort(key=lambda x: x.fitness)
        
        for player_1, player_2 in zip(best_players[::2], best_players[1::2]):
            parameters_1 = [
                player_1.parameters[0],
                player_2.parameters[1],
                player_2.parameters[2],
                player_1.parameters[3],
                player_1.parameters[4]]
            next_gen_players.append(game.Player(screen, parameters_1))
            
            parameters_2 = [
                player_2.parameters[0],
                player_1.parameters[1],
                player_1.parameters[2],
                player_2.parameters[3],
                player_2.parameters[4]]
            next_gen_players.append(game.Player(screen, parameters_2))

            if len(next_gen_players) >= Genetic.POPULATION_SIZE:
                break
        
        return next_gen_players
        
    def mutate(self, crossed_gen: 'list[game.Player]'):
        for player in crossed_gen:
            for i in range(0, len(player.parameters)):
                dice = random.random() * 100
                if dice < Genetic.MUTATION_FACTOR:
                    player.parameters[i] += random.randint(-50, 50)

    def fitness(self, player_index: int, camera_x: int):
        if player_index < 0 or player_index >= len(self.players):
            return

        player = self.players[player_index]
        player.fitness = (camera_x * Genetic.DISTANCE_FACTOR) + (player.score * Genetic.SCORE_FACTOR)
