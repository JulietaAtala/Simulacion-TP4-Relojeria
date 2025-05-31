import itertools

class Evento:
    _id_counter = itertools.count() # Class variable to generate unique IDs

    def __init__(self, tipo, tiempo, id_cliente=None, id_reloj=None, datos_adicionales=None):
        self.tipo = tipo
        self.tiempo = tiempo
        self.id_evento = next(Evento._id_counter) # Assign a unique ID
        self.id_cliente = id_cliente
        self.id_reloj = id_reloj
        self.random_llegada = None
        self.cliente_obj_being_served = None
        self.reloj_obj_being_repaired = None
        # ... (otros atributos que puedas tener) ...
        self.datos_adicionales = datos_adicionales if datos_adicionales is not None else {}


    # Implement __lt__ (less than) for heapq comparison
    def __lt__(self, other):
        if not isinstance(other, Evento):
            return NotImplemented
        # Primary sort by time
        if self.tiempo != other.tiempo:
            return self.tiempo < other.tiempo
        # Secondary sort by unique event ID as a tie-breaker
        return self.id_evento < other.id_evento

    # (Opcional pero recomendado) Implementa __eq__ (equals) si es relevante
    def __eq__(self, other):
        if not isinstance(other, Evento):
            return NotImplemented
        return (self.tiempo, self.id_evento) == (other.tiempo, other.id_evento)

    def __repr__(self):
        return f"Evento({self.tipo}, t={self.tiempo}, id={self.id_evento})"

