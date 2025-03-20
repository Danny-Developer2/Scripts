from comandos import ejecutar_comando
from colores import print_info, print_ok

def instalar_paquetes(api_path):
    print_info("Instalando dependencias necesarias...")
    ejecutar_comando("dotnet add package Microsoft.EntityFrameworkCore --version 7.0.0", cwd=api_path)
    ejecutar_comando("dotnet add package Microsoft.EntityFrameworkCore.InMemory --version 7.0.0", cwd=api_path)
    ejecutar_comando("dotnet add package Swashbuckle.AspNetCore --version 6.0.0", cwd=api_path)
    ejecutar_comando("dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer", cwd=api_path)
    ejecutar_comando("dotnet add package Microsoft.EntityFrameworkCore.Sqlite --version 7.0.0", cwd=api_path)
    ejecutar_comando("dotnet add package Microsoft.EntityFrameworkCore.Design --version 7.0.0", cwd=api_path)
    ejecutar_comando("dotnet add package Swashbuckle.AspNetCore --version 7.0.0",cwd=api_path)
    print_ok("Dependencias instaladas correctamente")

