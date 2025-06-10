import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

from simulacion import Simulacion

def ventana_simulacion():
    ventana = tk.Tk()
    ventana.title("Simulación de Relojería")
    ventana.geometry("1800x950") # Increased size significantly for more parameters

    # Configure grid to allow resizing
    ventana.grid_rowconfigure(2, weight=1)
    ventana.grid_columnconfigure(0, weight=1)

    # Frame for simulation parameters
    frame_parametros = tk.Frame(ventana, bd=2, relief="groove")
    frame_parametros.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    # --- SIMULATION CONTROL PARAMETERS ---
    row_idx = 0
    tk.Label(frame_parametros, text="Tiempo a simular (min):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
    entry_tiempo_simulacion = tk.Entry(frame_parametros, width=8)
    entry_tiempo_simulacion.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
    entry_tiempo_simulacion.insert(0, "480") 

    row_idx += 1
    tk.Label(frame_parametros, text="Mostrar desde hora (min):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
    entry_hora_desde = tk.Entry(frame_parametros, width=8)
    entry_hora_desde.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
    entry_hora_desde.insert(0, "0") 

    row_idx += 1
    tk.Label(frame_parametros, text="Cantidad de iteraciones a mostrar:", font=("Roboto", 10, "bold")).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
    entry_cant_iteraciones = tk.Entry(frame_parametros, width=8)
    entry_cant_iteraciones.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
    entry_cant_iteraciones.insert(0, "50") 
    
    # --- DYNAMIC SIMULATION PARAMETERS (Marked in Red) ---
    col_start = 2 # Start a new column for these parameters

    # Client Arrival Interval U(13, 17)
    row_idx = 0
    tk.Label(frame_parametros, text="Tiempo entre llegadas (min):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    tk.Label(frame_parametros, text="U(", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 1, sticky="w")
    entry_tll_min = tk.Entry(frame_parametros, width=5)
    entry_tll_min.grid(row=row_idx, column=col_start + 2, padx=1, pady=2, sticky="w")
    entry_tll_min.insert(0, "13")
    tk.Label(frame_parametros, text=";", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 3, sticky="w")
    entry_tll_max = tk.Entry(frame_parametros, width=5)
    entry_tll_max.grid(row=row_idx, column=col_start + 4, padx=1, pady=2, sticky="w")
    entry_tll_max.insert(0, "17")
    tk.Label(frame_parametros, text=")", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 5, sticky="w")

    # Client Type Probabilities (45%, 25%, 30%)
    row_idx += 1
    tk.Label(frame_parametros, text="Prob. Cliente Comprar (%):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    entry_prob_comprar = tk.Entry(frame_parametros, width=8)
    entry_prob_comprar.grid(row=row_idx, column=col_start + 1, padx=5, pady=2, sticky="w")
    entry_prob_comprar.insert(0, "45")

    row_idx += 1
    tk.Label(frame_parametros, text="Prob. Cliente Entregar (%):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    entry_prob_entregar = tk.Entry(frame_parametros, width=8)
    entry_prob_entregar.grid(row=row_idx, column=col_start + 1, padx=5, pady=2, sticky="w")
    entry_prob_entregar.insert(0, "25")

    row_idx += 1
    tk.Label(frame_parametros, text="Prob. Cliente Retirar (%):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    entry_prob_retirar = tk.Entry(frame_parametros, width=8)
    entry_prob_retirar.grid(row=row_idx, column=col_start + 1, padx=5, pady=2, sticky="w")
    entry_prob_retirar.insert(0, "30")

    # Sales Duration U(6, 10)
    row_idx += 1
    tk.Label(frame_parametros, text="Tiempo Venta (min):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    tk.Label(frame_parametros, text="U(", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 1, sticky="w")
    entry_venta_min = tk.Entry(frame_parametros, width=5)
    entry_venta_min.grid(row=row_idx, column=col_start + 2, padx=1, pady=2, sticky="w")
    entry_venta_min.insert(0, "6")
    tk.Label(frame_parametros, text=";", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 3, sticky="w")
    entry_venta_max = tk.Entry(frame_parametros, width=5)
    entry_venta_max.grid(row=row_idx, column=col_start + 4, padx=1, pady=2, sticky="w")
    entry_venta_max.insert(0, "10")
    tk.Label(frame_parametros, text=")", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 5, sticky="w")

    # Deliver/Pickup Duration (3 min)
    row_idx += 1
    tk.Label(frame_parametros, text="Tiempo Atención (Entregar/Retirar, min):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    entry_atencion_fija = tk.Entry(frame_parametros, width=8)
    entry_atencion_fija.grid(row=row_idx, column=col_start + 1, padx=5, pady=2, sticky="w")
    entry_atencion_fija.insert(0, "3")

    # Repair Duration U(18, 22)
    row_idx += 1
    tk.Label(frame_parametros, text="Tiempo Reparación (min):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    tk.Label(frame_parametros, text="U(", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 1, sticky="w")
    entry_reparacion_min = tk.Entry(frame_parametros, width=5)
    entry_reparacion_min.grid(row=row_idx, column=col_start + 2, padx=1, pady=2, sticky="w")
    entry_reparacion_min.insert(0, "18")
    tk.Label(frame_parametros, text=";", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 3, sticky="w")
    entry_reparacion_max = tk.Entry(frame_parametros, width=5)
    entry_reparacion_max.grid(row=row_idx, column=col_start + 4, padx=1, pady=2, sticky="w")
    entry_reparacion_max.insert(0, "22")
    tk.Label(frame_parametros, text=")", font=("Roboto", 10)).grid(row=row_idx, column=col_start + 5, sticky="w")

    # Cleanup Duration (5 min)
    row_idx += 1
    tk.Label(frame_parametros, text="Tiempo Orden Relojero (min):", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    entry_orden_relojero = tk.Entry(frame_parametros, width=8)
    entry_orden_relojero.grid(row=row_idx, column=col_start + 1, padx=5, pady=2, sticky="w")
    entry_orden_relojero.insert(0, "5")

    # Initial Clocks for Pickup (3)
    row_idx += 1
    tk.Label(frame_parametros, text="Relojes iniciales en espera de retiro:", font=("Roboto", 10, "bold")).grid(row=row_idx, column=col_start, padx=5, pady=2, sticky="w")
    entry_relojes_iniciales = tk.Entry(frame_parametros, width=8)
    entry_relojes_iniciales.grid(row=row_idx, column=col_start + 1, padx=5, pady=2, sticky="w")
    entry_relojes_iniciales.insert(0, "3")


    # Frame for statistics
    frame_estadisticas = tk.Frame(ventana, bd=2, relief="groove")
    frame_estadisticas.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    # Labels for statistics
    label_prob_no_reparado = tk.Label(frame_estadisticas, text="Prob. cliente retira no reparado: ", font=("Roboto", 10))
    label_prob_no_reparado.grid(row=0, column=0, padx=5, pady=2, sticky="w")
    
    label_ocup_ayudante = tk.Label(frame_estadisticas, text="Porc. ocupación ayudante: ", font=("Roboto", 10))
    label_ocup_ayudante.grid(row=1, column=0, padx=5, pady=2, sticky="w")

    label_ocup_relojero = tk.Label(frame_estadisticas, text="Porc. ocupación relojero: ", font=("Roboto", 10))
    label_ocup_relojero.grid(row=2, column=0, padx=5, pady=2, sticky="w")
    
    label_cola_max = tk.Label(frame_estadisticas, text="Cola máxima de clientes: ", font=("Roboto", 10))
    label_cola_max.grid(row=3, column=0, padx=5, pady=2, sticky="w")

    # Treeview for the state vector
    frame_tabla = tk.Frame(ventana)
    frame_tabla.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # Define columns based on the simulation output
    columnas = [
        "Fila", "Reloj", "Evento", "RND Llegada", "Tiempo entre llegadas", "Proxima llegada",
        "RND Tipo Cliente", "Tipo Cliente", "RND Atencion Ayudante", "Tiempo Atencion Ayudante", "Fin Atencion Ayudante",
        "RND Reparacion Relojero", "Tiempo Reparacion Relojero", "Fin Reparacion Relojero", "Fin Limpieza Relojero",
        "Estado Ayudante", "Cola Clientes", "Estado Relojero", "Cola Relojes a Reparar", "Relojes Espera Retiro",
        "Acum. Clientes Retiran No Listos", "Acum. Tiempo Ocio Ayudante", "Acum. Tiempo Ocio Relojero",
        "Cont. Clientes", "Cont. Reparaciones", "Porc. Ocup. Ayudante", "Porc. Ocup. Relojero", "Cola Max. Clientes",
        "Cliente Evento ID", "Estado Cliente Evento" 
    ]

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings')
    tabla.grid(row=0, column=0, sticky="nsew")

    # Configure column headings and widths
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120, anchor="center") 
    
    # Specific width for the new columns
    tabla.column("Cliente Evento ID", width=100)
    tabla.column("Estado Cliente Evento", width=150)

    # Configure Treeview tags for row coloring
    style = ttk.Style()
    style.configure("Departed.Treeview", background="lightgray") 

    # Scrollbars
    scrollbar_horizontal = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=tabla.xview)
    scrollbar_horizontal.grid(row=1, column=0, sticky="ew")
    tabla.config(xscrollcommand=scrollbar_horizontal.set)

    scrollbar_vertical = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla.yview)
    scrollbar_vertical.grid(row=0, column=1, sticky="ns")
    tabla.config(yscrollcommand=scrollbar_vertical.set)

    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    global full_sim_data_for_export
    full_sim_data_for_export = []

    def ejecutar_simulacion_y_mostrar():
        for i in tabla.get_children():
            tabla.delete(i) # Clear previous results

        try:
            # --- Get simulation control parameters ---
            tiempo_simulacion = float(entry_tiempo_simulacion.get())
            hora_desde = float(entry_hora_desde.get())
            cant_iteraciones = int(entry_cant_iteraciones.get())

            # --- Get dynamic simulation parameters ---
            # Client Arrival Interval
            tll_min = float(entry_tll_min.get())
            tll_max = float(entry_tll_max.get())
            if not (0 <= tll_min < tll_max):
                raise ValueError("Tiempo entre llegadas (min) debe ser 0 <= min < max.")

            # Client Type Probabilities
            prob_comprar = float(entry_prob_comprar.get()) / 100.0
            prob_entregar = float(entry_prob_entregar.get()) / 100.0
            prob_retirar = float(entry_prob_retirar.get()) / 100.0
            prob_sum = prob_comprar + prob_entregar + prob_retirar
            if abs(prob_sum - 1.0) > 0.001: # Allow for minor float precision differences
                messagebox.showwarning("Advertencia de Probabilidades", f"Las probabilidades de tipo de cliente suman {prob_sum*100:.2f}%, no 100%. Se normalizarán.")
                # Normalize probabilities if they don't sum to 1.0
                norm_factor = 1.0 / prob_sum
                prob_comprar *= norm_factor
                prob_entregar *= norm_factor
                prob_retirar *= norm_factor
            
            probabilidades_cliente = [prob_comprar, prob_entregar, prob_retirar]

            # Sales Duration
            venta_min = float(entry_venta_min.get())
            venta_max = float(entry_venta_max.get())
            if not (0 <= venta_min < venta_max):
                raise ValueError("Tiempo Venta (min) debe ser 0 <= min < max.")

            # Deliver/Pickup Duration
            atencion_fija = float(entry_atencion_fija.get())
            if atencion_fija < 0:
                raise ValueError("Tiempo Atención (Entregar/Retirar) no puede ser negativo.")

            # Repair Duration
            reparacion_min = float(entry_reparacion_min.get())
            reparacion_max = float(entry_reparacion_max.get())
            if not (0 <= reparacion_min < reparacion_max):
                raise ValueError("Tiempo Reparación (min) debe ser 0 <= min < max.")

            # Cleanup Duration
            orden_relojero = float(entry_orden_relojero.get())
            if orden_relojero < 0:
                raise ValueError("Tiempo Orden Relojero no puede ser negativo.")

            # Initial Clocks for Pickup
            relojes_iniciales = int(entry_relojes_iniciales.get())
            if relojes_iniciales < 0:
                raise ValueError("Relojes iniciales no puede ser negativo.")

        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Por favor ingrese valores numéricos válidos. {e}")
            return
        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error al procesar las entradas: {e}")
            return


        # Pass all parameters to the Simulacion constructor
        sim = Simulacion(
            tiempo_simulacion_max=tiempo_simulacion, 
            iteraciones_max=100000, # Fixed max iterations for the simulation loop
            tll_params=(tll_min, tll_max),
            prob_cliente_params=probabilidades_cliente,
            venta_params=(venta_min, venta_max),
            atencion_fija=atencion_fija,
            reparacion_params=(reparacion_min, reparacion_max),
            orden_relojero=orden_relojero,
            relojes_iniciales=relojes_iniciales
        )

        # Call execute_simulation (which now only takes display parameters)
        vector_estado_display, estadisticas, full_sim_data = sim.ejecutar_simulacion(
            iteraciones_a_mostrar=cant_iteraciones, 
            hora_desde_mostrar=hora_desde
        )
        
        print(f"DEBUG UI: Received {len(vector_estado_display)} rows for display.")
        if len(vector_estado_display) > 1:
            print(f"DEBUG UI: First display data row: {vector_estado_display[1]}")
        else:
            print("DEBUG UI: vector_estado_display contains only headers or is empty.")

        global full_sim_data_for_export
        full_sim_data_for_export = full_sim_data

        for row_values in vector_estado_display[0:]: 
            tags_to_apply = []
            # Find the corresponding row in full_sim_data to get tags
            for original_full_row_values, original_tags in full_sim_data_for_export:
                if original_full_row_values == row_values: 
                    tags_to_apply = original_tags
                    break
            tabla.insert("", tk.END, values=row_values, tags=tuple(tags_to_apply))

        label_prob_no_reparado.config(text=f"Prob. cliente retira no reparado: {estadisticas['prob_cliente_retira_no_listo']}")
        label_ocup_ayudante.config(text=f"Porc. ocupación ayudante: {estadisticas['porc_ocup_ayudante']}")
        label_ocup_relojero.config(text=f"Porc. ocupación relojero: {estadisticas['porc_ocup_relojero']}")
        label_cola_max.config(text=f"Cola máxima de clientes: {estadisticas['cola_max_clientes']}")

    def exportar_a_csv():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar Vector de Estado como CSV"
        )
        
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if full_sim_data_for_export:
                    writer.writerow(full_sim_data_for_export[0][0])
                    for row_values, _ in full_sim_data_for_export[1:]:
                        writer.writerow(row_values)
                else:
                    messagebox.showwarning("Exportar CSV", "No hay datos de simulación para exportar.")
                    return
            messagebox.showinfo("Exportar CSV", "Datos exportados exitosamente a:\n" + file_path)
        except Exception as e:
            messagebox.showerror("Error al exportar", f"No se pudo exportar el archivo: {e}")

    def copiar_tabla_portapapeles():
        filas = []
        filas.append('\t'.join(columnas))
        for item_id in tabla.get_children():
            valores = tabla.item(item_id)['values']
            fila_str = [str(v) if v is not None else "" for v in valores]
            filas.append('\t'.join(fila_str))
        texto_copiado = '\n'.join(filas)

        ventana.clipboard_clear()
        ventana.clipboard_append(texto_copiado)
        tk.messagebox.showinfo("Copiado", "Contenido copiado al portapapeles. Ahora puede pegarlo en Excel.")


    btn_simular = tk.Button(frame_parametros, text="Simular", command=ejecutar_simulacion_y_mostrar, font=("Roboto", 12, "bold"), bg="#4CAF50", fg="white")
    btn_simular.grid(row=0, column=col_start + 6, rowspan=3, padx=10, pady=5, sticky="e") 

    btn_copiar = tk.Button(frame_parametros, text="Copiar para Excel", command=copiar_tabla_portapapeles, font=("Roboto", 12, "bold"), bg="#D392F1", fg="white")
    btn_copiar.grid(row=2, column=col_start + 6, rowspan=3, padx=10, pady=5, sticky="e")

    btn_exportar_csv = tk.Button(frame_parametros, text="Descargar CSV", command=exportar_a_csv, font=("Roboto", 12, "bold"), bg="#008CBA", fg="white")
    btn_exportar_csv.grid(row=4, column=col_start + 6, rowspan=3, padx=10, pady=5, sticky="e")

    ventana.mainloop()

if __name__ == "__main__":
    ventana_simulacion()