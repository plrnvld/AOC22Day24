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
        self.target = Pos(self.width - 2, self.height - 1)
        self.lines = lines
        self.position_cache = self.cache_positions()

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
                    all_boards[m][x][y] = self.get_pos(translated_pos,
                                                       m) == "."

        print("Finished caching boards")
        return all_boards

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

    def is_open(self, pos, minutes) -> bool:
        if (pos == valley.target or pos == valley.start):
            return True

        if (pos.x <= 0 or pos.x >= self.width - 1 or pos.y <= 0
                or pos.y >= self.height - 1):
            return False

        left_pos = self.wrap_to_board_pos(pos.move_left(minutes))
        right_pos = self.wrap_to_board_pos(pos.move_right(minutes))
        up_pos = self.wrap_to_board_pos(pos.move_up(minutes))
        down_pos = self.wrap_to_board_pos(pos.move_down(minutes))

        left = self.get_pos_initial(left_pos)
        right = self.get_pos_initial(right_pos)
        up = self.get_pos_initial(up_pos)
        down = self.get_pos_initial(down_pos)

        return left != '>' and right != '<' and up != 'v' and down != '^'

    def is_open_upgraded(self, pos, minutes) -> bool:
        if (pos == valley.target or pos == valley.start):
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

prio_queue = PriorityQueue()
items_deque = deque()

rejected = 0
counter = 1


def create_prio_item(pos: Pos, minute: int,
                     prev: PrioritizedItem | None) -> PrioritizedItem:
    return PrioritizedItem(priority=valley.dist_to_target(pos),
                           item=(pos, minute))


def create_prio_item_end_game(pos: Pos, minute: int,
                              prev: PrioritizedItem | None) -> PrioritizedItem:
    return PrioritizedItem(priority=2 * valley.dist_to_target(pos) + minute,
                           item=(pos, minute))


def add_to_normal_queue(pos: Pos, minute: int, prev: PrioritizedItem | None):
    prio_queue.put(create_prio_item(pos, minute, prev))


def add_to_end_game_queue(pos: Pos, minute: int, prev: PrioritizedItem):
    prio_queue.put(create_prio_item_end_game(pos, minute, prev))


add_to_normal_queue(valley.start, 0, None)

best_minutes = inf  # 450 is too high says AOC, so why not make use of it?

first_answer_found = False

while not prio_queue.empty():
    if first_answer_found:
        prio_item = prio_queue.get()
    else:
        prio_item = prio_queue.get()

    (p, m) = prio_item.item
    dist = prio_item.priority

    if (p == valley.target and m < best_minutes):
        best_minutes = m

        print(f"🎉 answer found 🎉 => {best_minutes}")

        if (not first_answer_found):
            print("🔥🔥🔥 END GAME STARTS 🔥🔥🔥")
            first_answer_found = True

    if (counter % 1000000 == 0):
        millis = counter / 1000000
        num_items = prio_queue.qsize()
        num_items_m = num_items / 1000000
        rejected_m = rejected / 1000000
        print(
            f"[{millis}M] current best = {best_minutes}, #items={num_items_m}M, rejected={rejected_m}M"
        )

    for next in valley.next_positions(p, m):
        counter += 1
        if m + valley.dist_to_target(p) < best_minutes:
            if first_answer_found:
                add_to_end_game_queue(next, m + 1, prio_item)
            else:
                add_to_normal_queue(next, m + 1, prio_item)
        else:
            rejected += 1

# 170 too low
# 494 too high
# 450 too high
