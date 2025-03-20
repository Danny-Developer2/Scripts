import subprocess
import sys
from colores import print_info, print_error, print_ok

def ejecutar_comando(cmd, cwd=None):
    print_info(f"Ejecutando: {cmd}")
    try:
        res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if res.returncode != 0:
            print_error(f"Fallo: {cmd}")
            if res.stderr:
                print_error(f"STDERR: {res.stderr.strip()}")
            sys.exit(1)
        print_ok("Comando exitoso")
        return res  # Devuelve resultado completo si necesitas stdout más tarde
    except KeyboardInterrupt:
        print_info("\n[INTERRUPT] Ejecución interrumpida por el usuario.")
        sys.exit(0)
