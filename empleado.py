class Empleado:
    def __init__(self, id_empleado, tipo_empleado, estado="Libre", tiempo_ocupado_acumulado=0, tiempo_fin_tarea=0):
        self.id_empleado = id_empleado
        self.tipo_empleado = tipo_empleado
        self.estado = estado
        self.tiempo_ocupado_acumulado = tiempo_ocupado_acumulado
        self.tiempo_fin_tarea = tiempo_fin_tarea
        self.random_tiempo_tarea = None