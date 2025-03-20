

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
