import colorama
import datetime

colorama.init()

def warn(message):
    print(f"{colorama.Fore.GREEN}[{datetime.datetime.now()}] [WARN] {message}{colorama.Style.RESET_ALL}")

def error(message):
    colorama.init()
    print(f"{colorama.Fore.RED}[{datetime.datetime.now()}] [ERROR] {message}{colorama.Style.RESET_ALL}")

def output(message):
    colorama.init()
    print(f"{colorama.Fore.BLUE}[{datetime.datetime.now()}] [PRINT] {message}{colorama.Style.RESET_ALL}")
