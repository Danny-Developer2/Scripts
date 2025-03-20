from pathlib import Path
from colores import print_ok
from comandos import ejecutar_comando

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

   # Ruta del archivo Program.cs actual
    program_path = api_path / "Program.cs"

    # Eliminar el archivo Program.cs si existe
    if program_path.exists():
        program_path.unlink()  # Esto eliminará el archivo actual Program.cs

    # Crear el nuevo contenido de Program.cs
    program_text = """
    using prueba.Interfaces;
    using Microsoft.OpenApi.Models;
    using prueba.Repositories;
    using prueba.Data;
    using Microsoft.EntityFrameworkCore;

    var builder = WebApplication.CreateBuilder(args);

    // Configuración de servicios
    // Configurar OpenAPI/Swagger
    builder.Services.AddSwaggerGen(c =>
    {
        c.SwaggerDoc("v1", new OpenApiInfo
        {
            Title = "Mi API",
            Version = "v1",
            Description = "Ejemplo de API con Swagger en ASP.NET Core"
        });
    });

    // Agregar DbContext para SQLite
    builder.Services.AddDbContext<AppDbContext>(options =>
        options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

    // Registrar los servicios de repositorio
    builder.Services.AddScoped<IProductoRepository, ProductoRepository>();

    // Agregar controladores
    builder.Services.AddControllers();

    // Habilitar CORS (si necesitas permitir solicitudes desde otros dominios)
    builder.Services.AddCors(options =>
    {
        options.AddPolicy("AllowAll", builder =>
            builder.AllowAnyOrigin()
                .AllowAnyMethod()
                .AllowAnyHeader());
    });

    var app = builder.Build();

    // Habilitar Swagger en desarrollo
    if (app.Environment.IsDevelopment())
    {
        app.UseSwagger();
        app.UseSwaggerUI(c =>
        {
            c.SwaggerEndpoint("/swagger/v1/swagger.json", "Mi API v1");
            c.RoutePrefix = string.Empty; // Hace que Swagger esté disponible en la raíz
        });
    }

    // Configuración de CORS (si es necesario)
    app.UseCors("AllowAll");

    // Habilitar redirección HTTPS (comentarlo si no estás usando HTTPS en desarrollo)
    app.UseHttpsRedirection();

    // Configurar las rutas de la aplicación
    app.UseRouting();

    // Mapeo de controladores
    app.MapControllers();

    // Iniciar la aplicación
    app.Run();
    """

    # Escribir el nuevo contenido en el archivo Program.cs
    program_path.write_text(program_text)

    print("Archivo Program.cs reemplazado con la nueva configuración.")

    # Agregar configuración de redirección HTTPS
    if "app.UseHttpsRedirection();" not in program_text:
        program_text = program_text.replace("app.UseRouting();", "app.UseHttpsRedirection();\n\napp.UseRouting();")
        print_ok("Program.cs: Redirección HTTPS agregada")

    # Guardar el archivo Program.cs actualizado
    program_path.write_text(program_text)
    print_ok("Program.cs actualizado con la configuración completa")

    # Guardar otros archivos (Entity, DTO, etc.)
    (api_path / "Entities" / "Producto.cs").write_text(entity_code)
    (api_path / "Dto" / "ProductoDto.cs").write_text(dto_code)
    (api_path / "Data" / "AppDbContext.cs").write_text(context_code)
    (api_path / "Interfaces" / "IProductoRepository.cs").write_text(interface_code)
    (api_path / "Repositories").mkdir(exist_ok=True)
    (api_path / "Repositories" / "ProductoRepository.cs").write_text(repository_code)
    (api_path / "Helpers" / "FormatoHelper.cs").write_text(helper_code)
    (api_path / "Controllers" / "ProductosController.cs").write_text(controller_code)
print_ok("Entity, DTO, Context, Repository, Helper, Controller creados")
