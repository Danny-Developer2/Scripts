
class Colores:
    OK = '\033[92m'
    INFO = '\033[94m'
    ERROR = '\033[91m'
    FIN = '\033[0m'

def print_ok(msg):
    print(f"{Colores.OK}[OK]{Colores.FIN} {msg}")

def print_info(msg):
    print(f"{Colores.INFO}[INFO]{Colores.FIN} {msg}")

def print_error(msg):
    print(f"{Colores.ERROR}[ERROR]{Colores.FIN} {msg}")
