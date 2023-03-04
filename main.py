class Valley:

    def __init__(self, lines):
        self.width = len(lines[0])
        self.height = len(lines)
        self.lines = lines

    def get_pos(self, x, y) -> str:
        return self.lines[y][x]

    def print_valley(self):
        for y in range(self.height):
            for x in range(self.width):
                print(self.get_pos(x, y), end='')
            print()


with open('Input.txt') as file:
    valley = Valley(file.read().splitlines())

valley.print_valley()
