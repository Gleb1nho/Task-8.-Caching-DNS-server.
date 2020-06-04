from os import get_terminal_size


class LineDrawer:
    width, height = get_terminal_size(0)

    def draw_horisontal_line(self):
        return '~' * self.width


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
