# logica.py
class Evento:
    def __init__(self, tipo, tiempo, id_cliente=None, id_reloj=None):
        self.tipo = tipo
        self.tiempo = tiempo
        self.id_cliente = id_cliente
        self.id_reloj = id_reloj

    #def __lt__(self, other):
        #return self.tiempo < other.tiempo
    
