import random
import game
import pygame

class Genetic:
    POPULATION_SIZE = 100
    MUTATION_FACTOR = 0.05
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
            # [0] - Left pipe sensor
            # [1] - Top pipe sensor
            # [2] - Bottom right pipe sensor
            cofactors = [
                random.random() * random.randint(-100, 100),
                random.random() * random.randint(-100, 100),
                random.random() * random.randint(-100, 100)]
            players.append(game.Player(screen, cofactors))
        return players

    def crossover(self, screen: pygame.Surface) -> 'list[game.Player]':
        next_gen_players = []
        
        best_players = self.players.copy()
        best_players.sort(key=lambda x: x.fitness)
        
        for player_1, player_2 in zip(best_players, best_players[::-1]):
            cofactors_1 = [
                player_1.cofactors[0],
                player_2.cofactors[1],
                player_2.cofactors[2]]
            next_gen_players.append(game.Player(screen, cofactors_1))
            
            cofactors_2 = [
                player_2.cofactors[0],
                player_1.cofactors[1],
                player_1.cofactors[2]]
            next_gen_players.append(game.Player(screen, cofactors_2))

            if len(next_gen_players) >= Genetic.POPULATION_SIZE:
                break
        
        return next_gen_players
        
    def mutate(self, crossed_gen: 'list[game.Player]'):
        for player in crossed_gen:
            for i in range(0, len(player.cofactors)):
                dice = random.random() * 100
                if dice < Genetic.MUTATION_FACTOR:
                    player.cofactors[i] += random.random() * random.randint(-20, 20)

    def fitness(self, player_index: int, camera_x: int):
        if player_index < 0 or player_index >= len(self.players):
            return

        player = self.players[player_index]
        player.fitness = (camera_x * Genetic.DISTANCE_FACTOR) + (player.score * Genetic.SCORE_FACTOR)
