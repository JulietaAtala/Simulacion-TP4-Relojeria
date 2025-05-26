# cliente.py
class Cliente:
    def __init__(self, id_cliente, tiempo_llegada, tipo_cliente=None, tiempo_atencion=0, estado="En cola"):
        self.id_cliente = id_cliente
        self.tiempo_llegada = tiempo_llegada
        self.tipo_cliente = tipo_cliente
        self.tiempo_atencion = tiempo_atencion
        self.estado = estado
        self.reloj_a_entregar = False
        self.reloj_a_retirar = False
        self.random_tipo_cliente = None
        self.random_tiempo_atencion = None