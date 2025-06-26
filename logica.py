import itertools

class Evento:
    _id_counter = itertools.count() 

    def __init__(self, tipo, tiempo, id_cliente=None, id_reloj=None, datos_adicionales=None):
        self.tipo = tipo
        self.tiempo = tiempo
        self.id_evento = next(Evento._id_counter) 
        self.id_cliente = id_cliente
        self.id_reloj = id_reloj
        self.random_llegada = None
        self.random_llegada_que_lo_genero = None
        self.tiempo_entre_llegadas_que_lo_genero = None
        self.cliente_obj_being_served = None
        self.reloj_obj_being_repaired = None
        self.datos_adicionales = datos_adicionales if datos_adicionales is not None else {}


    def __lt__(self, other):
        if not isinstance(other, Evento):
            return NotImplemented
        if self.tiempo != other.tiempo:
            return self.tiempo < other.tiempo
        return self.id_evento < other.id_evento

    def __eq__(self, other):
        if not isinstance(other, Evento):
            return NotImplemented
        return (self.tiempo, self.id_evento) == (other.tiempo, other.id_evento)

    def __repr__(self):
        return f"Evento({self.tipo}, t={self.tiempo}, id={self.id_evento})"

