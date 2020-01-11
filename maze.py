import numpy as np
import string
import heapq
from itertools import combinations

all_keys = set(string.ascii_lowercase)
all_doors = set([key.upper() for key in all_keys])


class Maze:

    def __init__(self, file_path):

        self.array = self.load_data(file_path)
        self.map = np.asarray(self.array)
        print(f'map = {self.map}')
        self.maze_keys = self.get_maze_keys()
        self.closed_doors = set([key.upper() for key in self.maze_keys])
        self.closed_doors.add('#')
        self.key_positions = {key: np.argwhere(self.map == key)[0] for key in self.maze_keys}
        self.key_positions.update({'@': np.argwhere(self.map == '@')[0]})
        print(f'key positions = {self.key_positions}')
        self.shortest_paths_dic = self.get_initial_shortest_paths()

    def load_data(self, file_path):
        array = []
        with open(file_path, 'r') as data:
            line = data.readline()
            self.x_max = len(line) - 2
            y = 0
            while line:
                chars = list(line)
                array.append(chars[:self.x_max+1])
                x = line.find('@')
                if x != -1:
                    self.x0 = x
                    self.y0 = y
                line = data.readline()
                y += 1
            self.y_max = y - 1
        return array

    def get_neighbours(self, position, collected_keys=[]):
        neighbours_list = []
        i, j = position
        for coordinates in [(i, j+1), (i, j-1), (i-1, j), (i+1, j)]:
            char = self.map[coordinates]
            opened_doors = set([key.upper() for key in collected_keys])
            closed_doors = self.closed_doors.difference(opened_doors)
            if char not in closed_doors:
                neighbours_list.append(coordinates)
        return neighbours_list

    def fill(self, position):
        # check if position matches a dead-end
        char = self.map[position]
        if (char != '.') and not (char in all_doors):
            return 0
        # print(f'position = {position}')
        # print(f'value = {self.map[position]}')
        neighbours = self.get_neighbours(position, collected_keys=all_keys)
        if len(neighbours) != 1:
            return 0
        # print(f'filling position = {position}')
        self.map[position] = '#'
        return 1

    def simplify(self):
        count = 0
        for y in range(self.y_max):
            for x in range(self.x_max):
                position = (y, x)
                count += self.fill(position)
        return count

    def get_initial_shortest_paths(self):
        shortest_path_dic = {}
        key_list = sorted(list(self.maze_keys))
        print(f'key list = {key_list}')
        key_count = len(key_list)
        for source_index in range(key_count):
            for target_index in range(source_index+1, key_count):
                source_key = key_list[source_index]
                target_key = key_list[target_index]
                route = (source_key, target_key)
                distance = self.shortest_path(source_key, target_key)
                distances_dic = {('@'): distance}
                shortest_path_dic.update({route: distances_dic})
        return shortest_path_dic

    def get_maze_keys(self):
        all_keys = set(string.ascii_lowercase)
        chars = set(self.map.ravel())
        maze_keys = all_keys.intersection(chars)
        return maze_keys

    # bi-directional breadth-first search
    def shortest_path(self, source, target, collected_keys=set()):
        try:
            start = tuple(self.key_positions[source])
            end = tuple(self.key_positions[target])
        except IndexError:
            return -2
        forward_queue = [start]
        backward_queue = []
        forward_queue.append(start)
        backward_queue.append(end)
        forward_marked = [start]
        backward_marked = [end]
        forward_distances_dic = {start: 0}
        backward_distances_dic = {end: 0}

        while (len(forward_queue) > 0 and len(backward_queue) > 0):
            forward_position = forward_queue.pop()
            backward_position = backward_queue.pop()
            forward_distance = forward_distances_dic[forward_position]
            backward_distance = backward_distances_dic[backward_position]
            if forward_position in backward_marked:
                return forward_distance + backward_distances_dic[forward_position]
            if backward_position in forward_marked:
                return backward_distance + forward_distances_dic[backward_position]
            for neighbour_position in self.get_neighbours(forward_position, collected_keys):
                if not neighbour_position in forward_marked:
                    forward_marked.append(neighbour_position)
                    forward_queue.append(neighbour_position)
                    forward_distances_dic.update(
                        {neighbour_position: forward_distance + 1})
            for neighbour_position in self.get_neighbours(backward_position, collected_keys):
                if not neighbour_position in backward_marked:
                    backward_marked.append(neighbour_position)
                    backward_queue.append(neighbour_position)
                    backward_distances_dic.update(
                        {neighbour_position: backward_distance + 1})
        return -1

    def run(self, source):

        keys_set = self.maze_keys
        keys_count = len(keys_set)
        queue = []
        visited = set()
        state = tuple('@')
        distances_dic = {state: 0}
        heapq.heappush(queue, (0, state))
        # shortest_path_dic = self.shortest_paths_dic

        while len(queue) > 0:
            distance, state = heapq.heappop(queue)
            # print(f'current state = {state}')
            if state in visited:
                continue
            visited.add(state)
            remaining_keys = set(keys_set).difference(set(state))
            state_distance = distances_dic[state]
            print(f'distance = {state_distance}')

            if len(state) == keys_count + 1:
                print(
                    f'distance {state_distance} reached with key sequence = {state}')
                return state_distance

            last_key = state[len(state)-1]
            # print(f'remaining_keys = {remaining_keys}')
            for new_key in remaining_keys:
                new_key_distance = self.shortest_path(
                    last_key, new_key, collected_keys=set(state))
                # print(f'shortest path for {(last_key, new_key)} = {new_key_distance}')
                # print(f'new key = {new_key}, distance = {new_key_distance}')
                if new_key_distance < 0:
                    continue
                new_state = tuple(list(state) + [new_key])
                distance = new_key_distance + state_distance
                # print(f'distance = {distance}')
                if (not new_state in distances_dic) or distance < distances_dic[new_state]:
                    distances_dic[new_state] = distance
                    heapq.heappush(queue, (distance, new_state))
