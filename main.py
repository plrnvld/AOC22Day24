from queue import PriorityQueue
# https://docs.python.org/3/library/queue.html


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


class Valley:

    def __init__(self, lines):
        self.width = len(lines[0])
        self.height = len(lines)
        self.start = Pos(1, 0)
        self.target = Pos(self.width - 2, self.height - 1)
        self.lines = lines

    def get_pos(self, pos) -> str:
        return self.lines[pos.y][pos.x]

    def get_pos(self, pos, minute) -> str:
        left_on_pos

    def is_open(self, pos) -> bool:
        return self.lines[pos.y][pos.x] == '.'

    def print_valley(self):
        for y in range(self.height):
            for x in range(self.width):
                print(self.get_pos(Pos(x, y)), end='')
            print()

    def wrap_to_board_pos(self, pos) -> Pos:
        return Pos((pos.x - 1) % (self.width - 2) + 1,
                   (pos.y - 1) % (self.height - 2) + 1)


with open('Example.txt') as file:
    valley = Valley(file.read().splitlines())

valley.print_valley()


def test_is_open(x, y):
    pos = Pos(x, y)
    open = valley.is_open(pos)
    print(f"Pos {pos} is open={open}")


test_is_open(3, 1)
test_is_open(2, 1)
test_is_open(4, 1)
test_is_open(1, 2)
