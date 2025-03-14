#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR
import time
import math
from concurrent.futures import ThreadPoolExecutor


class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and sends
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            msg = self.receiver()
            if msg["game_over"]:
                return



class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()
        self.start_time = None
        self.cache = {}
        self.time_limit = 0.075

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        """
        first_msg = self.receiver()

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Find the best move using Minimax
            best_move = self.search_best_next_move(initial_tree_node=node)

            # Execute the action
            self.sender({"action": best_move, "search_time": None})

    def initialize_model(self, tree_node, depth, alpha, beta, player):
        """
        Minimax algorithm with alpha-beta pruning, transposition table, and move ordering.
        """
        if time.time() - self.start_time > self.time_limit:
            raise TimeoutError

        # State caching
        state_key = str(tree_node.state.get_hook_positions()) + str(tree_node.state.get_fish_positions())
        if state_key in self.cache:
            return self.cache[state_key]

        possible_moves = tree_node.compute_and_get_children()
        if depth == 0 or not possible_moves:
            return self.simple_evaluation(tree_node.state)

        # Order moves to improve pruning
        possible_moves.sort(key=lambda child: self.simple_evaluation(child.state), reverse=(player == "A"))

        # Initialize best value for the current player
        best_value = float("-inf") if player == "A" else float("inf")

        for child in possible_moves:
            if player == "A":
                best_value = max(
                    best_value, self.initialize_model(child, depth - 1, alpha, beta, "B")
                )
                alpha = max(alpha, best_value)
            else:
                best_value = min(
                    best_value, self.initialize_model(child, depth - 1, alpha, beta, "A")
                )
                beta = min(beta, best_value)

            if beta <= alpha:#//
                break  # Prune

        self.cache[state_key] = best_value
        return best_value

    def simple_evaluation(self, state):
        """
        Enhanced heuristic evaluation function for smarter gameplay.
        """
        player_score, opponent_score = state.get_player_scores()
        hook_positions = state.get_hook_positions()
        fish_positions = state.get_fish_positions()
        fish_scores = state.get_fish_scores()
        player = state.get_player()

        # Base score: player's advantage over the opponent
        evaluation = player_score - opponent_score

        # Factor in proximity and score of fish
        for fish_id, fish_pos in fish_positions.items():
            hook_pos = hook_positions[player]
            distance = abs(hook_pos[0] - fish_pos[0]) + abs(hook_pos[1] - fish_pos[1])
            evaluation += fish_scores[fish_id] / (distance + 1)  # Weighted by proximity

        # Penalty for the opponent catching fish
        opponent_hook_pos = hook_positions[1 - player]
        for fish_id, fish_pos in fish_positions.items():
            opponent_distance = abs(opponent_hook_pos[0] - fish_pos[0]) + abs(opponent_hook_pos[1] - fish_pos[1])
            evaluation -= fish_scores[fish_id] / (opponent_distance + 1)

        return evaluation

    def search_best_next_move(self, initial_tree_node):
        """
        Iterative deepening with parallel top-level move evaluation.
        """
        self.start_time = time.time()
        self.cache = {}

        depth = 1
        best_move = "stay"
        best_value = float("-inf")
        moves = initial_tree_node.compute_and_get_children()

        # Evaluate top-level moves in parallel
        with ThreadPoolExecutor() as executor:
            while True:
                try:
                    move_values = {}
                    futures = {
                        executor.submit(
                            self.initialize_model, child, depth, float("-inf"), float("inf"), "A"
                        ): child.move
                        for child in moves
                    }

                    for future in futures:
                        move = futures[future]
                        value = future.result()  # Wait for the result
                        move_values[move] = value

                        if value > best_value:
                            best_value = value
                            best_move = move

                    if depth > 7 or time.time() - self.start_time > self.time_limit:
                        break

                    depth += 1  # Increase depth for the next iteration

                except TimeoutError:
                    break  # Stop deepening if time runs out

        return ACTION_TO_STR[best_move]