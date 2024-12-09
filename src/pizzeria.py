from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import config

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "http://localhost:4200",
        "methods": ["GET", "POST", "DELETE", "PUT"],
        "allow_headers": ["Content-Type"]
    }
})

conexion = MySQL(app)


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


@app.route("/alumnos/<int:institucion_id>", methods=["GET"])
def listar_alumnos(institucion_id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT id, nombre, nivel, calificacion_inicial, calificacion_final 
                FROM alumnos WHERE institucion_id = %s"""
        cursor.execute(sql, (institucion_id,))
        datos = cursor.fetchall()
        alumnos = []
        for fila in datos:
            alumno = {
                'id': fila[0],
                'nombre': fila[1],
                'nivel': fila[2],
                'calificacion_inicial': float(fila[3]),
                'calificacion_final': float(fila[4])
            }
            alumnos.append(alumno)
        return jsonify({'alumnos': alumnos, 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f"Error: {str(ex)}", 'exito': False})

if __name__ == "__main__":
    app.config.from_object(config['development'])
    app.run()
