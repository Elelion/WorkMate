def print_subtitle(text, args=''):
    green_text = "\033[32m" + text + "\033[0m"
    print(green_text, args)


def print_title(text, args=''):
    green_text = "\033[1m" + "\033[33m" + text + "\033[0m"
    print(green_text, args)