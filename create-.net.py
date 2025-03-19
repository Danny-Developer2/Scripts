import os
import subprocess
import sys
from pathlib import Path
import argparse
from time import time

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

def ejecutar_comando(cmd, cwd=None):
    print_info(f"Ejecutando: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if res.returncode != 0:
        print_error(f"Fallo: {cmd}")
        sys.exit(1)
    print_ok("Comando exitoso")

def crear_carpetas(base_path, carpetas):
    for carpeta in carpetas:
        ruta = base_path / carpeta
        ruta.mkdir(parents=True, exist_ok=True)
        (ruta / ".gitkeep").touch()
        print_ok(f"Carpeta + .gitkeep: {ruta}")

def crear_archivos(api_path, project_name):
    # Entity
    entity_code = f"""
namespace {project_name}.Entities
{{
    public class Producto
    {{
        public int Id {{ get; set; }}
        public string Nombre {{ get; set; }} = string.Empty;
        public decimal Precio {{ get; set; }}
    }}
}}
""".strip()

    # DTO
    dto_code = f"""
namespace {project_name}.Dto
{{
    public class ProductoDto
    {{
        public string Nombre {{ get; set; }} = string.Empty;
        public decimal Precio {{ get; set; }}
    }}
}}
""".strip()

    # DbContext
    context_code = f"""
using Microsoft.EntityFrameworkCore;
using {project_name}.Entities;

namespace {project_name}.Data
{{
    public class AppDbContext : DbContext
    {{
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) {{ }}
        public DbSet<Producto> Productos {{ get; set; }}
    }}
}}
""".strip()

    # Repository Interface
    interface_code = f"""
using {project_name}.Entities;

namespace {project_name}.Interfaces
{{
    public interface IProductoRepository
    {{
        Task<IEnumerable<Producto>> ObtenerTodosAsync();
    }}
}}
""".strip()

    # Repository Implementation
    repository_code = f"""
using {project_name}.Data;
using {project_name}.Entities;
using {project_name}.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace {project_name}.Repositories
{{
    public class ProductoRepository : IProductoRepository
    {{
        private readonly AppDbContext _context;

        public ProductoRepository(AppDbContext context)
        {{
            _context = context;
        }}

        public async Task<IEnumerable<Producto>> ObtenerTodosAsync()
        {{
            return await _context.Productos.ToListAsync();
        }}
    }}
}}
""".strip()

    # Helper básico
    helper_code = f"""
namespace {project_name}.Helpers
{{
    public static class FormatoHelper
    {{
        public static string FormatearMoneda(decimal valor)
        {{
            return $"${{valor:N2}}";
        }}
    }}
}}
""".strip()

    # Controller
    controller_code = f"""
using Microsoft.AspNetCore.Mvc;
using {project_name}.Entities;
using {project_name}.Interfaces;

namespace {project_name}.Controllers
{{
    [ApiController]
    [Route("api/[controller]")]
    public class ProductosController : ControllerBase
    {{
        private readonly IProductoRepository _repo;

        public ProductosController(IProductoRepository repo)
        {{
            _repo = repo;
        }}

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Producto>>> GetProductos()
        {{
            var productos = await _repo.ObtenerTodosAsync();
            return Ok(productos);
        }}
    }}
}}
""".strip()

    # Modificar Program.cs
    program_path = api_path / "Program.cs"
    program_text = program_path.read_text()

    # Agregar las directivas using necesarias si no están presentes
    if "using Microsoft.EntityFrameworkCore;" not in program_text:
        program_text = "using Microsoft.EntityFrameworkCore;\n" + program_text
    if f"using {project_name}.Data;" not in program_text:
        program_text = f"using {project_name}.Data;\n" + program_text
    if f"using {project_name}.Interfaces;" not in program_text:
        program_text = f"using {project_name}.Interfaces;\nusing {project_name}.Repositories;\n" + program_text

    # AddDbContext y Repository
    if "AddDbContext" not in program_text:
        db_context_config = f"""
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseInMemoryDatabase("MiBaseDatos"));
builder.Services.AddScoped<IProductoRepository, ProductoRepository>();
""".strip()
        program_text = program_text.replace("var app = builder.Build();", db_context_config + "\n\nvar app = builder.Build();")
        print_ok("Program.cs: InMemory DB y Repository registrados")

    # Swagger servicios
    if "AddSwaggerGen" not in program_text:
        swagger_services = """
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
""".strip()
        program_text = program_text.replace("var app = builder.Build();", swagger_services + "\n\nvar app = builder.Build();")
        print_ok("Program.cs: Swagger servicios agregados")

    # Swagger middleware
    if "app.UseSwagger()" not in program_text:
        swagger_pipeline = """
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
""".strip()
        program_text = program_text.replace("app.UseHttpsRedirection();", swagger_pipeline + "\n\napp.UseHttpsRedirection();")
        print_ok("Program.cs: Middleware Swagger agregado")

    program_path.write_text(program_text)
    print_ok("Program.cs actualizado")

    # Guardar archivos
    (api_path / "Entities" / "Producto.cs").write_text(entity_code)
    (api_path / "Dto" / "ProductoDto.cs").write_text(dto_code)
    (api_path / "Data" / "AppDbContext.cs").write_text(context_code)
    (api_path / "Interfaces" / "IProductoRepository.cs").write_text(interface_code)
    (api_path / "Repositories").mkdir(exist_ok=True)
    (api_path / "Repositories" / "ProductoRepository.cs").write_text(repository_code)
    (api_path / "Helpers" / "FormatoHelper.cs").write_text(helper_code)
    (api_path / "Controllers" / "ProductosController.cs").write_text(controller_code)
    print_ok("Entity, DTO, Context, Repository, Helper, Controller creados")



def crear_nuevo_launchsettings(api_path, puerto):
    # Detectar el nombre del proyecto a partir del archivo .csproj
    csproj_files = list(api_path.glob("*.csproj"))
    if not csproj_files:
        print("No se encontró el archivo .csproj.")
        return
    
    # Suponemos que solo hay un archivo .csproj
    project_name = csproj_files[0].stem  # Extrae el nombre del archivo sin la extensión .csproj

    # Definir la ruta del archivo launchSettings.json
    launchsettings_path = api_path / "Properties" / "launchSettings.json"

    # Eliminar el archivo launchSettings.json si ya existe
    if launchsettings_path.exists():
        launchsettings_path.unlink()
        print("Archivo launchSettings.json eliminado.")

    # Crear el nuevo archivo launchSettings.json con la configuración
    launchsettings_text = f"""
    {{
      "$schema": "https://json.schemastore.org/launchsettings.json",
      "profiles": {{
        "http": {{
          "commandName": "Project",
          "dotnetRunMessages": true,
          "launchBrowser": false,
          "applicationUrl": "http://localhost:{puerto}",
          "environmentVariables": {{
            "ASPNETCORE_ENVIRONMENT": "Development"
          }}
        }},
        "https": {{
          "commandName": "Project",
          "dotnetRunMessages": true,
          "launchBrowser": false,
          "applicationUrl": "https://localhost:{puerto};http://localhost:{puerto + 1000}",
          "environmentVariables": {{
            "ASPNETCORE_ENVIRONMENT": "Development"
          }}
        }}
      }}
    }}
    """

    # Crear el directorio "Properties" si no existe
    properties_path = api_path / "Properties"
    properties_path.mkdir(parents=True, exist_ok=True)

    # Escribir el nuevo archivo launchSettings.json
    launchsettings_path.write_text(launchsettings_text)
    print("Nuevo archivo launchSettings.json creado con la configuración adecuada.")


def crear_nuevo_appsettings(api_path):
    # Definir la ruta del archivo appsettings.json
    appsettings_path = api_path / "appsettings.json"

    # Eliminar el archivo appsettings.json si ya existe
    if appsettings_path.exists():
        appsettings_path.unlink()
        print("Archivo appsettings.json eliminado.")

    # Crear el nuevo archivo appsettings.json con la configuración
    appsettings_text = """
    {
      "Logging": {
        "LogLevel": {
          "Default": "Information",
          "Microsoft.AspNetCore": "Warning"
        }
      },
      "AllowedHosts": "*",
      "ConnectionStrings": {
        "DefaultConnection": "Data source=dating.db"
      },
      "JwtSettings": {
        "SecretKey": "mi_clave_secreta_de_32_caracteres_12345", 
        "Issuer": "TuAPI",
        "Audience": "TuCliente"
      }
    }
    """
    
    # Escribir el nuevo archivo appsettings.json
    appsettings_path.write_text(appsettings_text)
    print("Nuevo archivo appsettings.json creado con la configuración adecuada.")

def dockerfile(api_path):
    # Detectar el nombre del proyecto a partir del archivo .csproj
    csproj_files = list(api_path.glob("*.csproj"))
    if not csproj_files:
        print("No se encontró el archivo .csproj.")
        return
    
    # Suponemos que solo hay un archivo .csproj
    project_name = csproj_files[0].stem  # Extrae el nombre del archivo sin la extensión .csproj
    
    # Contenido del Dockerfile con el nombre del proyecto dinámico
    dockerfile_content = f"""
# Etapa 1: Construcción de la aplicación
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 7500

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["{project_name}/{project_name}.csproj", "{project_name}/"]
RUN dotnet restore "{project_name}/{project_name}.csproj"
COPY . .
WORKDIR "/src/{project_name}"
RUN dotnet build "{project_name}.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "{project_name}.csproj" -c Release -o /app/publish

# Etapa 2: Construcción del contenedor final
FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Copiar el archivo appsettings.json
COPY {project_name}/appsettings.json /app/
COPY {project_name}/dating.db /app/

# Configurar variables de entorno
ENV ASPNETCORE_ENVIRONMENT=Production

ENTRYPOINT ["dotnet", "{project_name}.dll"]
"""
    
    # Crear y escribir el Dockerfile
    dockerfile_path = api_path / "Dockerfile"
    dockerfile_path.write_text(dockerfile_content)
    print("Dockerfile actualizado con el nombre del proyecto:", project_name)


def instalar_paquetes(api_path):
    print_info("Instalando dependencias necesarias...")
    ejecutar_comando("dotnet add package Microsoft.EntityFrameworkCore --version 7.0.0", cwd=api_path)
    ejecutar_comando("dotnet add package Microsoft.EntityFrameworkCore.InMemory --version 7.0.0", cwd=api_path)
    ejecutar_comando("dotnet add package Swashbuckle.AspNetCore --version 6.0.0", cwd=api_path)
    ejecutar_comando("dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer", cwd=api_path)
    print_ok("Dependencias instaladas correctamente")

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

    # Calcular y mostrar duración
    duracion = round(time() - inicio, 2)
    print_ok(f"\n🎉 Proyecto .NET completo listo en {duracion}s.")
    print_info(f"Swagger: https://localhost:5001/swagger")

    # Levantar el servidor si se indica
    if args.run:
        print_info("Levantando servidor...")
        ejecutar_comando("dotnet run", cwd=api_path)


if __name__ == "__main__":
    main()
