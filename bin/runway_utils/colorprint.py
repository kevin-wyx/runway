class bcolors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def colorize(text, color):
    return "{}{}{}".format(color, text, bcolors.ENDC)


def debug(text):
    print(colorize(text, bcolors.BLUE))


def error(text):
    print(colorize(text, bcolors.RED))


def info(text):
    print(colorize(text, bcolors.BOLD))


def success(text):
    print(colorize(text, bcolors.GREEN))


def warning(text):
    print(colorize(text, bcolors.YELLOW))
