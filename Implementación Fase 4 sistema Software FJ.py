import logging
from abc import ABC, abstractmethod

# Configuración del archivo de registro de eventos y errores
logging.basicConfig(
    filename="eventos.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


# =====================================================================
# EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# =====================================================================
class ErrorSistema(Exception):
    """Excepción base para todos los errores controlados de Software FJ."""


class DatoInvalidoError(ErrorSistema):
    """Se lanza cuando un dato de entrada no cumple las reglas de validación."""


class ServicioNoDisponibleError(ErrorSistema):
    """Se lanza cuando un servicio no se encuentra disponible para reserva."""


class ErrorReserva(ErrorSistema):
    """Se lanza ante operaciones inválidas o fallos en el ciclo de una reserva."""


# =====================================================================
# CLASE ABSTRACTA BASE: ENTIDADES
# =====================================================================
class Entidades(ABC):
    def __init__(self, id: str, nombre: str):
        self._id = id
        self._nombre = nombre

    @property
    def id(self) -> str:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""


# =====================================================================
# CLASE CLIENTE (ENCAPSULACIÓN Y VALIDACIÓN ESTRICTA)
# =====================================================================
class Cliente(Entidades):
    def __init__(self, id: str, nombre: str, numero: str, correo: str):
        super().__init__(id, nombre)
        self._correo = correo
        self._numero = numero
        self.validar()

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def numero(self) -> str:
        return self._numero

    def validar(self) -> None:
        if not self._id or not str(self._id).strip():
            raise DatoInvalidoError("El ID del cliente no puede estar vacío")
        if not self._nombre or not self._nombre.strip():
            raise DatoInvalidoError("El nombre no puede estar vacío")
        if "@" not in self._correo or "." not in self._correo:
            raise DatoInvalidoError(f"Correo no válido: {self._correo}")
        if not self._numero.isdigit():
            raise DatoInvalidoError("El teléfono solo debe contener números")

    def describir(self) -> str:
        return f"Cliente {self._nombre} | correo: {self._correo} | tel: {self._numero}"


# =====================================================================
# CLASE ABSTRACTA: SERVICIO
# =====================================================================
class Servicio(Entidades):
    def __init__(self, id: str, nombre: str, precio_base: float, disponible: bool = True):
        super().__init__(id, nombre)
        self._precio_base = precio_base
        self._disponible = disponible
        self.validar()

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    def validar(self) -> None:
        if self._precio_base <= 0:
            raise DatoInvalidoError(f"Precio base no válido: {self._precio_base}")

    @abstractmethod
    def calcular_costo(self, horas: float, descuento: float = 0, impuesto: float = 0) -> float:
        """Calcula el costo total del servicio soportando sobrecarga por parámetros opcionales."""


# =====================================================================
# SERVICIOS ESPECIALIZADOS (HERENCIA Y POLIMORFISMO)
# =====================================================================
class ReservaSala(Servicio):
    TARIFAS = {(10, False): 35, (10, True): 40, (20, False): 45, (20, True): 50}

    def __init__(self, id: str, nombre: str, capacidad: int, proyector: bool = False):
        self._capacidad = capacidad
        self._proyector = proyector
        if (capacidad, proyector) not in self.TARIFAS:
            raise DatoInvalidoError("Capacidad válida: 10 o 20 personas")
        super().__init__(id, nombre, self.TARIFAS[(capacidad, proyector)])

    def validar(self) -> None:
        super().validar()
        if (self._capacidad, self._proyector) not in self.TARIFAS:
            raise DatoInvalidoError("Configuración de sala no permitida")

    def calcular_costo(self, horas: float, descuento: float = 0, impuesto: float = 0) -> float:
        if horas <= 0:
            raise DatoInvalidoError("Las horas deben ser mayores a 0")
        subtotal = self._precio_base * horas
        subtotal -= subtotal * descuento
        return subtotal + (subtotal * impuesto)

    def describir(self) -> str:
        extra = "con proyector" if self._proyector else "sin proyector"
        return f"Sala {self._nombre} ({self._capacidad} personas, {extra}) - ${self._precio_base}/hora"


class AlquilerEquipo(Servicio):
    SEGURO = 5

    def __init__(self, id: str, nombre: str, precio_hora: float, seguro: bool = False):
        self._seguro = seguro
        super().__init__(id, nombre, precio_hora)

    def validar(self) -> None:
        super().validar()
        if not isinstance(self._seguro, bool):
            raise DatoInvalidoError("El indicador de seguro debe ser booleano")

    def calcular_costo(self, horas: float, descuento: float = 0, impuesto: float = 0) -> float:
        if horas <= 0:
            raise DatoInvalidoError("Las horas de alquiler deben ser mayores a 0")
        subtotal = self._precio_base * horas
        subtotal -= subtotal * descuento
        total = subtotal + (subtotal * impuesto)
        if self._seguro:
            total += self.SEGURO
        return total

    def describir(self) -> str:
        info_seguro = "con seguro" if self._seguro else "sin seguro"
        return f"Equipo: {self._nombre} ({info_seguro}) - ${self._precio_base}/hora"


class Asesoria(Servicio):
    TARIFAS = {"junior": 40, "senior": 60}

    def __init__(self, id: str, nombre: str, nivel: str = "junior"):
        self._nivel = nivel.lower().strip()
        if self._nivel not in self.TARIFAS:
            raise DatoInvalidoError("Nivel válido: junior o senior")
        super().__init__(id, nombre, self.TARIFAS[self._nivel])

    def validar(self) -> None:
        super().validar()
        if self._nivel not in self.TARIFAS:
            raise DatoInvalidoError(f"Nivel de asesoría no válido: {self._nivel}")

    def calcular_costo(self, horas: float, descuento: float = 0, impuesto: float = 0) -> float:
        if horas <= 0:
            raise DatoInvalidoError("Las horas de asesoría deben ser mayores a 0")
        subtotal = self._precio_base * horas
        subtotal -= subtotal * descuento
        return subtotal + (subtotal * impuesto)

    def describir(self) -> str:
        return f"Asesoría {self._nombre} (nivel: {self._nivel}) - ${self._precio_base}/hora"


# =====================================================================
# CLASE RESERVA (GESTIÓN DE ESTADOS Y MANEJO AVANZADO DE EXCEPCIONES)
# =====================================================================
class Reserva:
    def __init__(self, id: str, cliente: Cliente, servicio: Servicio, horas: float):
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva necesita un cliente y un servicio válidos")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio {servicio.nombre} no está disponible")
        self.id = id
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "PENDIENTE"

    def confirmar(self) -> None:
        if self.estado != "PENDIENTE":
            raise ErrorReserva(f"No se puede confirmar una reserva en estado {self.estado}")
        self.estado = "CONFIRMADA"
        logging.info(f"Reserva {self.id} confirmada")

    def cancelar(self) -> None:
        if self.estado == "CANCELADA":
            raise ErrorReserva("La reserva ya estaba cancelada")
        self.estado = "CANCELADA"
        logging.info(f"Reserva {self.id} cancelada")

    def procesar(self, descuento: float = 0, impuesto: float = 0) -> float:
        """Calcula el costo y confirma la reserva usando try/except/else/finally y encadenamiento."""
        try:
            costo = self.servicio.calcular_costo(self.horas, descuento, impuesto)
        except DatoInvalidoError as e:
            raise ErrorReserva(f"No se pudo procesar la reserva {self.id}") from e
        else:
            self.confirmar()
            logging.info(f"Reserva {self.id} procesada. Costo: ${costo:,.2f}")
            return costo
        finally:
            logging.info(f"Intento de procesar la reserva {self.id} finalizado")


# =====================================================================
# SIMULACIÓN PRINCIPAL (12 OPERACIONES SIN BASE DE DATOS)
# =====================================================================
def main():
    clientes, servicios, reservas = [], [], []

    def intentar(descripcion: str, accion):
        """Ejecuta una operación y captura excepciones para mantener activo el sistema."""
        print(f"\n{descripcion}")
        try:
            resultado = accion()
            print("  OK:", resultado.describir() if hasattr(resultado, "describir") else resultado)
            logging.info(f"{descripcion}: OK")
            return resultado
        except ErrorSistema as e:
            causa = f" (causa: {e.__cause__})" if e.__cause__ else ""
            print(f"  ERROR: {e}{causa}")
            logging.error(f"{descripcion}: {e}{causa}")
        except Exception as e:
            print(f"  ERROR inesperado: {e}")
            logging.critical(f"{descripcion}: error inesperado {e}")

    c1 = intentar("1. Cliente válido", lambda: Cliente("1", "Ana", "3001234567", "ana@mail.com"))
    if c1:
        clientes.append(c1)

    intentar("2. Cliente con correo inválido", lambda: Cliente("2", "Luis", "3001234567", "luismail.com"))
    intentar("3. Cliente con teléfono con letras", lambda: Cliente("3", "Eva", "30a", "eva@mail.com"))

    s1 = intentar("4. Sala válida", lambda: ReservaSala("S1", "Norte", 20, True))
    if s1:
        servicios.append(s1)

    intentar("5. Sala con capacidad no permitida", lambda: ReservaSala("S2", "Sur", 15))
    intentar("6. Equipo con precio negativo", lambda: AlquilerEquipo("E1", "Portátil", -10))

    s2 = intentar("7. Equipo válido con seguro", lambda: AlquilerEquipo("E2", "Proyector 4K", 25, True))
    if s2:
        servicios.append(s2)

    s3 = intentar("8. Asesoría válida", lambda: Asesoria("A1", "Python", "senior"))
    if s3:
        servicios.append(s3)

    def reserva_ok():
        r = Reserva("R1", c1, s1, 3)
        costo = r.procesar(descuento=0.1, impuesto=0.19)
        reservas.append(r)
        return f"{r.id} {r.estado} - costo ${costo:,.2f}"

    intentar("9. Reserva exitosa (10% desc., 19% IVA)", reserva_ok)
    intentar("10. Reserva con 0 horas", lambda: Reserva("R2", c1, s3, 0).procesar())

    def cancelar():
        r = reservas[0]
        r.cancelar()
        return f"{r.id} {r.estado}"

    intentar("11. Cancelar reserva", cancelar)
    intentar("12. Confirmar reserva ya cancelada", lambda: reservas[0].confirmar())

    print(f"\nResumen: {len(clientes)} clientes, {len(servicios)} servicios, {len(reservas)} reservas.")
    print("Revisa el archivo eventos.log")


if __name__ == "__main__":
    main()