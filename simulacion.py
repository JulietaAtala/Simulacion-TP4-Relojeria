import random
import math
from collections import deque
import sys
import heapq # ¡Importar heapq!

# Importar clases necesarias de sus respectivos módulos
from logica import Evento
from cliente import Cliente
from empleado import Empleado
from reloj import Reloj
from relojeria_state import Relojeria 

class Simulacion:
    # Se actualiza __init__ para aceptar todos los nuevos parámetros parametrizables
    def __init__(self, tiempo_simulacion_max, iteraciones_max, 
                 tll_params, prob_cliente_params, venta_params, atencion_fija, 
                 reparacion_params, orden_relojero, relojes_iniciales):
        
        self.tiempo_simulacion_max = tiempo_simulacion_max
        self.iteraciones_max = iteraciones_max
        self.reloj_anterior = 0
        self.reloj = 0
        self.iteracion = 0
        self.eventos = [] # ¡Ahora será una cola de prioridad gestionada por heapq!
        self.cantidadClientes = 0
        
        # Almacenar los valores parametrizables como atributos de la instancia
        self.tll_min, self.tll_max = tll_params
        self.prob_comprar, self.prob_entregar, self.prob_retirar = prob_cliente_params
        self.venta_min, self.venta_max = venta_params
        self.atencion_fija = atencion_fija
        self.reparacion_min, self.reparacion_max = reparacion_params
        self.orden_relojero_tiempo = orden_relojero # Renombrado para evitar conflicto con método
        self.relojes_iniciales = relojes_iniciales # Almacenar el número de relojes iniciales

        # Inicializar Relojeria con el número parametrizable de relojes iniciales
        self.relojeria = Relojeria(num_relojes_iniciales_para_retiro=self.relojes_iniciales) 
        
        self.id_proximo_cliente = 1 # Contador para IDs de clientes
        self.resultados_vector_estado = [] # Para almacenar cada fila del vector de estado
        self.full_simulation_rows = [] # Almacena (lista_valores_fila, lista_tags) para todas las filas

        # Atributos para mantener los próximos tiempos de fin de tarea para la visualización
        self.next_fin_atencion_ayudante_display_time = None # MODIFICACIÓN: Nuevo atributo para persistir el tiempo de fin de atención del ayudante
        self.next_fin_reparacion_relojero_display_time = None # MODIFICACIÓN: Nuevo atributo para persistir el tiempo de fin de reparación del relojero
        self.next_fin_limpieza_relojero_display_time = None # MODIFICACIÓN: Nuevo atributo para persistir el tiempo de fin de limpieza del relojero

        # Inicializar el primer evento de llegada
        # Esta llamada añadirá el primer evento "Llegada Cliente" a self.eventos
        self.generar_proxima_llegada()
        print(f"DEBUG: [Simulacion.__init__] Eventos iniciales en la lista: {[e.tipo for e in self.eventos]}")


    # Se usan los valores parametrizables en las funciones de generación
    def generar_tiempo_entre_llegadas(self):
        """Genera un tiempo entre llegadas para clientes según U(tll_min, tll_max) minutos."""
        rnd = random.random()
        tiempo_entre_llegadas = self.tll_min + rnd * (self.tll_max - self.tll_min)
        return tiempo_entre_llegadas, rnd

    # Se usan las probabilidades parametrizables
    def generar_tipo_cliente(self):
        """Determina el tipo de cliente (Comprar, Entregar, Retirar) basado en probabilidades parametrizables."""
        rnd = random.random()
        if rnd < self.prob_comprar:
            return "Comprar", rnd
        elif rnd < (self.prob_comprar + self.prob_entregar):
            return "Entregar", rnd
        else:
            return "Retirar", rnd

    # Se usan los tiempos de venta y atención fijos parametrizables
    def generar_tiempo_atencion_ayudante(self, tipo_cliente):
        """Genera el tiempo de atención del ayudante según el tipo de cliente y parámetros."""
        if tipo_cliente == "Comprar":
            rnd = random.random()
            tiempo_atencion = self.venta_min + rnd * (self.venta_max - self.venta_min)
            return tiempo_atencion, rnd
        else: # "Entregar" o "Retirar"
            return self.atencion_fija, None # Usar el tiempo de atención fijo parametrizable

    # Se usan los tiempos de reparación parametrizables
    def generar_tiempo_reparacion_relojero(self):
        """Genera el tiempo de reparación del relojero según U(reparacion_min, reparacion_max) minutos."""
        rnd = random.random()
        tiempo_reparacion = self.reparacion_min + rnd * (self.reparacion_max - self.reparacion_min)
        return tiempo_reparacion, rnd

    def generar_proxima_llegada(self):
        """Programa el próximo evento de llegada y lo añade a la cola de prioridad."""
        tiempo_entre_llegadas, rnd_llegada = self.generar_tiempo_entre_llegadas()
        proxima_llegada_tiempo = self.reloj + tiempo_entre_llegadas
        
        if proxima_llegada_tiempo <= self.tiempo_simulacion_max:
            evento = Evento(tipo="Llegada Cliente", tiempo=proxima_llegada_tiempo)
            evento.random_llegada = rnd_llegada 
            evento.tiempo_entre_llegadas_generado = tiempo_entre_llegadas 
            heapq.heappush(self.eventos, evento) # ¡Usar heappush!
            print(f"DEBUG: [generar_proxima_llegada] Evento programado {evento.tipo} en {evento.tiempo:.2f}. Eventos ahora: {[e.tipo for e in self.eventos]}") # FIX: Corrected f-string syntax
        else:
            print(f"DEBUG: [generar_proxima_llegada] No hay más llegadas programadas más allá de {self.tiempo_simulacion_max:.2f}")

    def procesar_llegada_cliente(self, evento_actual):
        """Procesa un evento de llegada de cliente."""
        id_cliente = self.id_proximo_cliente
        self.id_proximo_cliente += 1
        self.cantidadClientes += 1
        
        tipo_cliente, rnd_tipo_cliente = self.generar_tipo_cliente()
        
        cliente = Cliente(id_cliente, evento_actual.tiempo, tipo_cliente, estado="Esperando") 
        cliente.random_tipo_cliente = rnd_tipo_cliente 

        if tipo_cliente == "Entregar":
            cliente.reloj_a_entregar = True
        elif tipo_cliente == "Retirar":
            cliente.reloj_a_retirar = True
            self.relojeria.total_clientes_tipo_retirar_que_llegaron += 1 

        self.relojeria.clientes_en_sistema[id_cliente] = cliente 

        if self.relojeria.ayudante.estado == "Libre":
            self.relojeria.tiempo_ocio_ayudante += (self.reloj - self.relojeria.ultimo_tiempo_ayudante_libre) 

            cliente.estado = "Siendo Atendido" 
            self.relojeria.ayudante.estado = "Ocupado"
            self.relojeria.ayudante.cliente_actual = cliente 

            tiempo_atencion, rnd_atencion = self.generar_tiempo_atencion_ayudante(cliente.tipo_cliente)
            cliente.tiempo_atencion = tiempo_atencion 
            cliente.random_tiempo_atencion = rnd_atencion 
            
            self.relojeria.ayudante.random_tiempo_tarea = rnd_atencion 
            self.relojeria.ayudante.tiempo_fin_tarea = self.reloj + tiempo_atencion
            cliente.fin_atencion_programado = self.relojeria.ayudante.tiempo_fin_tarea

            evento = Evento(tipo="Fin Atencion Ayudante", tiempo=self.relojeria.ayudante.tiempo_fin_tarea, id_cliente=cliente.id_cliente)
            evento.cliente_obj_being_served = cliente 
            heapq.heappush(self.eventos, evento) # ¡Usar heappush!
            self.next_fin_atencion_ayudante_display_time = evento.tiempo # MODIFICACIÓN: Actualizar el tiempo para la visualización
        else:
            cliente.estado = "En cola" 
            self.relojeria.cola_clientes.append(cliente) 

            if len(self.relojeria.cola_clientes) > self.relojeria.max_cola_clientes:
                self.relojeria.max_cola_clientes = len(self.relojeria.cola_clientes)

        # Programar la próxima llegada después de procesar la actual
        self.generar_proxima_llegada()


    def intentar_atender_cliente(self):
        """Intenta que el ayudante atienda a un cliente si está libre y hay clientes en cola."""
        if self.relojeria.ayudante.estado == "Libre" and self.relojeria.cola_clientes:
            self.relojeria.tiempo_ocio_ayudante += (self.reloj - self.relojeria.ultimo_tiempo_ayudante_libre)

            cliente_atendiendo = self.relojeria.cola_clientes.popleft()
            
            tiempo_atencion, rnd_atencion = self.generar_tiempo_atencion_ayudante(cliente_atendiendo.tipo_cliente)
            
            cliente_atendiendo.tiempo_atencion = tiempo_atencion
            cliente_atendiendo.random_tiempo_atencion = rnd_atencion
            cliente_atendiendo.estado = "Siendo Atendido"

            self.relojeria.ayudante.estado = "Ocupado"
            self.relojeria.ayudante.cliente_actual = cliente_atendiendo
            self.relojeria.ayudante.random_tiempo_tarea = rnd_atencion
            self.relojeria.ayudante.tiempo_fin_tarea = self.reloj + tiempo_atencion

            cliente_atendiendo.fin_atencion_programado = self.relojeria.ayudante.tiempo_fin_tarea

            evento = Evento(tipo="Fin Atencion Ayudante", tiempo=self.relojeria.ayudante.tiempo_fin_tarea, id_cliente=cliente_atendiendo.id_cliente)
            evento.cliente_obj_being_served = cliente_atendiendo
            heapq.heappush(self.eventos, evento) # ¡Usar heappush!
            self.next_fin_atencion_ayudante_display_time = evento.tiempo # MODIFICACIÓN: Actualizar el tiempo para la visualización

    def procesar_fin_atencion_ayudante(self, evento_actual):
        """Procesa un evento de fin de atención del ayudante."""
        cliente_atendido = evento_actual.cliente_obj_being_served

        cliente_atendido.estado = "Atendido"
        self.relojeria.ayudante.estado = "Libre"
        self.relojeria.ayudante.cliente_actual = None
        
        #self.relojeria.ayudante.tiempo_ocupado_acumulado += cliente_atendido.tiempo_atencion
        self.relojeria.clientes_atendidos_ayudante += 1
        self.relojeria.ultimo_tiempo_ayudante_libre = evento_actual.tiempo

        client_departed_flag = False
        if cliente_atendido.tipo_cliente == "Entregar":
            reloj_nuevo = Reloj(estado="Pendiente de Reparacion")
            self.relojeria.cola_relojes_a_reparar.append(reloj_nuevo)
            del self.relojeria.clientes_en_sistema[cliente_atendido.id_cliente]
            client_departed_flag = True
            self.intentar_reparar_reloj()
        elif cliente_atendido.tipo_cliente == "Retirar":
            reloj_encontrado = None
            for reloj in self.relojeria.relojes_reparados:
                if reloj.estado == "Reparado":
                    reloj_encontrado = reloj
                    break

            if reloj_encontrado:
                reloj_encontrado.estado = "Retirado"
                self.relojeria.relojes_reparados.remove(reloj_encontrado)
            else:
                self.relojeria.acum_clientes_retiran_no_listos += 1
            del self.relojeria.clientes_en_sistema[cliente_atendido.id_cliente]
            client_departed_flag = True
        elif cliente_atendido.tipo_cliente == "Comprar":
            del self.relojeria.clientes_en_sistema[cliente_atendido.id_cliente]
            client_departed_flag = True

        evento_actual.client_departed = client_departed_flag
        evento_actual.client_finished_id = cliente_atendido.id_cliente
        evento_actual.client_finished_state = "Se Fue"

        self.intentar_atender_cliente()

    def intentar_reparar_reloj(self):
        """Intenta que el relojero repare un reloj si está libre y hay relojes en cola."""
        if self.relojeria.relojero.estado == "Libre" and self.relojeria.cola_relojes_a_reparar:
            self.relojeria.tiempo_ocio_relojero += (self.reloj - self.relojeria.ultimo_tiempo_relojero_libre)

            reloj_a_reparar = self.relojeria.cola_relojes_a_reparar.popleft()
            reloj_a_reparar.estado = "En Reparacion"
            reloj_a_reparar.tiempo_inicio_reparacion = self.reloj 

            tiempo_reparacion, rnd_reparacion = self.generar_tiempo_reparacion_relojero()
            
            self.relojeria.relojero.estado = "Ocupado"
            self.relojeria.relojero.random_tiempo_tarea = rnd_reparacion
            self.relojeria.relojero.tiempo_fin_tarea = self.reloj + tiempo_reparacion

            evento = Evento(tipo="Fin Reparacion Relojero", tiempo=self.relojeria.relojero.tiempo_fin_tarea, id_reloj=reloj_a_reparar.id_reloj)
            evento.reloj_obj_being_repaired = reloj_a_reparar
            heapq.heappush(self.eventos, evento) # ¡Usar heappush!
            self.next_fin_reparacion_relojero_display_time = evento.tiempo # MODIFICACIÓN: Actualizar el tiempo para la visualización

    # Se usa el tiempo de limpieza parametrizable (orden_relojero_tiempo)
    def procesar_fin_reparacion_relojero(self, evento_actual):
        """Procesa un evento de fin de reparación del relojero."""
        reloj_reparado = evento_actual.reloj_obj_being_repaired 
        
        # --- IMPRESIONES DE DEPURACIÓN para tiempo de reparación negativo ---
        if reloj_reparado is None:
            print(f"DEBUG ERROR: El objeto Reloj es None en el evento Fin Reparacion Relojero en {evento_actual.tiempo}")
            return 
        
        reloj_reparado.estado = "Reparado"
        reloj_reparado.tiempo_fin_reparacion = evento_actual.tiempo 

        duration = reloj_reparado.tiempo_fin_reparacion - reloj_reparado.tiempo_inicio_reparacion
        print(f"DEBUG RELOJERO: ------------------- !")
        print(f"DEBUG RELOJERO: Importante FIN {reloj_reparado.tiempo_fin_reparacion}!")
        print(f"DEBUG RELOJERO: Importante INICIO {reloj_reparado.tiempo_inicio_reparacion}!")
        
        if duration < 0:
            print(f"DEBUG ERROR: Duración de reparación negativa para Reloj ID {reloj_reparado.id_reloj}!")
            print(f"   Duración: {duration:.2f}, Inicio: {reloj_reparado.tiempo_inicio_reparacion:.2f}, Fin: {evento_actual.tiempo:.2f}")

        #self.relojeria.relojero.tiempo_ocupado_acumulado += duration
        self.relojeria.reparaciones_realizadas_relojero += 1

        self.relojeria.relojero.estado = "Limpiando"
        tiempo_limpieza = self.orden_relojero_tiempo 
        self.relojeria.relojero.tiempo_fin_tarea = self.reloj + tiempo_limpieza

        self.relojeria.relojes_reparados.append(reloj_reparado)

        evento = Evento(tipo="Fin Limpieza Relojero", tiempo=self.relojeria.relojero.tiempo_fin_tarea)
        heapq.heappush(self.eventos, evento) # ¡Usar heappush!
        self.next_fin_limpieza_relojero_display_time = evento.tiempo # MODIFICACIÓN: Actualizar el tiempo para la visualización

    def procesar_fin_limpieza_relojero(self, evento_actual):
        """Procesa un evento de fin de limpieza del relojero."""
        self.relojeria.relojero.estado = "Libre"
        self.relojeria.relojero.tiempo_ocupado_acumulado += self.orden_relojero_tiempo 
        self.relojeria.ultimo_tiempo_relojero_libre = evento_actual.tiempo

        self.intentar_reparar_reloj()
    
    def obtener_proxima_llegada(self):
        for e in heapq.nsmallest(len(self.eventos), self.eventos):
            if e.tipo == "Llegada Cliente":
                return e
        return None

    # Se actualiza la firma de execute_simulacion
    def ejecutar_simulacion(self, iteraciones_a_mostrar, hora_desde_mostrar): 
        # tiempo_simulacion_max e iteraciones_max son ahora atributos de __init__ (self.tiempo_simulacion_max, self.iteraciones_max)
        
        self.reloj = 0
        self.iteracion = 0
        self.eventos = [] # ¡Asegurarse de que esté vacío al reiniciar!
        # Reinicializar Relojeria con el número parametrizable de relojes iniciales para cada ejecución de simulación
        self.relojeria = Relojeria(num_relojes_iniciales_para_retiro=self.relojes_iniciales) 
        self.id_proximo_cliente = 1
        self.resultados_vector_estado = []
        self.full_simulation_rows = [] # Reiniciar para una nueva ejecución

        Reloj._id_counter = 0 

        # Reiniciar los tiempos de visualización al inicio de cada simulación
        self.next_fin_atencion_ayudante_display_time = None
        self.next_fin_reparacion_relojero_display_time = None
        self.next_fin_limpieza_relojero_display_time = None

        # Generar el primer evento de llegada
        self.generar_proxima_llegada()
        
        print(f"DEBUG: [ejecutar_simulacion] Eventos iniciales en la lista después de la primera generación: {[e.tipo for e in self.eventos]}")

        max_columnas_clientes = 100  
        headers = [
            "Fila", "Reloj", "Evento", "RND Llegada", "Tiempo entre llegadas", "Proxima llegada",
            "RND Tipo Cliente", "Tipo Cliente", "RND Atencion Ayudante", "Tiempo Atencion Ayudante", "Fin Atencion Ayudante",
            "RND Reparacion Relojero", "Tiempo Reparacion Relojero", "Fin Reparacion Relojero", "Fin Limpieza Relojero",
            "Estado Ayudante", "Cola Clientes", "Estado Relojero", "Cola Relojes a Reparar", "Relojes Espera Retiro",
            "Acum. Clientes Retiran", "Acum. Clientes Retiran No Listos", "Acum. Tiempo Ocup Ayudante", "Acum. Tiempo Ocup Relojero",
            "Cont. Clientes", "Cont. Reparaciones", "Porc. Ocup. Ayudante", "Porc. Ocup. Relojero", "Cola Max. Clientes",
            "Cliente Evento ID", "Estado Cliente Evento"
        ]
        
        headers += [f"C {i+1}" for i in range(max_columnas_clientes)]
        # Añadir encabezados como la primera fila para full_simulation_rows (para exportación CSV)
        self.full_simulation_rows.append((headers, []))


        num_displayed_rows = 0

        # Persistent dictionary to track current display state of each client.
        # This will be updated based on events and then used to populate the C1, C2, C3... columns.
        # Initialize all client columns as empty.
        clientes_estado_para_fila = {i+1: "" for i in range(max_columnas_clientes)} 


        while self.eventos and self.reloj <= self.tiempo_simulacion_max and self.iteracion < self.iteraciones_max:
            print(f"DEBUG: [ejecutar_simulacion] Iteración {self.iteracion}, Reloj {self.reloj:.2f}. Eventos antes de pop: {[e.tipo for e in self.eventos]}")
            self.iteracion += 1
            evento_actual = heapq.heappop(self.eventos) # ¡Usar heappop para obtener el evento más próximo!
            print(f"---------------------------------------------!")
            print(f"DEBUG RELOJ ANTES {self.reloj}!")
            print(f"DEBUG AYUDANTE ANTES {self.relojeria.ayudante.estado}!")
            self.reloj_anterior = self.reloj
            self.reloj = evento_actual.tiempo
            if self.relojeria.ayudante.estado == 'Ocupado':
                self.relojeria.ayudante.tiempo_ocupado_acumulado += self.reloj - self.reloj_anterior
            if self.relojeria.relojero.estado == 'Ocupado':
                self.relojeria.relojero.tiempo_ocupado_acumulado += self.reloj - self.reloj_anterior
            print(f"DEBUG RELOJ DESPUES {self.reloj}!")
            print(f"DEBUG AYUDANTE DESPUES {self.relojeria.ayudante.estado}!")
            print(f"---------------------------------------------!")
            
            print(f"DEBUG: [ejecutar_simulacion] Evento sacado {evento_actual.tipo} en {evento_actual.tiempo:.2f}. Eventos después de pop: {[e.tipo for e in self.eventos]}")

            row_data = {header: "" for header in headers} 
            row_data["Fila"] = self.iteracion
            row_data["Reloj"] = f"{self.reloj:.2f}"
            row_data["Evento"] = evento_actual.tipo

            current_row_tags = [] 

            # MODIFICACIÓN: Populate persistent "Fin Atencion/Reparacion/Limpieza" times before event processing
            # These values will persist unless explicitly updated by the event processing.
            if self.next_fin_atencion_ayudante_display_time is not None and self.next_fin_atencion_ayudante_display_time >= self.reloj:
                row_data["Fin Atencion Ayudante"] = f"{self.next_fin_atencion_ayudante_display_time:.2f}"
            else:
                self.next_fin_atencion_ayudante_display_time = None # Clear if time has passed or not scheduled

            if self.next_fin_reparacion_relojero_display_time is not None and self.next_fin_reparacion_relojero_display_time >= self.reloj:
                row_data["Fin Reparacion Relojero"] = f"{self.next_fin_reparacion_relojero_display_time:.2f}"
            else:
                self.next_fin_reparacion_relojero_display_time = None # Clear if time has passed or not scheduled
            
            if self.next_fin_limpieza_relojero_display_time is not None and self.next_fin_limpieza_relojero_display_time >= self.reloj:
                row_data["Fin Limpieza Relojero"] = f"{self.next_fin_limpieza_relojero_display_time:.2f}"
            else:
                self.next_fin_limpieza_relojero_display_time = None # Clear if time has passed or not scheduled

            if evento_actual.tipo == "Llegada Cliente":
                row_data["RND Llegada"] = f"{evento_actual.random_llegada:.4f}"
                row_data["Tiempo entre llegadas"] = f"{evento_actual.tiempo_entre_llegadas_generado:.2f}"
                
                self.procesar_llegada_cliente(evento_actual) # This might set next_fin_atencion_ayudante_display_time
                
                next_llegada_event_in_list = None
                for e in heapq.nsmallest(len(self.eventos), self.eventos):
                    if e.tipo == "Llegada Cliente":
                        next_llegada_event_in_list = e
                        break

                if next_llegada_event_in_list:
                    row_data["Proxima llegada"] = f"{next_llegada_event_in_list.tiempo:.2f}"
                else:
                    row_data["Proxima llegada"] = "N/A"
                
                current_client_id = self.id_proximo_cliente - 1 
                client_just_processed = self.relojeria.clientes_en_sistema.get(current_client_id)
                if client_just_processed:
                    row_data["RND Tipo Cliente"] = f"{client_just_processed.random_tipo_cliente:.4f}"
                    row_data["Tipo Cliente"] = client_just_processed.tipo_cliente
                    row_data["Cliente Evento ID"] = client_just_processed.id_cliente
                    row_data["Estado Cliente Evento"] = client_just_processed.estado 
                    if client_just_processed.estado == "Siendo Atendido":
                        rnd_val = client_just_processed.random_tiempo_atencion
                        row_data["RND Atencion Ayudante"] = f"{rnd_val:.4f}" if rnd_val is not None else ""
                        row_data["Tiempo Atencion Ayudante"] = f"{client_just_processed.tiempo_atencion:.2f}"
                        # The self.next_fin_atencion_ayudante_display_time would have been set in procesar_llegada_cliente
                        # or intentar_atender_cliente if a client started being attended.
                        # MODIFICACIÓN: Asegurarse que se muestre el valor actual si se acaba de programar
                        row_data["Fin Atencion Ayudante"] = f"{self.next_fin_atencion_ayudante_display_time:.2f}" if self.next_fin_atencion_ayudante_display_time is not None else ""


            elif evento_actual.tipo == "Fin Atencion Ayudante":
                # MODIFICACIÓN: Clear the scheduled time as this event is now happening (for the *previous* client)
                self.next_fin_atencion_ayudante_display_time = None 

                self.procesar_fin_atencion_ayudante(evento_actual) # This might schedule a new Fin Atencion Ayudante event

                next_llegada_event = self.obtener_proxima_llegada()
                if next_llegada_event:
                    row_data["Proxima llegada"] = f"{next_llegada_event.tiempo:.2f}"
                else:
                    row_data["Proxima llegada"] = "N/A"

                # MODIFICACIÓN: If a new client is being attended immediately after the previous one left,
                # update the "Fin Atencion Ayudante" for the new client.
                cliente_que_inicia_atencion = self.relojeria.ayudante.cliente_actual
                if cliente_que_inicia_atencion:
                    # This new 'fin' time is what should persist in future rows
                    self.next_fin_atencion_ayudante_display_time = cliente_que_inicia_atencion.fin_atencion_programado
                    row_data["RND Atencion Ayudante"] = f"{cliente_que_inicia_atencion.random_tiempo_atencion:.4f}" if cliente_que_inicia_atencion.random_tiempo_atencion is not None else ""
                    row_data["Tiempo Atencion Ayudante"] = f"{cliente_que_inicia_atencion.tiempo_atencion:.2f}"
                    row_data["Fin Atencion Ayudante"] = f"{cliente_que_inicia_atencion.fin_atencion_programado:.2f}"
                else: # No new client started being attended, clear the displayed fin attention
                    self.next_fin_atencion_ayudante_display_time = None
                    row_data["Fin Atencion Ayudante"] = "" # Explicitly clear for this row if no new client

                # Show the ID of the client who *just finished* their service in this row.
                row_data["Cliente Evento ID"] = evento_actual.client_finished_id
                row_data["Estado Cliente Evento"] = evento_actual.client_finished_state

                if hasattr(evento_actual, 'client_departed') and evento_actual.client_departed:
                    current_row_tags.append("Departed") 
                
            elif evento_actual.tipo == "Fin Reparacion Relojero":
                # MODIFICACIÓN: Clear the scheduled time as this event is now happening
                self.next_fin_reparacion_relojero_display_time = None

                reloj_obj_finished = evento_actual.reloj_obj_being_repaired 
                if reloj_obj_finished:
                    row_data["RND Reparacion Relojero"] = f"{self.relojeria.relojero.random_tiempo_tarea:.4f}" if self.relojeria.relojero.random_tiempo_tarea is not None else ""
                    
                    repair_duration = evento_actual.tiempo - reloj_obj_finished.tiempo_inicio_reparacion
                    
                    if repair_duration < 0:
                        print(f"DEBUG DISPLAY ERROR: Duración de visualización negativa para Reloj ID {reloj_obj_finished.id_reloj}!")
                        print(f"   Duración: {repair_duration:.2f}, Inicio: {reloj_obj_finished.tiempo_inicio_reparacion:.2f}, Fin: {evento_actual.tiempo:.2f}")

                    row_data["Tiempo Reparacion Relojero"] = f"{repair_duration:.2f}"
                row_data["Fin Reparacion Relojero"] = f"{evento_actual.tiempo:.2f}" # This is the *actual* finish time

                self.procesar_fin_reparacion_relojero(evento_actual) # This will schedule Fin Limpieza Relojero
                
                # MODIFICACIÓN: Update the persistent display time for cleaning
                if self.relojeria.relojero.estado == "Limpiando":
                    row_data["Fin Limpieza Relojero"] = f"{self.relojeria.relojero.tiempo_fin_tarea:.2f}"
                    self.next_fin_limpieza_relojero_display_time = self.relojeria.relojero.tiempo_fin_tarea


            elif evento_actual.tipo == "Fin Limpieza Relojero":
                # MODIFICACIÓN: Clear the scheduled time as this event is now happening
                self.next_fin_limpieza_relojero_display_time = None

                row_data["Fin Limpieza Relojero"] = f"{evento_actual.tiempo:.2f}" # This is the *actual* finish time
                
                self.procesar_fin_limpieza_relojero(evento_actual)
            
            # --- Common updates for all events ---
            # Update 'Proxima llegada' after potentially generating a new one
            next_llegada_event = self.obtener_proxima_llegada()
            if next_llegada_event:
                row_data["Proxima llegada"] = f"{next_llegada_event.tiempo:.2f}"
            else:
                row_data["Proxima llegada"] = "N/A"

            row_data["Estado Ayudante"] = self.relojeria.ayudante.estado
            row_data["Cola Clientes"] = len(self.relojeria.cola_clientes)
            row_data["Estado Relojero"] = self.relojeria.relojero.estado
            row_data["Cola Relojes a Reparar"] = len(self.relojeria.cola_relojes_a_reparar)
            row_data["Relojes Espera Retiro"] = len(self.relojeria.relojes_reparados)
            
            #Agrege la row de abajo pero no me la esta agregando
            row_data["Acum. Clientes Retiran"] = self.relojeria.total_clientes_tipo_retirar_que_llegaron
            row_data["Acum. Clientes Retiran No Listos"] = self.relojeria.acum_clientes_retiran_no_listos

            row_data["Acum. Tiempo Ocup Ayudante"] = f"{self.relojeria.ayudante.tiempo_ocupado_acumulado:.2f}"
            row_data["Acum. Tiempo Ocup Relojero"] = f"{self.relojeria.relojero.tiempo_ocupado_acumulado:.2f}"

            row_data["Cont. Clientes"] = self.id_proximo_cliente - 1
            row_data["Cont. Reparaciones"] = self.relojeria.reparaciones_realizadas_relojero
            row_data["Cola Max. Clientes"] = self.relojeria.max_cola_clientes

            row_data["Porc. Ocup. Ayudante"] = ""
            row_data["Porc. Ocup. Relojero"] = ""
            
            # Reset clientes_estado_para_fila for this row
            for client_id in clientes_estado_para_fila:
                clientes_estado_para_fila[client_id] = ""

            # Populate based on current clients in system
            for cliente in self.relojeria.clientes_en_sistema.values():
                if cliente.id_cliente <= max_columnas_clientes:
                    estado_str = f"{cliente.tipo_cliente}-{cliente.estado}"
                    clientes_estado_para_fila[cliente.id_cliente] = estado_str

            # Add columns for each client (from 1 to max_columnas_clientes)
            for i in range(max_columnas_clientes):
                row_data[f"C {i+1}"] = clientes_estado_para_fila.get(i+1, "")

            # Special handling for a client who just departed in THIS row's event
            if evento_actual.tipo == "Fin Atencion Ayudante" and \
               hasattr(evento_actual, 'client_finished_id') and \
               evento_actual.client_finished_id is not None and \
               evento_actual.client_finished_id <= max_columnas_clientes:
                # This ensures "Se Fue" overrides any subsequent state for this *specific* client in this *specific* row
                row_data[f"C {evento_actual.client_finished_id}"] = "Se Fue"


            ordered_row = [row_data[header] for header in headers]
            self.full_simulation_rows.append((ordered_row, current_row_tags))

            if self.reloj >= hora_desde_mostrar and num_displayed_rows < iteraciones_a_mostrar:
                self.resultados_vector_estado.append(ordered_row) 
                num_displayed_rows += 1
            
        self.relojeria.tiempo_total_simulacion = self.reloj

        total_tiempo_simulado = self.reloj
        
        porc_ocup_ayudante = 0
        if total_tiempo_simulado > 0:
            tiempo_ocup_ayudante = self.relojeria.ayudante.tiempo_ocupado_acumulado
            porc_ocup_ayudante = (tiempo_ocup_ayudante / total_tiempo_simulado) * 100

        porc_ocup_relojero = 0
        if total_tiempo_simulado > 0:
            tiempo_ocup_relojero = self.relojeria.relojero.tiempo_ocupado_acumulado
            porc_ocup_relojero = (tiempo_ocup_relojero / total_tiempo_simulado) * 100

        prob_cliente_retira_no_listo = 0
        if self.relojeria.total_clientes_tipo_retirar_que_llegaron > 0:
            prob_cliente_retira_no_listo = self.relojeria.acum_clientes_retiran_no_listos / self.relojeria.total_clientes_tipo_retirar_que_llegaron

        final_row_data = {header: "" for header in headers}
        final_row_data["Fila"] = "FINAL"
        final_row_data["Reloj"] = f"{self.reloj:.2f}"
        final_row_data["Evento"] = "FIN SIMULACION"
        
        final_row_data["Estado Ayudante"] = self.relojeria.ayudante.estado
        final_row_data["Cola Clientes"] = len(self.relojeria.cola_clientes)
        final_row_data["Estado Relojero"] = self.relojeria.relojero.estado
        final_row_data["Cola Relojes a Reparar"] = len(self.relojeria.cola_relojes_a_reparar)
        final_row_data["Relojes Espera Retiro"] = len(self.relojeria.relojes_reparados)
        final_row_data["Acum. Clientes Retiran"] = self.relojeria.total_clientes_tipo_retirar_que_llegaron
        final_row_data["Acum. Clientes Retiran No Listos"] = self.relojeria.acum_clientes_retiran_no_listos
        final_row_data["Acum. Tiempo Ocup Ayudante"] = f"{self.relojeria.ayudante.tiempo_ocupado_acumulado:.2f}"
        final_row_data["Acum. Tiempo Ocup Relojero"] = f"{self.relojeria.relojero.tiempo_ocupado_acumulado:.2f}"
        final_row_data["Cont. Clientes"] = self.id_proximo_cliente - 1
        final_row_data["Cont. Reparaciones"] = self.relojeria.reparaciones_realizadas_relojero
        final_row_data["Porc. Ocup. Ayudante"] = f"{porc_ocup_ayudante:.2f}%"
        final_row_data["Porc. Ocup. Relojero"] = f"{porc_ocup_relojero:.2f}%"
        final_row_data["Cola Max. Clientes"] = self.relojeria.max_cola_clientes
        
        # Ensure client columns in the final row reflect their ultimate state (e.g., empty if departed)
        for i in range(max_columnas_clientes):
            client_id = i + 1
            if client_id in self.relojeria.clientes_en_sistema:
                client = self.relojeria.clientes_en_sistema[client_id]
                final_row_data[f"C {client_id}"] = f"{client.tipo_cliente}-{client.estado}"
            else:
                final_row_data[f"C {client_id}"] = "" # Clear if client is not in system at final time

        ordered_final_row = [final_row_data[header] for header in headers]
        
        if not self.resultados_vector_estado or self.resultados_vector_estado[-1][0] != "FINAL":
            self.resultados_vector_estado.append(ordered_final_row)
        
        self.full_simulation_rows.append((ordered_final_row, [])) 

        estadisticas_finales = {
            "prob_cliente_retira_no_listo": f"{prob_cliente_retira_no_listo:.2%}",
            "porc_ocup_ayudante": f"{porc_ocup_ayudante:.2f}%",
            "porc_ocup_relojero": f"{porc_ocup_relojero:.2f}%",
            "cola_max_clientes": self.relojeria.max_cola_clientes,
            "total_clientes_retiran": self.relojeria.total_clientes_tipo_retirar_que_llegaron,
            "clientes_retiran_no_listos": self.relojeria.acum_clientes_retiran_no_listos
        }
        
        return self.resultados_vector_estado, estadisticas_finales, self.full_simulation_rows, self.cantidadClientes