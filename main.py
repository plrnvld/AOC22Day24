# https://stackoverflow.com/questions/67641986/update-of-elements-priority-in-priorityqueue-is-not-taken-into-account

from __future__ import annotations
from queue import SimpleQueue, PriorityQueue
from dataclasses import dataclass, field
from collections import deque
from typing import Any, List
from math import inf
import datetime

# https://docs.python.org/3/library/queue.html
# https://linuxhint.com/priority-queue-python/

file_name = "Input.txt"

PositionCache = List[List[List[bool]]]


class Vertex:
    def __init__(self, x: int, y: int, m: int):
        self.x = x
        self.y = y
        self.m = m
        self.dist = inf
        self.neighbors = []
        self.prev = None
        self.key = (x, y, m)
        self.processed = False
        self.invalidated = False

    def __lt__(self, other):
        return self.dist < other.dist

    def __repr__(self):
        return f'Vertex({self.x}, {self.y}, {self.m}) dist={self.dist} processed={self.processed}'

    def __eq__(self, other):
        if isinstance(other, Vertex):
            return self.x == other.x and self.y == other.y and self.m == other.m
        return False


class Pos:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Pos):
            return self.x == other.x and self.y == other.y
        return False

    def __str__(self):
        return f"Pos ({self.x},{self.y})"

    def dist(self, target) -> int:
        return abs(self.x - target.x) + abs(self.y - target.y)

    def move_left(self, steps) -> Pos:
        return Pos(self.x - steps, self.y)

    def move_right(self, steps) -> Pos:
        return Pos(self.x + steps, self.y)

    def move_up(self, steps) -> Pos:
        return Pos(self.x, self.y - steps)

    def move_down(self, steps) -> Pos:
        return Pos(self.x, self.y + steps)


class Valley:

    def __init__(self, lines):
        self.width = len(lines[0])
        self.height = len(lines)
        self.start = Pos(1, 0)
        # self.start = Pos(self.width - 2, self.height - 1)
        # self.start_minute = 0
        self.start_minute = 343 + 320
        self.target = Pos(self.width - 2, self.height - 1)
        # self.target = Pos(1, 0)
        self.lines = lines
        self.position_cache = self.cache_positions()
        self.queue = self.create_vertices(self.start, self.target)

    def cache_positions(self) -> PositionCache:
        print("Start caching boards...")
        pos_width = self.width - 2
        pos_height = self.height - 2
        m = 300
        w = pos_width
        h = pos_height
        all_boards = [[[False] * h for _ in range(w)] for _ in range(m)]

        for m in range(m):
            for y in range(h):
                for x in range(w):
                    translated_pos = Pos(x + 1, y + 1)
                    all_boards[m][x][y] = self.get_pos(
                        translated_pos, m) == "."

        print("Finished caching boards")
        return all_boards

    def create_vertices(self, start: Pos, target: Pos) -> PriorityQueue:
        queue = PriorityQueue()

        self.start_vertex = Vertex(start.x, start.y, self.start_minute)
        self.start_vertex.dist = 0

        print("Start creating vertices...")
        dict = {self.start_vertex.key: self.start_vertex}

        for m in range(300):  # Add start vertics for other minutes
            if m != self.start_minute:
                other_start_vertex = Vertex(start.x, start.y, m % 300)
                dict[other_start_vertex.key] = other_start_vertex

        for m in range(300):
            for y in range(self.height - 2):
                for x in range(self.width - 2):
                    new_vertex = Vertex(x + 1, y + 1, m)
                    if self.is_open_upgraded(Pos(x + 1, y + 1), m):
                        dict[new_vertex.key] = new_vertex

        for k in dict.keys():
            queue.put(dict[k])        

        for v in queue.queue:
            next_positions = self.next_positions(Pos(v.x, v.y), v.m)
            for next in next_positions:
                if (next.x == target.x and next.y == target.y):
                    target_key = (target.x, target.y, (v.m + 1) % 300)

                    if target_key in dict.keys():
                        target_vertex = dict[target_key]
                    else:
                        target_vertex = Vertex(
                            target.x, target.y, (v.m + 1) % 300)
                        dict[target_vertex.key] = target_vertex
                        queue.put(target_vertex)

                    v.neighbors.append(target_vertex)
                else:
                    reachable_neighbor = dict[(
                        next.x, next.y, (v.m + 1) % 300)]
                    v.neighbors.append(reachable_neighbor)

        print("Finished creating vertices")
        return queue

    def get_pos_initial(self, pos) -> str:
        return self.lines[pos.y][pos.x]

    def get_pos(self, pos, minutes) -> str:
        left_pos = self.wrap_to_board_pos(pos.move_left(minutes))
        right_pos = self.wrap_to_board_pos(pos.move_right(minutes))
        up_pos = self.wrap_to_board_pos(pos.move_up(minutes))
        down_pos = self.wrap_to_board_pos(pos.move_down(minutes))

        left = self.get_pos_initial(left_pos)
        right = self.get_pos_initial(right_pos)
        up = self.get_pos_initial(up_pos)
        down = self.get_pos_initial(down_pos)

        on_pos = []
        if (left == '>'):
            on_pos.append(left)
        if (right == '<'):
            on_pos.append(right)
        if (up == 'v'):
            on_pos.append(up)
        if (down == '^'):
            on_pos.append(down)
        on_pos_count = len(on_pos)
        if (on_pos_count == 0):
            return '.'
        if (on_pos_count == 1):
            return on_pos[0]

        return str(on_pos_count)

    def is_open_initial(self, pos) -> bool:
        return self.lines[pos.y][pos.x] == '.'

    def is_open_upgraded(self, pos, minutes) -> bool:
        if (pos == self.target or pos == self.start):
            return True

        if (pos.x <= 0 or pos.x >= self.width - 1 or pos.y <= 0
                or pos.y >= self.height - 1):
            return False

        # 300 only works for Input.txt because that when everything repeats itself on a (150, 20) board
        return self.position_cache[minutes % 300][pos.x - 1][pos.y - 1]

    def print_valley(self, minutes):
        for y in range(self.height):
            for x in range(self.width):
                if (x == 0 or x == self.width - 1 or y == 0
                        or y == self.height - 1):
                    print(self.get_pos_initial(Pos(x, y)), end='')
                else:
                    print(self.get_pos(Pos(x, y), minutes), end='')
            print()

    def wrap_to_board_pos(self, pos) -> Pos:
        return Pos((pos.x - 1) % (self.width - 2) + 1,
                   (pos.y - 1) % (self.height - 2) + 1)

    def dist_to_target(self, pos) -> int:
        return pos.dist(self.target)

    def next_positions(self, pos, curr_minute) -> filter[Pos]:
        x = pos.x
        y = pos.y
        next_minute = curr_minute + 1
        all_next = [
            pos,
            Pos(x - 1, y),
            Pos(x + 1, y),
            Pos(x, y - 1),
            Pos(x, y + 1)
        ]
        filtered_next = filter(lambda p: self.is_open_upgraded(p, next_minute),
                               all_next)
        return filtered_next


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any = field(compare=False)


now = datetime.datetime.now()
print(now)

with open(file_name) as file:
    valley = Valley(file.read().splitlines())

vertices = []
for v in valley.queue.queue:
    vertices.append(v)

num_vertices = len(vertices)
while not num_vertices == 0:
    smallest_dist = inf
    best_vertex = vertices[0]

    for v in vertices:
        if v.dist < smallest_dist:
            smallest_dist = v.dist
            best_vertex = v

    if num_vertices % 1000 == 0:
        now = datetime.datetime.now()
        print(f"> {num_vertices} -> {now.time()}")

    vertices.remove(best_vertex)
    num_vertices -= 1

    # u = valley.queue.get()
    u = best_vertex
    u.processed = True

    if u.x == valley.target.x and u.y == valley.target.y and u.dist < 1000:
        print(f"⚡⚡⚡ Answer found, dist={u.dist} ⚡⚡⚡")

    for v in u.neighbors:

        if not v.processed:
            alt = u.dist + 1
            if alt < v.dist:
                v.dist = alt
                v.prev = u

print("End 🏁")

# Answer is 343
# Part 1 implementation: 321k to 311k in 6m 5s.

# Part 2:
# * There 343
# * Back again 320
# * There again ? (starts at 663) 297

# Answer = 343 + 320 + 297 = 960


############### Maybe invalidate existing items in the queue for more performance?