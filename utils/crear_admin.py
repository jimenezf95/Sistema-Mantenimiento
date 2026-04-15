from database import crear_usuario, crear_tabla_usuarios

# Crear tabla si no existe
crear_tabla_usuarios()

# Crear usuario admin
crear_usuario("Admin", "21100", "admin")

print("Usuario admin creado correctamente")