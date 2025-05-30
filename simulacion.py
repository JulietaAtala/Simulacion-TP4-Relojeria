import random
import math
from collections import deque
import sys

# Import necessary classes from their respective files
from logica import Evento
from cliente import Cliente
from empleado import Empleado
from reloj import Reloj
from relojeria_state import Relojeria # Assuming you've created this file with the Relojeria class

class Simulacion:
    def __init__(self, tiempo_simulacion_max, iteraciones_max):
        self.tiempo_simulacion_max = tiempo_simulacion_max
        self.iteraciones_max = iteraciones_max
        self.reloj = 0
        self.iteracion = 0
        self.eventos = [] # Priority queue for events (list that will be sorted)
        
        # Initialize Relojeria here. It already sets up initial clocks.
        self.relojeria = Relojeria(num_relojes_iniciales_para_retiro=3) 
        
        self.id_proximo_cliente = 1 # Counter for client IDs
        self.resultados_vector_estado = [] # To store each row of the state vector

        # Initialize the first arrival event
        self.generar_proxima_llegada()

    def generar_tiempo_entre_llegadas(self):
        """Genera un tiempo entre llegadas para clientes según U(13, 17) minutos."""
        rnd = random.random()
        tiempo_entre_llegadas = 13 + rnd * (17 - 13) # U(13, 17)
        return tiempo_entre_llegadas, rnd

    def generar_tipo_cliente(self):
        """Determina el tipo de cliente (Comprar, Entregar, Retirar) basado en probabilidades."""
        rnd = random.random()
        if rnd < 0.45:
            return "Comprar", rnd
        elif rnd < 0.45 + 0.25: # 0.45 to 0.70
            return "Entregar", rnd
        else: # 0.70 to 1.00
            return "Retirar", rnd

    def generar_tiempo_atencion_ayudante(self, tipo_cliente):
        """Genera el tiempo de atención del ayudante."""
        if tipo_cliente == "Comprar":
            rnd = random.random()
            tiempo_atencion = 6 + rnd * (10 - 6) # U(6, 10)
            return tiempo_atencion, rnd
        else: # "Entregar" or "Retirar"
            return 3, None # Fixed 3 minutes, no random number needed for this

    def generar_tiempo_reparacion_relojero(self):
        """Genera el tiempo de reparación del relojero según U(18, 22) minutos."""
        rnd = random.random()
        tiempo_reparacion = 18 + rnd * (22 - 18) # U(18, 22)
        return tiempo_reparacion, rnd

    def generar_proxima_llegada(self):
        """Programa el próximo evento de llegada de un cliente."""
        tiempo_entre_llegadas, rnd_llegada = self.generar_tiempo_entre_llegadas()
        proxima_llegada_tiempo = self.reloj + tiempo_entre_llegadas
        
        # Only schedule if it's within the total simulation time
        if proxima_llegada_tiempo <= self.tiempo_simulacion_max:
            evento = Evento(tipo="Llegada Cliente", tiempo=proxima_llegada_tiempo)
            evento.random_llegada = rnd_llegada # Store the random number for display
            self.eventos.append(evento)
            self.eventos.sort(key=lambda ev: ev.tiempo) # Maintain sorted event list

    def procesar_llegada_cliente(self, evento_actual):
        """Procesa un evento de llegada de cliente."""
        id_cliente = self.id_proximo_cliente
        self.id_proximo_cliente += 1
        
        tipo_cliente, rnd_tipo_cliente = self.generar_tipo_cliente()
        
        # Initialize client state as "Esperando" before deciding queue or service
        cliente = Cliente(id_cliente, evento_actual.tiempo, tipo_cliente, estado="Esperando") 
        cliente.random_tipo_cliente = rnd_tipo_cliente # Store random for client type

        if tipo_cliente == "Entregar":
            cliente.reloj_a_entregar = True
        elif tipo_cliente == "Retirar":
            cliente.reloj_a_retirar = True
            self.relojeria.total_clientes_tipo_retirar_que_llegaron += 1 # Increment counter for 'Retirar' clients

        self.relojeria.clientes_en_sistema[id_cliente] = cliente # Add client to active system

        # --- CRITICAL CHANGE FOR QUEUE LOGIC ---
        if self.relojeria.ayudante.estado == "Libre":
            # Assistant is free, serve immediately
            self.relojeria.tiempo_ocio_ayudante += (self.reloj - self.relojeria.ultimo_tiempo_ayudante_libre) # Update idle time

            cliente.estado = "Siendo Atendido" # Client is immediately attended
            self.relojeria.ayudante.estado = "Ocupado"

            tiempo_atencion, rnd_atencion = self.generar_tiempo_atencion_ayudante(cliente.tipo_cliente)
            cliente.tiempo_atencion = tiempo_atencion # Store actual attention time
            cliente.random_tiempo_atencion = rnd_atencion # Store random for attention time
            
            self.relojeria.ayudante.random_tiempo_tarea = rnd_atencion # Store random for assistant's task (if applicable)
            self.relojeria.ayudante.tiempo_fin_tarea = self.reloj + tiempo_atencion

            # Schedule Fin Atencion Ayudante event
            evento = Evento(tipo="Fin Atencion Ayudante", tiempo=self.relojeria.ayudante.tiempo_fin_tarea, id_cliente=cliente.id_cliente)
            evento.cliente_obj_being_served = cliente # Pass the actual client object for accurate calculation
            self.eventos.append(evento)
            self.eventos.sort(key=lambda ev: ev.tiempo) # Maintain sorted event list
        else:
            # Assistant is busy, client joins the queue
            cliente.estado = "En cola" # Client is waiting in queue
            self.relojeria.cola_clientes.append(cliente) # Add client to assistant's queue

            # Update max client queue if necessary
            if len(self.relojeria.cola_clientes) > self.relojeria.max_cola_clientes:
                self.relojeria.max_cola_clientes = len(self.relojeria.cola_clientes)

        # Schedule next arrival (this is separate and always happens regardless of service)
        self.generar_proxima_llegada()

    def intentar_atender_cliente(self):
        """Intenta que el ayudante atienda a un cliente si está libre y hay clientes en cola."""
        # This function is now ONLY called when an assistant finishes a task (Fin Atencion Ayudante).
        # It checks if the assistant is free AND there's someone in the queue.
        if self.relojeria.ayudante.estado == "Libre" and self.relojeria.cola_clientes:
            # Update idle time for assistant
            self.relojeria.tiempo_ocio_ayudante += (self.reloj - self.relojeria.ultimo_tiempo_ayudante_libre)

            cliente_atendiendo = self.relojeria.cola_clientes.popleft() # Client moves from queue to being served
            
            tiempo_atencion, rnd_atencion = self.generar_tiempo_atencion_ayudante(cliente_atendiendo.tipo_cliente)
            
            cliente_atendiendo.tiempo_atencion = tiempo_atencion # Store actual attention time
            cliente_atendiendo.random_tiempo_atencion = rnd_atencion # Store random for attention time
            cliente_atendiendo.estado = "Siendo Atendido"

            self.relojeria.ayudante.estado = "Ocupado"
            self.relojeria.ayudante.random_tiempo_tarea = rnd_atencion # Store random for assistant's task (if applicable)
            self.relojeria.ayudante.tiempo_fin_tarea = self.reloj + tiempo_atencion

            # Schedule Fin Atencion Ayudante event
            evento = Evento(tipo="Fin Atencion Ayudante", tiempo=self.relojeria.ayudante.tiempo_fin_tarea, id_cliente=cliente_atendiendo.id_cliente)
            evento.cliente_obj_being_served = cliente_atendiendo # Pass the actual client object for accurate calculation
            self.eventos.append(evento)
            self.eventos.sort(key=lambda ev: ev.tiempo) # Maintain sorted event list

    def procesar_fin_atencion_ayudante(self, evento_actual):
        """Procesa un evento de fin de atención del ayudante."""
        cliente_atendido = evento_actual.cliente_obj_being_served # Retrieve the actual client object

        cliente_atendido.estado = "Atendido"
        self.relojeria.ayudante.estado = "Libre"
        
        # Accurately add time spent busy by the assistant
        self.relojeria.ayudante.tiempo_ocupado_acumulado += cliente_atendido.tiempo_atencion
        
        self.relojeria.clientes_atendidos_ayudante += 1 # Increment attended clients by assistant
        self.relojeria.ultimo_tiempo_ayudante_libre = evento_actual.tiempo # Update last free time

        if cliente_atendido.tipo_cliente == "Entregar":
            reloj_nuevo = Reloj(estado="Pendiente de Reparacion")
            self.relojeria.cola_relojes_a_reparar.append(reloj_nuevo)
            del self.relojeria.clientes_en_sistema[cliente_atendido.id_cliente] # Client leaves after delivering
            self.intentar_reparar_reloj() # Try to start repair if relojero is free

        elif cliente_atendido.tipo_cliente == "Retirar":
            reloj_encontrado = None
            # Search for a repaired clock
            for reloj in self.relojeria.relojes_reparados:
                if reloj.estado == "Reparado":
                    reloj_encontrado = reloj
                    break

            if reloj_encontrado:
                reloj_encontrado.estado = "Retirado"
                self.relojeria.relojes_reparados.remove(reloj_encontrado) # Remove from repaired list
            else:
                self.relojeria.acum_clientes_retiran_no_listos += 1 # Clock not ready

            del self.relojeria.clientes_en_sistema[cliente_atendido.id_cliente] # Client leaves after attempt

        elif cliente_atendido.tipo_cliente == "Comprar":
            del self.relojeria.clientes_en_sistema[cliente_atendido.id_cliente] # Client leaves after buying

        # Try to serve next client if assistant is free and there are clients in queue
        self.intentar_atender_cliente()

    def intentar_reparar_reloj(self):
        """Intenta que el relojero repare un reloj si está libre y hay relojes en cola."""
        if self.relojeria.relojero.estado == "Libre" and self.relojeria.cola_relojes_a_reparar:
            # Update idle time for relojero
            self.relojeria.tiempo_ocio_relojero += (self.reloj - self.relojeria.ultimo_tiempo_relojero_libre)

            reloj_a_reparar = self.relojeria.cola_relojes_a_reparar.popleft()
            reloj_a_reparar.estado = "En Reparacion"
            reloj_a_reparar.tiempo_inicio_reparacion = self.reloj # Mark start of repair

            tiempo_reparacion, rnd_reparacion = self.generar_tiempo_reparacion_relojero()
            
            self.relojeria.relojero.estado = "Ocupado"
            self.relojeria.relojero.random_tiempo_tarea = rnd_reparacion # Store random for repair time
            self.relojeria.relojero.tiempo_fin_tarea = self.reloj + tiempo_reparacion

            # Schedule Fin Reparacion Relojero event, passing the actual reloj object
            evento = Evento(tipo="Fin Reparacion Relojero", tiempo=self.relojeria.relojero.tiempo_fin_tarea, id_reloj=reloj_a_reparar.id_reloj)
            evento.reloj_obj_being_repaired = reloj_a_reparar # Store the actual object
            self.eventos.append(evento)
            self.eventos.sort(key=lambda ev: ev.tiempo)

    def procesar_fin_reparacion_relojero(self, evento_actual):
        """Procesa un evento de fin de reparación del relojero."""
        reloj_reparado = evento_actual.reloj_obj_being_repaired # Retrieve the actual object

        reloj_reparado.estado = "Reparado"
        reloj_reparado.tiempo_fin_reparacion = evento_actual.tiempo # Mark end of repair

        # Accurately add time spent busy by the relojero on repair
        self.relojeria.relojero.tiempo_ocupado_acumulado += (reloj_reparado.tiempo_fin_reparacion - reloj_reparado.tiempo_inicio_reparacion)
        
        self.relojeria.reparaciones_realizadas_relojero += 1 # Increment repairs done

        # Relojero enters "Limpiando" state after repair
        self.relojeria.relojero.estado = "Limpiando"
        tiempo_limpieza = 5 # Fixed cleanup time
        self.relojeria.relojero.tiempo_fin_tarea = self.reloj + tiempo_limpieza # Schedule end of cleanup

        self.relojeria.relojes_reparados.append(reloj_reparado) # Move to repaired list

        # Schedule Fin Limpieza Relojero event
        evento = Evento(tipo="Fin Limpieza Relojero", tiempo=self.relojeria.relojero.tiempo_fin_tarea)
        self.eventos.append(evento)
        self.eventos.sort(key=lambda ev: ev.tiempo)

        # Do NOT try to repair next clock yet, clockmaker is cleaning

    def procesar_fin_limpieza_relojero(self, evento_actual):
        """Procesa un evento de fin de limpieza del relojero."""
        self.relojeria.relojero.estado = "Libre"
        # Accurately add time spent busy by the relojero on cleanup
        self.relojeria.relojero.tiempo_ocupado_acumulado += 5 # Cleanup is fixed 5 minutes
        self.relojeria.ultimo_tiempo_relojero_libre = evento_actual.tiempo # Update last free time

        # Try to repair next clock if there are clocks in queue
        self.intentar_reparar_reloj()

    def ejecutar_simulacion(self, tiempo_simulacion_max, iteraciones_a_mostrar, hora_desde_mostrar):
        """
        Ejecuta la simulación y genera el vector de estado y las estadísticas.
        
        Args:
            tiempo_simulacion_max (float): El tiempo máximo a simular.
            iteraciones_a_mostrar (int): La cantidad de filas a mostrar en el vector de estado.
            hora_desde_mostrar (float): La hora a partir de la cual se empiezan a mostrar las filas.
        """
        self.tiempo_simulacion_max = tiempo_simulacion_max
        
        # Reset simulation state for a new run
        self.reloj = 0
        self.iteracion = 0
        self.eventos = []
        self.relojeria = Relojeria(num_relojes_iniciales_para_retiro=3) # Reinitialize relojeria state
        self.id_proximo_cliente = 1
        self.resultados_vector_estado = []
        Reloj._id_counter = 0 # Reset clock ID counter for new simulation run

        # Generate the first arrival event
        self.generar_proxima_llegada()

        # Headers for the state vector (must match ui.py columns)
        headers = [
            "Fila", "Reloj", "Evento", "RND Llegada", "Tiempo entre llegadas", "Proxima llegada",
            "RND Tipo Cliente", "Tipo Cliente", "RND Atencion Ayudante", "Tiempo Atencion Ayudante", "Fin Atencion Ayudante",
            "RND Reparacion Relojero", "Tiempo Reparacion Relojero", "Fin Reparacion Relojero", "Fin Limpieza Relojero",
            "Estado Ayudante", "Cola Clientes", "Estado Relojero", "Cola Relojes a Reparar", "Relojes Espera Retiro",
            "Acum. Clientes Retiran No Listos", "Acum. Tiempo Ocio Ayudante", "Acum. Tiempo Ocio Relojero",
            "Cont. Clientes", "Cont. Reparaciones", "Porc. Ocup. Ayudante", "Porc. Ocup. Relojero", "Cola Max. Clientes"
        ]
        self.resultados_vector_estado.append(headers) # Add headers as the first row

        num_displayed_rows = 0 # Counter for rows added to display results

        while self.eventos and self.reloj <= self.tiempo_simulacion_max and self.iteracion < self.iteraciones_max:
            self.iteracion += 1
            evento_actual = self.eventos.pop(0) # Get the next event
            self.reloj = evento_actual.tiempo # Advance the clock

            # Prepare row for state vector
            row_data = {header: "" for header in headers} # Initialize with empty strings
            row_data["Fila"] = self.iteracion
            row_data["Reloj"] = f"{self.reloj:.2f}"
            row_data["Evento"] = evento_actual.tipo

            # Process the event and update system state
            if evento_actual.tipo == "Llegada Cliente":
                row_data["RND Llegada"] = f"{evento_actual.random_llegada:.4f}"
                
                # To get the *next* arrival details, we need to peek at the next scheduled event
                next_llegada_event = next((e for e in self.eventos if e.tipo == "Llegada Cliente"), None)
                if next_llegada_event:
                    tll_for_display = next_llegada_event.tiempo - self.reloj # Calculate TLL for display
                    row_data["Tiempo entre llegadas"] = f"{tll_for_display:.2f}"
                    row_data["Proxima llegada"] = f"{next_llegada_event.tiempo:.2f}"
                else:
                    row_data["Tiempo entre llegadas"] = "N/A"
                    row_data["Proxima llegada"] = "N/A"
                
                # This is the actual event processing
                self.procesar_llegada_cliente(evento_actual)
                
                # For Tipo Cliente, the client object has the determined type
                # We need to access the client object that was just created/added.
                # Since id_proximo_cliente is incremented *after* client creation, it's the ID of the just created client.
                # Find the client based on its state and time
                # If served immediately, it will be in Ayudante's context. If in queue, in queue.
                # This part is tricky because the client object itself holds the rnd_tipo_cliente.
                # The easiest way to retrieve it for display is to pass it through the event if possible,
                # or ensure the client object is easily accessible.
                # For simplicity here, we'll assume the random number generation is done *before* the client object.
                # So we can just use the random number from the event's random_llegada, and infer for other fields.
                # However, for `RND Tipo Cliente`, it's tied to the logic inside procesar_llegada_cliente.
                # Let's directly get the random number used from the logic for the row display.
                # Note: This is less ideal, but to avoid making Evento too complex.
                
                # To accurately get the RND_Tipo_Cliente, we'd need to store it with the event when generated.
                # For the purpose of the state vector, we can generate a random number here
                # just for display, or better, pass the info from the client object when it's handled.
                # Given the change in procesar_llegada_cliente, the client object is directly available.
                
                # If client was immediately served:
                if self.relojeria.ayudante.estado == "Ocupado" and self.relojeria.ayudante.tiempo_fin_tarea > self.reloj:
                    current_client_serving = next((c for c in self.relojeria.clientes_en_sistema.values() if c.estado == "Siendo Atendido"), None)
                    if current_client_serving and current_client_serving.tiempo_llegada == evento_actual.tiempo:
                        row_data["RND Tipo Cliente"] = f"{current_client_serving.random_tipo_cliente:.4f}"
                        row_data["Tipo Cliente"] = current_client_serving.tipo_cliente
                # If client went to queue:
                elif len(self.relojeria.cola_clientes) > 0 and self.relojeria.cola_clientes[-1].tiempo_llegada == evento_actual.tiempo:
                    last_client_in_queue = self.relojeria.cola_clientes[-1]
                    row_data["RND Tipo Cliente"] = f"{last_client_in_queue.random_tipo_cliente:.4f}"
                    row_data["Tipo Cliente"] = last_client_in_queue.tipo_cliente


            elif evento_actual.tipo == "Fin Atencion Ayudante":
                client_obj_finished = evento_actual.cliente_obj_being_served # Get the actual client object
                if client_obj_finished:
                    row_data["RND Atencion Ayudante"] = f"{client_obj_finished.random_tiempo_atencion:.4f}" if client_obj_finished.random_tiempo_atencion is not None else ""
                    row_data["Tiempo Atencion Ayudante"] = f"{client_obj_finished.tiempo_atencion:.2f}"
                row_data["Fin Atencion Ayudante"] = f"{evento_actual.tiempo:.2f}" # When this event finished
                self.procesar_fin_atencion_ayudante(evento_actual)
                
            elif evento_actual.tipo == "Fin Reparacion Relojero":
                reloj_obj_finished = evento_actual.reloj_obj_being_repaired # Get the actual clock object
                if reloj_obj_finished:
                    row_data["RND Reparacion Relojero"] = f"{self.relojeria.relojero.random_tiempo_tarea:.4f}" if self.relojeria.relojero.random_tiempo_tarea is not None else ""
                    repair_duration = reloj_obj_finished.tiempo_fin_reparacion - reloj_obj_finished.tiempo_inicio_reparacion
                    row_data["Tiempo Reparacion Relojero"] = f"{repair_duration:.2f}"
                row_data["Fin Reparacion Relojero"] = f"{evento_actual.tiempo:.2f}" # When repair finished
                self.procesar_fin_reparacion_relojero(evento_actual)
                if self.relojeria.relojero.estado == "Limpiando": # Relojero starts cleaning
                    row_data["Fin Limpieza Relojero"] = f"{self.relojeria.relojero.tiempo_fin_tarea:.2f}"


            elif evento_actual.tipo == "Fin Limpieza Relojero":
                row_data["Fin Limpieza Relojero"] = f"{evento_actual.tiempo:.2f}" # When cleanup finished
                self.procesar_fin_limpieza_relojero(evento_actual)
            
            # Update common state variables for the current row
            row_data["Estado Ayudante"] = self.relojeria.ayudante.estado
            row_data["Cola Clientes"] = len(self.relojeria.cola_clientes)
            row_data["Estado Relojero"] = self.relojeria.relojero.estado
            row_data["Cola Relojes a Reparar"] = len(self.relojeria.cola_relojes_a_reparar)
            row_data["Relojes Espera Retiro"] = len(self.relojeria.relojes_reparados)
            row_data["Acum. Clientes Retiran No Listos"] = self.relojeria.acum_clientes_retiran_no_listos

            row_data["Acum. Tiempo Ocio Ayudante"] = f"{self.relojeria.tiempo_ocio_ayudante:.2f}"
            row_data["Acum. Tiempo Ocio Relojero"] = f"{self.relojeria.tiempo_ocio_relojero:.2f}"

            row_data["Cont. Clientes"] = self.id_proximo_cliente - 1 # Total clients that have arrived
            row_data["Cont. Reparaciones"] = self.relojeria.reparaciones_realizadas_relojero
            row_data["Cola Max. Clientes"] = self.relojeria.max_cola_clientes

            # Percentage calculation only makes sense at the end of simulation
            row_data["Porc. Ocup. Ayudante"] = ""
            row_data["Porc. Ocup. Relojero"] = ""

            # Logic to add row to display results based on "hora_desde_mostrar" and "iteraciones_a_mostrar"
            if self.reloj >= hora_desde_mostrar and num_displayed_rows < iteraciones_a_mostrar:
                # Convert dict to list based on headers order for Treeview
                ordered_row = [row_data[header] for header in headers]
                self.resultados_vector_estado.append(ordered_row)
                num_displayed_rows += 1
            
        self.relojeria.tiempo_total_simulacion = self.reloj # Final simulation time

        # Calculate final statistics
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

        # Prepare the final row data (without temporal objects)
        final_row_data = {header: "" for header in headers} # Initialize with empty strings
        final_row_data["Fila"] = "FINAL" # Or a special indicator
        final_row_data["Reloj"] = f"{self.reloj:.2f}"
        final_row_data["Evento"] = "FIN SIMULACION"
        
        # Non-temporal objects and final stats
        final_row_data["Estado Ayudante"] = self.relojeria.ayudante.estado
        final_row_data["Cola Clientes"] = len(self.relojeria.cola_clientes)
        final_row_data["Estado Relojero"] = self.relojeria.relojero.estado
        final_row_data["Cola Relojes a Reparar"] = len(self.relojeria.cola_relojes_a_reparar)
        final_row_data["Relojes Espera Retiro"] = len(self.relojeria.relojes_reparados)
        final_row_data["Acum. Clientes Retiran No Listos"] = self.relojeria.acum_clientes_retiran_no_listos
        final_row_data["Acum. Tiempo Ocio Ayudante"] = f"{self.relojeria.tiempo_ocio_ayudante:.2f}"
        final_row_data["Acum. Tiempo Ocio Relojero"] = f"{self.relojeria.tiempo_ocio_relojero:.2f}"
        final_row_data["Cont. Clientes"] = self.id_proximo_cliente - 1
        final_row_data["Cont. Reparaciones"] = self.relojeria.reparaciones_realizadas_relojero
        final_row_data["Porc. Ocup. Ayudante"] = f"{porc_ocup_ayudante:.2f}%"
        final_row_data["Porc. Ocup. Relojero"] = f"{porc_ocup_relojero:.2f}%"
        final_row_data["Cola Max. Clientes"] = self.relojeria.max_cola_clientes
        
        # Convert dict to list
        ordered_final_row = [final_row_data[header] for header in headers]
        
        # Check if this exact row (or a similar final row) is already the last one
        if not self.resultados_vector_estado or self.resultados_vector_estado[-1][0] != "FINAL":
            self.resultados_vector_estado.append(ordered_final_row)


        # Final statistics for display in UI labels
        estadisticas_finales = {
            "prob_cliente_retira_no_listo": f"{prob_cliente_retira_no_listo:.2%}",
            "porc_ocup_ayudante": f"{porc_ocup_ayudante:.2f}%",
            "porc_ocup_relojero": f"{porc_ocup_relojero:.2f}%",
            "cola_max_clientes": self.relojeria.max_cola_clientes,
            "total_clientes_retiran": self.relojeria.total_clientes_tipo_retirar_que_llegaron,
            "clientes_retiran_no_listos": self.relojeria.acum_clientes_retiran_no_listos
        }
        
        return self.resultados_vector_estado, estadisticas_finales