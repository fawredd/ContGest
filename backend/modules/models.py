# Importa la instancia de Flask creada en __init__.py
from modules import app
from modules import db, ma

class Empresa(db.Model):
    """
    Clase que representa una empresa en la base de datos.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.Integer, default = 0, nullable=False)

    def __init__(self, nombre, estado):
        """
        Constructor de la clase Empresa.
        :param nombre: Nombre de la empresa.
        :type nombre: str
        :param estado: Estado de la empresa.
        :type estado: int
        """
        self.nombre = nombre
        self.estado = estado

class Operaciones(db.Model):
    """
    Clase que representa una operación en la base de datos.

    Atributos:
        id (int): Identificador único de la operación.
        operador (int): Operador de la operación.
        detalle (str): Detalle de la operación.
        empresa_id (int): Identificador de la empresa asociada a la operación.
        estado (int): Estado de la operación.

    Métodos:
        __init__(self, operador, detalle, empresa_id, estado):
            Constructor de la clase Operaciones.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operador = db.Column(db.Integer, nullable=False)
    detalle = db.Column(db.Text, nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    estado = db.Column(db.Integer, default = 0, nullable=False)
    asientos = db.relationship(lambda: Asientos, back_populates='operacion_relacion')

    def __init__(self, operador, detalle, empresa_id, estado):
        """
        Constructor de la clase Operaciones.

        :param operador: Operador de la operación.
        :type operador: int
        :param detalle: Detalle de la operación.
        :type detalle: str
        :param empresa_id: Identificador de la empresa asociada a la operación.
        :type empresa_id: int
        :param estado: Estado de la operación.
        :type estado: int
        """
        self.operador = operador
        self.detalle = detalle
        self.empresa_id = empresa_id
        self.estado = estado

class Asientos(db.Model):  # Asientos hereda de db.Model
    """
    Definición de la tabla Asientos en la base de datos.
    La clase Asientos hereda de db.Model.
    Esta clase representa la tabla "Asientos" en la base de datos.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaRegistro = db.Column(db.DateTime(timezone=True), default=db.func.current_date())
    fechaMovimiento = db.Column(db.DateTime(timezone=True), default=db.func.current_date())
    operacion = db.Column(db.Integer, db.ForeignKey('operaciones.id'), nullable=False)
    detalle = db.Column(db.String(255))
    estado = db.Column(db.Integer, default=0)
    transacciones = db.relationship(lambda: Transacciones, back_populates="asientos")
    operacion_relacion = db.relationship(lambda: Operaciones, back_populates="asientos")
    adjuntos = db.relationship(lambda: AdjuntosAsientos, back_populates="asientoRel")

    def __init__(self, fechaRegistro, fechaMovimiento, operacion, detalle, estado):
        """
        Constructor de la clase Asientos.

        Args:
            fecha (Date) = fecha del asiento
            operacion (int) = id de la operacion
            detalle (str) = detalle descriptivo del asiento
            estado (int) = define algun tipo de estado del asiento
        """
        self.fechaRegistro = fechaRegistro
        self.fechaMovimiento = fechaMovimiento
        self.operacion = operacion
        self.detalle = detalle
        self.estado = estado

class Transacciones(db.Model):  # Transacciones hereda de db.Model
    """
    Definición de la tabla Transacciones en la base de datos.
    La clase Transacciones hereda de db.Model.
    Esta clase representa la tabla "Transacciones" en la base de datos.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    asiento = db.Column(db.Integer, db.ForeignKey('asientos.id'), nullable=False)
    movimiento = db.Column(db.Float, default = 0)
    tc = db.Column(db.Float, default = 0)
    cuenta = db.Column(db.Integer, db.ForeignKey('plan_de_cuentas.id'), nullable=False)
    detalle = db.Column(db.String(255))
    estado = db.Column(db.Integer, default=0)
    asientos = db.relationship(lambda: Asientos, back_populates="transacciones")
    cuentas = db.relationship(lambda: PlanDeCuentas, back_populates="transacciones")

    def __init__(self, asiento, movimiento, tc, cuenta, detalle, estado):
        """
        Constructor de la clase Transacciones.

        Args:
            asiento (int) = id del asiento al que esta relacionado
            movimiento (float) = importe
            tc (float) = tipo de cambio de la moneda
            cuenta (int) = cuenta contable relacionada
            detalle (str) = Descripcion de la transaccion
            estado (int) = define un tipo de estado de la transaccion
        """
        self.asiento = asiento
        self.movimiento = movimiento
        self.tc = tc
        self.cuenta = cuenta
        self.detalle = detalle
        self.estado = estado

class PlanDeCuentas(db.Model):  # Plan de cuentas hereda de db.Model
    """
    Representa una cuenta en el plan de cuentas de un sistema contable.

    Atributos:
        codigo (str): El código único de la cuenta.
        nombre (str): El nombre de la cuenta.
        descripcion (str): La descripción de la cuenta.
        naturaleza (str): La naturaleza de la cuenta, puede ser 'debito' o 'credito'.
        cuenta_padre_id (int, opcional): El ID de la cuenta padre, si existe.
        nivel (int, opcional): El nivel de la cuenta en la estructura jerárquica del plan de cuentas.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    naturaleza = db.Column(db.Enum('debito', 'credito'), nullable=False)
    cuenta_padre_id = db.Column(db.Integer, db.ForeignKey('plan_de_cuentas.id'), nullable=True)
    nivel = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    cuenta_padre = db.relationship('PlanDeCuentas', remote_side=[id])
    transacciones = db.relationship(lambda: Transacciones, back_populates="cuentas")

    def __init__(self, codigo, nombre, descripcion, naturaleza, cuenta_padre_id, nivel):
        """
        Inicializa una nueva instancia de la clase PlanDeCuentas.

        Args:
            codigo (str): El código único de la cuenta.
            nombre (str): El nombre de la cuenta.
            descripcion (str): La descripción de la cuenta.
            naturaleza (str): La naturaleza de la cuenta, puede ser 'debito' o 'credito'.
            cuenta_padre_id (int, opcional): El ID de la cuenta padre, si existe.
            nivel (int, opcional): El nivel de la cuenta en la estructura jerárquica del plan de cuentas.
        """
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.naturaleza = naturaleza
        self.cuenta_padre_id = cuenta_padre_id
        self.nivel = nivel

class AdjuntosAsientos(db.Model):
    """
    Clase que representa una empresa en la base de datos.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asiento = db.Column(db.Integer, db.ForeignKey('asientos.id'), nullable=False) 
    archivo = db.Column(db.String(255), nullable=False)
    detalle = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.Integer, default = 0, nullable=False)
    asientoRel = db.relationship(lambda: Asientos, back_populates="adjuntos")

    def __init__(self, asiento, archivo, detalle, estado):
        """ Constructor de la clase AdjuntosAsientos. """
        self.asiento = asiento
        self.archivo = archivo
        self.detalle = detalle
        self.estado = estado

# Se pueden agregar más clases para definir otras tablas en la base de datos

with app.app_context():
    # Agrega los modelos a la instancia de MetaData de SQLAlchemy
    db.Model.metadata.create_all(db.engine, checkfirst=True)  # Verifica las relaciones antes de crear las tablas
    db.create_all()  # Crea todas las tablas en la base de datos



# Definición del esquema para la clase PlanDeCuentas
class PlanDeCuentasSchema(ma.Schema):
    """
    Esquema de la clase PlanDeCuentas.
    Este esquema define los campos que serán serializados/deserializados
    para la clase PlanDeCuentas.
    """
    class Meta:
        fields = ('id', 'codigo', 'nombre', 'descripcion', 'naturaleza', 'cuenta_padre_id', 'nivel')

PlanDeCuentas_schema = PlanDeCuentasSchema()  # Objeto para serializar/deserializar una cuenta
PlanDeCuentas_schemas = PlanDeCuentasSchema(many=True)  # Objeto para serializar/deserializar múltiples cuentas

# Definición del esquema para la clase Transacciones
class TransaccionesSchema(ma.Schema):
    """
    Esquema de la clase Transacciones.
    Este esquema define los campos que serán serializados/deserializados
    para la clase Transacciones.
    """
    cuentas = ma.Nested(PlanDeCuentasSchema(only=("nombre",)))
    class Meta:
        fields = ('id', 'asiento', 'movimiento', 'tc', 'cuenta', "cuentas", 'detalle', 'estado')

transacciones_schema = TransaccionesSchema()  # Objeto para serializar/deserializar una transaccion
transacciones_schemas = TransaccionesSchema(many=True)  # Objeto para serializar/deserializar múltiples transacciones

# Definición del esquema para la clase Asientos
class AsientosSchema(ma.Schema):
    """
    Esquema de la clase Asientos.
    Este esquema define los campos que serán serializados/deserializados
    para la clase Asientos y todas las transacciones asociadas.
    """
    transacciones = ma.Nested(TransaccionesSchema, many=True)
    adjuntos = ma.Nested(lambda: AdjuntosAsientosSchema, many=True)
    class Meta:
        fields = ("id", "fechaRegistro", "fechaMovimiento", "operacion", "detalle", "estado", "transacciones", "adjuntos")

asientos_schema = AsientosSchema()  # Objeto para serializar/deserializar un asiento
asientos_schemas = AsientosSchema(many=True)  # Objeto para serializar/deserializar múltiples asientos

# Definición del esquema para la clase Operaciones
class OperacionesSchema(ma.Schema):
    """
    Esquema de la clase Operaciones.
    Este esquema define los campos que serán serializados/deserializados
    para la clase Operaciones.
    """
    class Meta:
        fields = ('id', 'operador', 'detalle', 'empresa_id', 'estado')

Operaciones_schema = OperacionesSchema()  # Objeto para serializar/deserializar una operacion
Operaciones_schemas = OperacionesSchema(many=True)  # Objeto para serializar/deserializar múltiples Operaciones

# Definición del esquema para la clase Empresas
class EmpresasSchema(ma.Schema):
    """
    Esquema de la clase Empresas.
    Este esquema define los campos que serán serializados/deserializados
    para la clase Empresas.
    """
    class Meta:
        fields = ('id', 'nombre', 'estado')

Empresas_schema = EmpresasSchema()  # Objeto para serializar/deserializar una empresa
Empresas_schemas = EmpresasSchema(many=True)  # Objeto para serializar/deserializar múltiples Empresas

# Definición del esquema para enviar un Mayor
class MayorSchema(ma.Schema):
    """
    Esquema de un Mayor.
    Este esquema define los campos que serán serializados/deserializados
    """
    class Meta:
        fields = ('id', 'fechaRegistro', 'fechaMovimiento', 'asiento','operacion','movimiento','detalleAsiento','detalleTransaccion','cuenta')

Mayor_schema = MayorSchema()  # Objeto para serializar/deserializar un Mayor
Mayor_schemas = MayorSchema(many=True)  # Objeto para serializar/deserializar transacciones de un Mayor

# Definición del esquema para enviar un Mayor
class AdjuntosAsientosSchema(ma.Schema):
    """
    Esquema de un adjunto.
    Este esquema define los campos que serán serializados/deserializados
    """
    class Meta:
        fields = ('id', 'asiento', 'archivo','detalle','estado')

AdjuntosAsientos_schema = AdjuntosAsientosSchema()  # Objeto para serializar/deserializar
AdjuntosAsientos_schemas = AdjuntosAsientosSchema(many=True)  # Objeto para serializar/deserializar multiples
