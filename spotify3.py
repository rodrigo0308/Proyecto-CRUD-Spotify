import bcrypt #Libreria para protejer las contrasenas de usuarios y hacer la BD mas segura
import mysql.connector #Libreria para conectarnos a la BD de Mysql XAMPP

# Conexión a la base de datos
def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="spotify_simulacion"
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error conectando a la base de datos: {err}")
        return None

# Función para crear la cuenta
def crear_cuenta():
    conexion = conectar_db()
    if conexion is None:
        return
    cursor = conexion.cursor()

    # Pedimos los datos al usuario
    nombre = input("Introduce tu nombre: ")
    apellido = input("Introduce tu apellido: ")
    email = input("Introduce tu email: ")
    contraseña = input("Introduce tu contraseña: ")

    # Verificamos si el email ya está registrado
    cursor.execute("SELECT * FROM Usuarios WHERE Email = %s", (email,))
    usuario_existente = cursor.fetchone()
    if usuario_existente:
        print("El email ya está registrado. Intenta con otro.")
    else:
        # Hasheamos la contraseña
        contraseña_hash = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

        # Verificamos si el email es de dominio @example.com para ser admin
        if email.endswith("@example.com"):
            es_admin = True
            print("Este usuario será administrador.")
        else:
            es_admin = False
            print("Este usuario será un usuario normal.")

        # Insertamos el nuevo usuario en la base de datos
        try:
            cursor.execute(
                "INSERT INTO Usuarios (Nombre, Apellido, Email, Contraseña, es_admin) VALUES (%s, %s, %s, %s, %s)",
                (nombre, apellido, email, contraseña_hash.decode('utf-8'), es_admin)
            )
            conexion.commit()
            print("¡Cuenta creada exitosamente!")
        except mysql.connector.Error as err:
            print(f"Error al crear la cuenta: {err}")

    cursor.close()
    conexion.close()

# Función para iniciar sesión
def iniciar_sesion():
    conexion = conectar_db()
    if conexion is None:
        return
    cursor = conexion.cursor()
    #Pedimos al usuario que ingrese el correo y contrasena
    correo = input("Introduce tu correo: ")
    contraseña = input("Introduce tu contraseña: ")

    try:
        # Seleccionamos la contraseña, el estado de admin, el ID y el nombre del usuario para el usuario con el correo proporcionado
        cursor.execute("SELECT id, nombre, Contraseña, es_admin FROM Usuarios WHERE Email = %s", (correo,))
        resultado = cursor.fetchone()

        if resultado:
            usuario_id = resultado[0]
            nombre = resultado[1]
            contraseña_hash = resultado[2]
            es_admin = resultado[3]

            # Verificamos la contraseña usando bcrypt
            if bcrypt.checkpw(contraseña.encode('utf-8'), contraseña_hash.encode('utf-8')):
                print("Inicio de sesión exitoso.")
                
                # Si es administrador, mostramos el menú de administrador
                if es_admin:
                    print(f"Bienvenido Administrador {nombre}")
                    menu_administrador()
                else:
                    print(f"Bienvenido Usuario {nombre}")
                    menu_usuario(usuario_id, nombre)  # Aquí pasamos el usuario_id y el nombre
            else:
                print("Contraseña incorrecta.")
        else:
            print("Correo no encontrado.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conexion.close()


# Función para crear una lista de reproducción
def crear_lista_reproduccion(usuario_id):
    conexion = conectar_db()
    cursor = conexion.cursor()

    nombre_lista = input("Introduce el nombre de la lista de reproducción: ")
    tipo_lista = input("¿La lista será pública o privada? (pública/privada): ").lower()

    # Determinar si la lista es pública o privada
    es_publica = tipo_lista == 'pública'

    # Insertar la lista en la tabla Listas_Reproducciones
    cursor.execute("INSERT INTO Listas_Reproducciones (nombre, usuario_id, fecha_creacion) VALUES (%s, %s, NOW())", 
                   (nombre_lista, usuario_id))
    conexion.commit()
    print(f"¡Lista de reproducción '{nombre_lista}' creada exitosamente!")

    cursor.close()
    conexion.close()

# Función para añadir canción a una lista de reproducción
def agregar_cancion_a_lista(usuario_id):
    conexion = conectar_db()
    cursor = conexion.cursor()
    #Pedimos al usuario que ingrese el ID de la lista de reproduccion y la cancion a agregar
    lista_id = input("Introduce el ID de la lista de reproducción: ")
    cancion_id = input("Introduce el ID de la canción que deseas agregar: ")

    # Insertar la canción en la lista
    cursor.execute("INSERT INTO Lista_Canciones (lista_id, cancion_id) VALUES (%s, %s)", (lista_id, cancion_id))
    conexion.commit()
    print("¡Canción añadida a la lista de reproducción!")

    cursor.close()
    conexion.close()

# Función para añadir canción a la biblioteca del usuario
def agregar_cancion_a_biblioteca(usuario_id):
    conexion = conectar_db()
    cursor = conexion.cursor()

    cancion_id = input("Introduce el ID de la canción que deseas agregar a tu biblioteca: ")

    # Insertar la canción en la biblioteca del usuario
    cursor.execute("INSERT INTO Bibliotecas (usuario_id, cancion_id) VALUES (%s, %s)", (usuario_id, cancion_id))
    conexion.commit()
    print("¡Canción añadida a tu biblioteca!")

    cursor.close()
    conexion.close()

# Función para buscar canciones por nombre
def buscar_cancion_por_nombre():
    conexion = conectar_db()
    cursor = conexion.cursor()

    nombre_cancion = input("Introduce el nombre de la canción que deseas buscar: ")

    # Buscar canciones que coincidan con el nombre
    cursor.execute("SELECT * FROM Canciones WHERE titulo LIKE %s", ('%' + nombre_cancion + '%',))
    canciones = cursor.fetchall()

    if canciones:
        print("Canciones encontradas:")
        for cancion in canciones:
            print(f"ID: {cancion[0]}, Título: {cancion[1]}, Duración: {cancion[2]}")
    else:
        print("No se encontraron canciones con ese nombre.")

    cursor.close()
    conexion.close()

# Menú de administrador
def menu_administrador():
    while True:
        print("\n===== Menú de Administrador =====")
        print("1. Añadir artista")
        print("2. Añadir canción")
        print("3. Añadir álbum")
        print("4. Salir")
        opcion = input("Selecciona una opción: ")
        if opcion == "4":
            break
        # Aquí puedes implementar las opciones del menú de administrador

# Menú del usuario
def menu_usuario(usuario_id, nombre):
    while True:
        print(f"\n===== Menú de Usuario =====")
        print(f"Bienvenido, {nombre}!")
        print("1. Crear lista de reproducción")
        print("2. Añadir canción a lista de reproducción")
        print("3. Añadir canción a biblioteca")
        print("4. Buscar canciones por nombre")
        print("5. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            crear_lista_reproduccion(usuario_id)
        elif opcion == "2":
            agregar_cancion_a_lista(usuario_id)
        elif opcion == "3":
            agregar_cancion_a_biblioteca(usuario_id)
        elif opcion == "4":
            buscar_cancion_por_nombre()
        elif opcion == "5":
            break
        else:
            print("Opción no válida. Intenta de nuevo.")
        # Aquí puedes implementar las opciones del menú de usuario

# Menú de principal de spotify terminal
def menu_principal():
    while True:
        print("\n===== SPOTIFY =====")  # Agregamos el título aquí
        print("1. Crear cuenta")
        print("2. Iniciar sesión")
        print("3. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            crear_cuenta()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion == "3":
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    menu_principal()
