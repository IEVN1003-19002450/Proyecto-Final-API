from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import config

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
conexion = MySQL(app)

# Ruta para login
@app.route("/login", methods=["POST"])
def login():
    try:
        cursor = conexion.connection.cursor()
        username = request.json['username']
        password = request.json['password']
        
        sql = """SELECT u.id, u.username, r.nombre as rol 
                FROM usuarios u 
                JOIN roles r ON u.rol_id = r.id 
                WHERE username = %s AND password = %s"""
        cursor.execute(sql, (username, password))
        
        usuario = cursor.fetchone()
        if usuario:
            return jsonify({
                'id': usuario[0],
                'username': usuario[1],
                'rol': usuario[2],
                'exito': True
            })
        return jsonify({'mensaje': "Credenciales incorrectas", 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Listar todas las instituciones
@app.route("/instituciones", methods=["GET"])
def listar_instituciones():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT id, nombre, direccion, telefono FROM instituciones"
        cursor.execute(sql)
        datos = cursor.fetchall()
        instituciones = []
        for fila in datos:
            institucion = {
                'id': fila[0],
                'nombre': fila[1],
                'direccion': fila[2],
                'telefono': fila[3]
            }
            instituciones.append(institucion)
        return jsonify({'instituciones': instituciones, 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Obtener una institución específica
@app.route("/instituciones/<int:id>", methods=["GET"])
def obtener_institucion(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT i.id, i.nombre, i.direccion, i.telefono, 
                i.encargado_id, u.username as encargado_nombre
                FROM instituciones i
                LEFT JOIN usuarios u ON i.encargado_id = u.id
                WHERE i.id = %s"""
        cursor.execute(sql, (id,))
        dato = cursor.fetchone()
        
        if dato is None:
            return jsonify({
                'mensaje': "Institución no encontrada",
                'exito': False
            })

        institucion = {
            'id': dato[0],
            'nombre': dato[1],
            'direccion': dato[2],
            'telefono': dato[3],
            'encargado_id': dato[4],
            'encargado_nombre': dato[5]
        }
        
        return jsonify({
            'institucion': institucion,
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Crear una nueva institución
@app.route("/instituciones", methods=["POST"])
def crear_institucion():
    try:
        cursor = conexion.connection.cursor()
        sql = """INSERT INTO instituciones (nombre, direccion, telefono, encargado_id) 
                VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (
            request.json['nombre'],
            request.json['direccion'],
            request.json['telefono'],
            request.json['encargado_id']
        ))
        conexion.connection.commit()
        return jsonify({
            'mensaje': "Institución creada exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Actualizar una institución existente
@app.route("/instituciones/<int:id>", methods=["PUT"])
def actualizar_institucion(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """UPDATE instituciones 
                SET nombre = %s, 
                    direccion = %s, 
                    telefono = %s, 
                    encargado_id = %s 
                WHERE id = %s"""
        cursor.execute(sql, (
            request.json['nombre'],
            request.json['direccion'],
            request.json['telefono'],
            request.json['encargado_id'],
            id
        ))
        conexion.connection.commit()
        return jsonify({
            'mensaje': "Institución actualizada exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Eliminar una institución
@app.route("/instituciones/<int:id>", methods=["DELETE"])
def eliminar_institucion(id):
    try:
        cursor = conexion.connection.cursor()
        # Primero verificamos si hay alumnos en esta institución
        sql_check = "SELECT COUNT(*) FROM alumnos WHERE institucion_id = %s"
        cursor.execute(sql_check, (id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return jsonify({
                'mensaje': "No se puede eliminar la institución porque tiene alumnos registrados",
                'exito': False
            })

        # Si no hay alumnos, procedemos a eliminar
        sql_delete = "DELETE FROM instituciones WHERE id = %s"
        cursor.execute(sql_delete, (id,))
        conexion.connection.commit()
        
        return jsonify({
            'mensaje': "Institución eliminada exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Listar todos los alumnos
@app.route("/alumnos", methods=["GET"])
def listar_alumnos():
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT a.*, i.nombre as institucion_nombre 
                FROM alumnos a 
                JOIN instituciones i ON a.institucion_id = i.id"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        alumnos = []
        for fila in datos:
            alumno = {
                'id': fila[0],
                'nombre': fila[1],
                'institucion_id': fila[2],
                'nivel': fila[3],
                'calificacion_inicial': float(fila[4]),
                'calificacion_final': float(fila[5]),
                'fecha_registro': fila[6].strftime('%Y-%m-%d %H:%M:%S'),
                'institucion_nombre': fila[7]
            }
            alumnos.append(alumno)
        return jsonify({'alumnos': alumnos, 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Listar alumnos por institución
@app.route("/alumnos/institucion/<int:institucion_id>", methods=["GET"])
def listar_alumnos_por_institucion(institucion_id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT * FROM alumnos WHERE institucion_id = %s"""
        cursor.execute(sql, (institucion_id,))
        datos = cursor.fetchall()
        alumnos = []
        for fila in datos:
            alumno = {
                'id': fila[0],
                'nombre': fila[1],
                'institucion_id': fila[2],
                'nivel': fila[3],
                'calificacion_inicial': float(fila[4]),
                'calificacion_final': float(fila[5]),
                'fecha_registro': fila[6].strftime('%Y-%m-%d %H:%M:%S')
            }
            alumnos.append(alumno)
        return jsonify({'alumnos': alumnos, 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Crear nuevo alumno
@app.route("/alumnos", methods=["POST"])
def crear_alumno():
    try:
        cursor = conexion.connection.cursor()
        sql = """INSERT INTO alumnos (nombre, institucion_id, nivel, 
                calificacion_inicial, calificacion_final) 
                VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            request.json['nombre'],
            request.json['institucion_id'],
            request.json['nivel'],
            request.json['calificacion_inicial'],
            request.json['calificacion_final']
        ))
        conexion.connection.commit()
        return jsonify({
            'mensaje': "Alumno creado exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Actualizar alumno
@app.route("/alumnos/<int:id>", methods=["PUT"])
def actualizar_alumno(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """UPDATE alumnos 
                SET nombre = %s,
                    institucion_id = %s,
                    nivel = %s,
                    calificacion_final = %s
                WHERE id = %s"""
        cursor.execute(sql, (
            request.json['nombre'],
            request.json['institucion_id'],
            request.json['nivel'],
            request.json['calificacion_final'],
            id
        ))
        conexion.connection.commit()
        return jsonify({
            'mensaje': "Alumno actualizado exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Eliminar alumno
@app.route("/alumnos/<int:id>", methods=["DELETE"])
def eliminar_alumno(id):
    try:
        cursor = conexion.connection.cursor()
        sql = "DELETE FROM alumnos WHERE id = %s"
        cursor.execute(sql, (id,))
        conexion.connection.commit()
        return jsonify({
            'mensaje': "Alumno eliminado exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Promedio general de calificaciones por institución
@app.route("/estadisticas/promedio/<int:institucion_id>", methods=["GET"])
def promedio_calificaciones(institucion_id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT AVG(calificacion_final) as promedio
                 FROM alumnos
                 WHERE institucion_id = %s"""
        cursor.execute(sql, (institucion_id,))
        resultado = cursor.fetchone()
        
        if resultado[0] is None:
            return jsonify({
                'mensaje': "No hay calificaciones para esta institución",
                'exito': False
            })
        
        return jsonify({
            'promedio': float(resultado[0]),
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Comparación de calificaciones iniciales y finales por institución
@app.route("/estadisticas/comparacion/<int:institucion_id>", methods=["GET"])
def comparacion_calificaciones(institucion_id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT 
                    AVG(calificacion_inicial) as promedio_inicial,
                    AVG(calificacion_final) as promedio_final
                 FROM alumnos
                 WHERE institucion_id = %s"""
        cursor.execute(sql, (institucion_id,))
        resultado = cursor.fetchone()
        
        if resultado[0] is None or resultado[1] is None:
            return jsonify({
                'mensaje': "No hay suficientes datos para esta institución",
                'exito': False
            })
            
        return jsonify({
            'promedio_inicial': float(resultado[0]),
            'promedio_final': float(resultado[1]),
            'mejora': float(resultado[1] - resultado[0]),
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Listar usuarios
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT u.id, u.username, r.nombre as rol 
                 FROM usuarios u 
                 JOIN roles r ON u.rol_id = r.id"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        usuarios = []
        for fila in datos:
            usuario = {
                'id': fila[0],
                'username': fila[1],
                'rol': fila[2]
            }
            usuarios.append(usuario)
        return jsonify({'usuarios': usuarios, 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Obtener un usuario específico
@app.route("/usuarios/<int:id>", methods=["GET"])
def obtener_usuario(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT u.id, u.username, r.nombre as rol 
                 FROM usuarios u 
                 JOIN roles r ON u.rol_id = r.id 
                 WHERE u.id = %s"""
        cursor.execute(sql, (id,))
        dato = cursor.fetchone()
        
        if dato is None:
            return jsonify({
                'mensaje': "Usuario no encontrado",
                'exito': False
            })

        usuario = {
            'id': dato[0],
            'username': dato[1],
            'rol': dato[2]
        }
        
        return jsonify({
            'usuario': usuario,
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Crear un nuevo usuario
@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    try:
        cursor = conexion.connection.cursor()
        sql = """INSERT INTO usuarios (username, password, rol_id) 
                VALUES (%s, %s, %s)"""
        cursor.execute(sql, (
            request.json['username'],
            request.json['password'],
            request.json['rol_id']
        ))
        conexion.connection.commit()
        return jsonify({
            'mensaje': "Usuario creado exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Actualizar un usuario existente
@app.route("/usuarios/<int:id>", methods=["PUT"])
def actualizar_usuario(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """UPDATE usuarios 
                SET username = %s, 
                    password = %s, 
                    rol_id = %s 
                WHERE id = %s"""
        cursor.execute(sql, (
            request.json['username'],
            request.json['password'],
            request.json['rol_id'],
            id
        ))
        conexion.connection.commit()
        return jsonify({
            'mensaje': "Usuario actualizado exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

# Eliminar un usuario
@app.route("/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    try:
        cursor = conexion.connection.cursor()
        sql_delete = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(sql_delete, (id,))
        conexion.connection.commit()
        return jsonify({
            'mensaje': "Usuario eliminado exitosamente",
            'exito': True
        })
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()