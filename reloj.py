class Reloj:
    _id_counter = 0

    def __init__(self, estado="Pendiente de Reparacion"):
        Reloj._id_counter += 1
        self.id_reloj = Reloj._id_counter
        self.estado = estado
        self.tiempo_inicio_reparacion = 0
        self.tiempo_fin_reparacion = 0