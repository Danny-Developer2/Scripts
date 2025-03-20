
import argparse
import os
from pathlib import Path
import sys
from time import time
import subprocess

from colores import print_ok, print_info
from comandos import ejecutar_comando
from estructura import crear_carpetas, crear_archivos
from configuracion import crear_nuevo_appsettings, crear_nuevo_launchsettings, dockerfile
from dependencias import instalar_paquetes

def main():
    inicio = time()

    parser = argparse.ArgumentParser(description="Crea entorno .NET completo con Swagger y lógica básica. & Crear nuevo launchSettings.json para el proyecto.")
    parser.add_argument('--sln', type=str, help='Nombre de la solución')
    parser.add_argument('--api', type=str, help='Nombre del proyecto Web API')
    parser.add_argument('--path', type=str, help='Ruta donde se creará el proyecto', default='.')
    parser.add_argument('--test', action='store_true', help='Crear proyecto de pruebas xUnit')
    parser.add_argument('--run', action='store_true', help='Levantar el servidor al finalizar')
    parser.add_argument("--puerto", type=int, help="Puerto para la aplicación")
    args = parser.parse_args()

    # Recoger los parámetros
    sln = args.sln or input("Nombre de la solución: ")
    api = args.api or input("Nombre del proyecto Web API: ")

    base_path = Path(args.path).resolve()
    os.makedirs(base_path, exist_ok=True)
    print_ok(f"Ruta base: {base_path}")

    # Crear la solución
    ejecutar_comando(f"dotnet new sln -n {sln}", cwd=base_path)
    ejecutar_comando(f"dotnet new webapi -n {api}", cwd=base_path)
    ejecutar_comando(f"dotnet sln {sln}.sln add {api}/{api}.csproj", cwd=base_path)

    # Crear carpetas necesarias
    carpetas = ["Controllers", "Data", "Dto", "Entities", "Error", "Extensions", "Helpers", "Interfaces", "Middleware", "Repositories", "Tests"]
    api_path = base_path / api
    crear_carpetas(api_path, carpetas)

    # Instalar paquetes de NuGet
    instalar_paquetes(api_path)

    # Crear los archivos necesarios (Entity, DTO, Context, Repository, etc.)
    crear_archivos(api_path, api)

    # Crear proyecto de pruebas si se indica
    if args.test:
        test_name = f"{api}.Tests"
        ejecutar_comando(f"dotnet new xunit -n {test_name}", cwd=base_path)
        ejecutar_comando(f"dotnet sln {sln}.sln add {test_name}/{test_name}.csproj", cwd=base_path)
        print_ok(f"Proyecto de pruebas creado: {test_name}")





    # Actualizar archivos de configuración
    crear_nuevo_appsettings(api_path)
    crear_nuevo_launchsettings(api_path,args.puerto) 

    # Crear Dockerfile
    dockerfile(api_path)

    # Construir el path completo a la API
    path_migration = os.path.join(args.path, args.api)

    # Verifica que la ruta exista
    if not os.path.exists(path_migration):
        print_info(f"La ruta {path_migration} no existe. Verifica el path.")
        sys.exit(1)
    else:
        print_ok(f"Ruta encontrada: {path_migration}")
        
        
    ejecutar_comando("dotnet ef migrations add NombreDeLaMigracion", cwd=path_migration)
    ejecutar_comando("dotnet ef database update", cwd=path_migration)
    
    
    # Calcular y mostrar duración
    duracion = round(time() - inicio, 2)
    print_ok(f"\n🎉 Proyecto .NET completo listo en {duracion}s.")
    print_info(f"Swagger: http://localhost:{args.puerto}/index.html")

    # Levantar el servidor si se indica
    if args.run:
        print_info("Levantando servidor...")
        ejecutar_comando("dotnet run --open", cwd=api_path)
        print_ok("Servidor levantado exitosamente")


if __name__ == "__main__":
    main()