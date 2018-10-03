from __future__ import print_function
from time import sleep
from time import time
from copy import copy, deepcopy
import os
import sys
import math
sys.path.append('../')
sys.path.append('../pieces')

from random import random, randint
from pieces import ChessPiece
from Board import Board

class GeneticAlgorithm:
    def __init__(self, request, mutation_prob, max_attempt, max_generation, max_population):
        self.__request = request
        self.__MUTATION_PROB = mutation_prob
        self.__MAX_ATTEMPTS = max_attempt
        self.__MAX_GENERATION = max_generation
        self.__MAX_POPULATION = max_population
        self.__SUM_COLORS = len(Board(request).get_colors())
        self.population = []

        self.assign_population(request)

    def assign_population(self, request):
        for _ in range(self.__MAX_POPULATION):
            self.population.append(Board(request))

        self.sort_population()
        self.best_board = Board(request)
        self.best_board.set_pieces(self.get_best_pieces(self.population))

    def get_fitness(self, board):
        return board.calculate_heuristic()['total']

    def sort_population(self):
        self.population.sort(key=self.get_fitness, reverse=True)

    def mutate(self, board):
        piece = board.random_pick()
        new_pos = board.random_move()

        piece.set_x(new_pos['x'])
        piece.set_y(new_pos['y'])

        return board

    def solve_overlap(self, grid):
        overlap = True
        while overlap:
            for val in set(grid):
                if grid.count(val) > 1:
                    new_val = randint(0, 63)
                    grid[grid.index(val)] = new_val

            if len(set(grid)) == len(grid):
                overlap = False
        return grid

    def reproduce(self, parent1, parent2):
        pieces1 = parent1.get_pieces()
        pieces2 = parent2.get_pieces()

        grid1 = []
        grid2 = []
        for i in range(len(parent1.get_pieces())):
            grid1.append(parent1.convert_to_grid(
                pieces1[i].get_x(),
                pieces1[i].get_y()
            ))
            grid2.append(parent2.convert_to_grid(
                pieces2[i].get_x(),
                pieces2[i].get_y()
            ))

        cross_point = randint(0, len(grid1)-1)

        grid_child1 = grid1[0:cross_point+1] + grid2[cross_point+1:len(grid2)]
        grid_child2 = grid2[0:cross_point+1] + grid1[cross_point+1:len(grid1)]
        grid_child1 = self.solve_overlap(grid_child1)
        grid_child2 = self.solve_overlap(grid_child2)

        for i in range(len(pieces1)):
            pieces1[i].set_x(Board.convert_to_axis(grid_child1[i])['x'])
            pieces1[i].set_y(Board.convert_to_axis(grid_child1[i])['y'])

            pieces2[i].set_x(Board.convert_to_axis(grid_child2[i])['x'])
            pieces2[i].set_y(Board.convert_to_axis(grid_child2[i])['y'])

        parent1.set_pieces(pieces1)
        parent2.set_pieces(pieces2)
        return [parent1, parent2]

    def stop_searching(self):
        if len(self.best_board.get_colors()) == 1:
            return self.best_board.calculate_heuristic()['total'] == 0
        else:
            return self.best_board.calculate_heuristic()['total'] == 9999 #update soon

    def get_best_pieces(self, population):
        return deepcopy(population)[0].get_pieces()

    def start(self):

        # start the process
        attempt = 1
        while attempt <= self.__MAX_ATTEMPTS:
            
            # for each attempt do :
            generation = 1
            while generation <= self.__MAX_GENERATION:
                # calculate total pair in a population
                total_pair = len(self.population) if len(self.population)%2 == 0 else len(self.population)-1
                new_population = []

                # generate childs
                for i in [el for el in list(range(total_pair)) if el % 2 == 0]:
                    new_population = new_population + self.reproduce(self.population[i], self.population[i+1])

                # assign population with its childs
                self.population = new_population
                for board in self.population:
                    if random() < self.__MUTATION_PROB:
                        board = self.mutate(board)

                self.sort_population()
                
                # set best board pieces with the best pieces of the child
                # otherwise, do nothing
                if self.best_board.calculate_heuristic()['total'] < self.population[0].calculate_heuristic()['total']:
                    self.best_board.set_pieces(self.get_best_pieces(self.population))
                
                print('Best Heuristic :', self.best_board.calculate_heuristic()['total'])

                if self.stop_searching():
                    break

                generation = generation + 1

            # reassign population
            self.assign_population(self.__request)
            attempt = attempt + 1

            self.best_board.draw()
            print("  ", self.best_board.calculate_heuristic()['a'], ' ', self.best_board.calculate_heuristic()['b'])
            
            if self.stop_searching():
                break
