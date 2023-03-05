from __future__ import annotations
from queue import SimpleQueue, PriorityQueue
from dataclasses import dataclass, field
from collections import deque
from typing import Any
from math import inf

# https://docs.python.org/3/library/queue.html
# https://linuxhint.com/priority-queue-python/

file_name = "Input.txt"


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

    def next_positions(self, pos, curr_minute) -> list[Pos]:
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
        all_next.sort(key=lambda p: self.dist_to_target(p))
        filtered_next = filter(lambda p: self.is_open(p, next_minute),
                               all_next)
        return filtered_next


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any = field(compare=False)
    hist: Any = field(compare=False)


with open(file_name) as file:
    valley = Valley(file.read().splitlines())

prio_queue = PriorityQueue()
# positions = SimpleQueue()
items_deque = deque()
best_positions = []
end_game_stack = []


def create_prio_item(pos: Pos, minute: int, prev: PrioritizedItem) -> PrioritizedItem:
    if (prev is None):
        hist_list = [pos]
    else:
        hist_list = prev.hist
        hist_list.insert(0, pos)
        if (len(hist_list) > 100):
            hist_list.pop()
    return PrioritizedItem(priority=valley.dist_to_target(pos), item=(pos, minute), hist=hist_list)


def add_to_normal_queue(pos: Pos, minute: int, prev: PrioritizedItem):
    prio_queue.put(create_prio_item(pos, minute, prev))


def add_to_end_game_queue(pos: Pos, minute: int, prev: PrioritizedItem):
    end_game_stack.append(create_prio_item(pos, minute, prev))


add_to_normal_queue(valley.start, 0, None)

best_minutes = inf  # 450 is too high says AOC, so why not make use of it?
best_dist = inf

first_answer_found = False

rejected = 0
dedupped = 0
counter = 1
while not prio_queue.empty() or len(best_positions) > 0 or len(end_game_stack) > 0:
    if len(best_positions) > 0:
        prio_item = best_positions.pop(0)
    elif first_answer_found:
        prio_item = end_game_stack.pop()
    else:
        prio_item = prio_queue.get()

    (p, m) = prio_item.item
    dist = prio_item.priority
    hist = prio_item.hist

    if (p == valley.target and m < best_minutes):
        best_minutes = m

        print(f"🎉 answer found 🎉 => {best_minutes}")

        if (not first_answer_found):
            print("🔥🔥🔥 END GAME STARTS 🔥🔥🔥")
            new_queue = SimpleQueue()
            while not prio_queue.empty():
                end_game_stack.append(prio_queue.get())

            first_answer_found = True

    if (counter % 1000000 == 0):
        millis = counter / 1000000
        num_items = len(end_game_stack)
        rejected_m = rejected / 1000000
        print(f"[{millis}M] current best = {best_minutes}, best dist = {best_dist}, #items {num_items}, rejected={rejected_m}M, dedupped={dedupped}")

    for next in valley.next_positions(p, m):
        counter += 1
        latest_pos = hist[0]
        latest_count = hist.count(next)
        if latest_count > 40 and latest_pos.y > 0:
            to_stringed = map(lambda p: "(" + str(p.x) + ", " + str(p.y) + ")", hist)
            hist_text = ','.join(to_stringed)
            print(f"Dedupping, dedupped={latest_count}, latest pos={latest_pos}, hist={hist_text}!")
            dedupped += 1
        elif m + valley.dist_to_target(p) < best_minutes:
            if first_answer_found:
                add_to_end_game_queue(next, m+1, prio_item)
            else:
                add_to_normal_queue(next, m + 1, prio_item)
        else:
            rejected += 1

# 170 too low
# 494 too high
# 450 too high
