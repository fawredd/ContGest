# Importa la instancia de Flask creada en __init__.py
from modules import app
# Importa la instancia de SQLAlchemy creada en __init__.py
from modules import db
# Importa la instancia de Marshmallow creada en __init__.py
from modules import ma
# Importa los modelos
from modules.models import *
import os
import json
#jsonify: Es una función que convierte los datos en formato JSON para ser enviados como respuesta desde la API.
#request: Es un objeto que representa la solicitud HTTP realizada por el cliente.
from flask import jsonify, request 

'''
Este código define un endpoint que permite obtener todos los asientos de la base de datos y los devuelve como un JSON en respuesta a una solicitud GET a la ruta /asientos.
@app.route("/asientos", methods=["GET"]): Este decorador establece la ruta /asientos para este endpoint y especifica que solo acepta solicitudes GET.
def get_Asientos(): Esta es la función asociada al endpoint. Se ejecuta cuando se realiza una solicitud GET a la ruta /asientos.
all_asientos = Producto.query..: Se obtienen todos los registros de la tabla de asientos mediante la consulta Asientos.query..... Esto se realiza utilizando el modelo Asientos que representa la tabla en la base de datos. El método query heredado de db.Model se utiliza para obtener los registros de la tabla.
result = asientos_schemas.dump(all_asientos): Los registros obtenidos se serializan en formato JSON utilizando el método dump() del objeto asientos_schemas. El método dump() heredado de ma.Schema se utiliza para convertir los objetos Python en representaciones JSON.
return jsonify(result): El resultado serializado en formato JSON se devuelve como respuesta al cliente utilizando la función jsonify() de Flask. Esta función envuelve el resultado en una respuesta HTTP con el encabezado Content-Type establecido como application/json.
'''
@app.route("/asientos", methods=["GET"])
def get_Asientos():
    """
    Endpoint para obtener todos los asientos de la base de datos.
    Retorna un JSON con todos los registros de la tabla de asientos.
    """
    all_asientos = Asientos.query.order_by(Asientos.id.desc()).limit(10).all()  # Obtiene los ultimos 10 registros de la tabla de asientos
    result = asientos_schemas.dump(all_asientos)  # Serializa los registros en formato JSON
    return jsonify(result)  # Retorna el JSON de todos los registros de la tabla

@app.route("/cuentas", methods=["GET"])
def get_cuentas():
    """
    Endpoint para obtener todos ls cuentas de la base de datos.
    Retorna un JSON con todos los registros de la tabla de PlanDeCuentas.
    """
    all_cuentas = PlanDeCuentas.query.order_by(PlanDeCuentas.id.asc()).all()
    result = PlanDeCuentas_schemas.dump(all_cuentas)  # Serializa los registros en formato JSON
    return jsonify(result)  # Retorna el JSON de todos los registros de la tabla

@app.route("/operaciones", methods=["GET"])
def get_operaciones():
    """
    Endpoint para obtener todas las operaciones de la base de datos.
    Retorna un JSON con todos los registros de la tabla de Operaciones.
    """
    all_operaciones = Operaciones.query.order_by(Operaciones.id.asc()).all()
    result = Operaciones_schemas.dump(all_operaciones)  # Serializa los registros en formato JSON
    return jsonify(result)  # Retorna el JSON de todos los registros de la tabla

@app.route("/asientos/<int:id>", methods=["GET"])
def get_asiento(id):
    """
    Endpoint para obtener un asiento específico de la base de datos.
    Retorna un JSON con la información del asiento correspondiente al ID proporcionado.
    """
    asiento = db.session.get(Asientos,id)  # Obtiene el Asiento correspondiente al ID recibido
    return asientos_schema.jsonify(asiento)  # Retorna el JSON del producto

@app.route("/asientos/find/<string:texto>", methods=["GET"])
def busca_asiento(texto):
    """
    Endpoint para buscar asientos en la base de datos.

    Retorna un JSON con la información de los asientos correspondientes.
    """
    texto_min = texto.lower()  # Convertir la cadena de búsqueda a minúscula
    all_asientos = db.session.query(Asientos).filter(Asientos.detalle.ilike(f'%{texto_min}%')).all()  # Filtra los asientos que contienen el texto en el detalle
    result = asientos_schemas.dump(all_asientos)  # Serializa los registros en formato JSON
    return jsonify(result)  # Retorna el JSON de todos los registros de la tabla

@app.route("/asientos/<id>", methods=["DELETE"])
def delete_asiento(id):
    """
    Endpoint para eliminar un asiento de la base de datos.
    Elimina el asiento correspondiente al ID proporcionado y retorna un JSON con el registro eliminado.
    """
    asiento = db.session.get(Asientos,id)  # Obtiene el asiento correspondiente al ID recibido
    db.session.delete(asiento)  # Elimina el producto de la sesión de la base de datos
    db.session.commit()  # Guarda los cambios en la base de datos
    return asientos_schema.jsonify(asiento)  # Retorna el JSON del producto eliminado

@app.route("/asientos", methods=["POST"])  # Endpoint para crear un asiento
def create_asiento():
    """
    Endpoint para crear un nuevo asiento en la base de datos.
    Lee los datos proporcionados en formato JSON por el cliente y crea un nuevo registro de asiento en la base de datos.
    Retorna un JSON con el nuevo asiento creado.
    """
    # Verifico que exista el objeto asiento
    asiento_data = request.form.get('asiento')
    if asiento_data is None:
        return 'El "asiento" no existe en los datos de la solicitud.', 400
    else:
        asiento = json.loads(asiento_data)
        fechaRegistro = asiento["fechaRegistro"]
        fechaMovimiento = asiento["fechaMovimiento"]  
        operacion = asiento["operacion"] 
        detalle = asiento["detalle"]  
        estado = asiento["estado"]

        # Verificar si la operación existe
        operacion_check = db.session.query(Operaciones).filter_by(id=operacion).first()
        if not operacion_check:
            raise ValueError(f"La operación con ID {operacion} no existe")
        
        # Agrego los datos recibidos al nuevo registro
        new_asiento = Asientos(fechaRegistro,fechaMovimiento, operacion, detalle, estado)  
        db.session.add(new_asiento)  

        # Crear nuevas transacciones para el asiento utilizando los datos proporcionados
        nuevas_transacciones = []
        total_movimiento = 0.0  # Inicializar la variable para sumar los movimientos
        for transaccion_data in asiento["transacciones"]:
            cuenta = transaccion_data["cuenta"]
            movimiento = transaccion_data["movimiento"]
            tc = transaccion_data["tc"]
            detalle = transaccion_data["detalle"]
            estado = transaccion_data["estado"]
            # Agregar el movimiento de la transacción a la variable total_movimiento
            total_movimiento += movimiento

            # Crear una nueva transacción para el asiento
            new_transaccion = Transacciones(new_asiento.id, movimiento, tc, cuenta, detalle, estado)
            db.session.add(new_transaccion)
            nuevas_transacciones.append(new_transaccion)

        # Verificar que la suma de los movimientos sea igual a cero
        if total_movimiento != 0.0:
            raise ValueError(f"La suma de los movimientos de las transacciones no es cero. La suma es {total_movimiento}")

        # Agregar las nuevas transacciones al objeto Asientos
        new_asiento.transacciones = nuevas_transacciones

        # Verifico los adjuntos
        nuevos_adjuntos = []
        for adjunto_data in asiento["adjuntosAsientos"]:
            archivo = adjunto_data["adjunto"]
            estado = adjunto_data["estado"]
            detalle = adjunto_data["detalle"]
            # Obtener el archivo subido desde la solicitud
            archivoSave = request.files[archivo]
            # Guardar el archivo en el servidor
            archivoSave.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo))
            # Crear una nuevo registro para el asiento
            new_adjunto = AdjuntosAsientos(new_asiento.id, archivo, detalle, estado)
            db.session.add(new_adjunto)
            nuevos_adjuntos.append(new_adjunto)

        # Agregar los adjuntos al objeto Asientos
        new_asiento.adjuntos = nuevos_adjuntos

        db.session.commit()
        # Crear un diccionario con los datos del objeto Asientos y sus transacciones
        asiento_data = asientos_schema.dump(new_asiento)
        transacciones_data = transacciones_schemas.dump(nuevas_transacciones)
        adjuntos_data = AdjuntosAsientos_schemas.dump(nuevos_adjuntos)
        asiento_data["transacciones"] = transacciones_data
        asiento_data["adjuntos"] = adjuntos_data
        return asientos_schema.jsonify(asiento_data)  # Retorna el JSON del nuevo asiento creado

@app.route("/asientos/<id>", methods=["PUT"])  # Endpoint para actualizar un asiento
def update_asiento(id):
    """
    Endpoint para actualizar un asiento existente en la base de datos.
    Lee los datos proporcionados en formato JSON por el cliente y actualiza el registro del asiento con el ID especificado.
    Retorna un JSON con el asiento actualizado.
    """
    asiento = db.session.get(Asientos,id)  # Obtiene el asiento existente con el ID especificado

    # Actualiza los atributos del asiento con los datos proporcionados en el JSON
    asiento.fecha = request.json["fecha"]
    asiento.operacion = request.json["operacion"]
    asiento.detalle = request.json["detalle"]
    asiento.estado = request.json["estado"]
    total_movimiento = 0.0  # Inicializar la variable para sumar los movimientos
    for transacciones in request.json["transacciones"]:
        transaccion = db.session.query(Transacciones).get(transacciones["id"])  # Obtiene la transaccion existente con el ID especificado
        # Actualiza los atributos de la transaccion con los datos proporcionados en el JSON
        transaccion.cuenta = transacciones["cuenta"]
        transaccion.movimiento = transacciones["movimiento"]
        transaccion.tc = transacciones["tc"]
        transaccion.detalle = transacciones["detalle"]
        transaccion.estado = transacciones["estado"]
         # Agregar el movimiento de la transacción a la variable total_movimiento
        total_movimiento += transacciones["movimiento"]

    # Verificar que la suma de los movimientos sea igual a cero
    if total_movimiento != 0.0:
        raise ValueError(f"La suma de los movimientos de las transacciones no es cero. La suma es {total_movimiento}")    

    db.session.commit()  # Guarda los cambios en la base de datos

    # Obtener todas las transacciones asociadas al asiento actualizado
    transacciones = db.session.query(Transacciones).filter_by(asiento=id).all()
    # Serializar las transacciones utilizando el esquema de transacciones
    transacciones_data = transacciones_schemas.dump(transacciones)
    # Agregar las transacciones al diccionario del asiento
    asiento_data = asientos_schema.dump(asiento)
    asiento_data["transacciones"] = transacciones_data

    return asientos_schema.jsonify(asiento_data)  # Retorna el JSON del asiento actualizado

@app.route("/operaciones", methods=["POST"])  # Endpoint para crear un registro de operacion
def create_operacion():
    """
    Endpoint para crear una nueva operacion en la base de datos.
    Lee los datos proporcionados en formato JSON por el cliente y crea un nuevo registro de operacion en la base de datos.
    Retorna un JSON con el nuevo registro creado.
    """
    empresa = request.json["empresa"]  
    operador = request.json["operador"]  
    detalle = request.json["detalle"] 
    estado = request.json["estado"] 
    # Verificar si la empresa relacionada existe
    empresa_check = db.session.query(Empresa).filter_by(id=empresa).first()
    if not empresa_check:
        raise ValueError(f"La empresa con ID {empresa} no existe")
    
    new_operacion = Operaciones(operador, detalle, empresa, estado)  
    db.session.add(new_operacion)  
    db.session.commit()  
    return Operaciones_schema.jsonify(new_operacion)  # Retorna el JSON de la nueva operacion creada

@app.route("/empresas", methods=["POST"])  # Endpoint para crear un registro de empresa
def create_empresas():
    """
    Endpoint para crear una nueva empresa en la base de datos.
    Lee los datos proporcionados en formato JSON por el cliente y crea un nuevo registro de empresa en la base de datos.
    Retorna un JSON con el nuevo registro creado.
    """
    nombre = request.json["nombre"]  
    estado = request.json["estado"] 
    
    new_empresa = Empresa(nombre, estado)  
    db.session.add(new_empresa)  
    db.session.commit()  
    return Empresas_schema.jsonify(new_empresa)  # Retorna el JSON de la nueva operacion creada

@app.route("/transaccion/<id>", methods=["PUT"])  # Endpoint para actualizar una transaccion
def update_transaccion(id):
    """
    Endpoint para actualizar una transaccion existente en la base de datos.
    Lee los datos proporcionados en formato JSON por el cliente y actualiza el registro de la transaccion con el ID especificado.
    Retorna un JSON con la transaccion actualizada.
    """
    transaccion = Transacciones.query.get(id)  # Obtiene la transaccion existente con el ID especificado

    # Actualiza los atributos de la transaccion con los datos proporcionados en el JSON
    transaccion.cuenta = request.json["cuenta"]
    transaccion.movimiento = request.json["movimiento"]
    transaccion.tc = request.json["tc"]
    transaccion.detalle = request.json["detalle"]
    transaccion.estado = request.json["estado"]

    db.session.commit()  # Guarda los cambios en la base de datos
    return transacciones_schema.jsonify(transaccion)  # Retorna el JSON de la transaccion actualizado

@app.route("/cuentas/<int:id>", methods=["GET"])
def get_mayor(id):
    """
    Endpoint para obtener todos las transacciones asociadas a la cuenta del id.

    Retorna un JSON con todos los registros.
    """
    laCuenta = db.session.query(PlanDeCuentas).filter_by(id=id).first()
    lasTransacciones = db.session.query(Transacciones).filter_by(cuenta=laCuenta.id).all()
    nuevasTransacciones = []
    for transaccion in lasTransacciones:
        elAsiento = db.session.query(Asientos).filter_by(id=transaccion.asiento).first()
        nuevaTransaccion = {
            "id": transaccion.id,
            "fechaRegistro": elAsiento.fechaRegistro,
            "fechaMovimiento": elAsiento.fechaMovimiento,            
            "asiento": elAsiento.id,
            "operacion": elAsiento.operacion,
            "movimiento": transaccion.movimiento,
            "detalleAsiento": elAsiento.detalle,
            "detalleTransaccion": transaccion.detalle,
            "cuenta": laCuenta.nombre
        }
        nuevasTransacciones.append(nuevaTransaccion)
    result = Mayor_schemas.dump(nuevasTransacciones)  # Serializa los registros en formato JSON
    return jsonify(result)  # Retorna el JSON de todos los registros de la tabla