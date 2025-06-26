from collections import deque
from empleado import Empleado
from reloj import Reloj 

class Relojeria:
    def __init__(self, num_relojes_iniciales_para_retiro=3):
        self.ayudante = Empleado(id_empleado=1, tipo_empleado="Ayudante")
        self.relojero = Empleado(id_empleado=2, tipo_empleado="Relojero")
        self.cola_clientes = deque()
        self.cola_relojes_a_reparar = deque()

        self.relojes_reparados = []
        for _ in range(num_relojes_iniciales_para_retiro):
            self.relojes_reparados.append(Reloj(estado="Reparado"))

        self.clientes_en_sistema = {}

        self.acum_clientes_retiran_no_listos = 0
        self.tiempo_ocio_ayudante = 0
        self.tiempo_ocio_relojero = 0
        self.max_cola_clientes = 0
        self.clientes_atendidos_ayudante = 0
        self.reparaciones_realizadas_relojero = 0
        self.tiempo_total_simulacion = 0

        self.ultimo_tiempo_ayudante_libre = 0
        self.ultimo_tiempo_relojero_libre = 0
        self.total_clientes_tipo_retirar_que_llegaron = 0