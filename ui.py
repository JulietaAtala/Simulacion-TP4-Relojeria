# ui.py (Major adaptations)
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from simulacion import Simulacion # Import the main simulation class

def ventana_simulacion():
    ventana = tk.Tk()
    ventana.title("Simulación de Relojería")
    ventana.geometry("1500x800") # Increased size for more columns

    # Configure grid to allow resizing
    ventana.grid_rowconfigure(2, weight=1)
    ventana.grid_columnconfigure(0, weight=1)

    # Frame for simulation parameters
    frame_parametros = tk.Frame(ventana, bd=2, relief="groove")
    frame_parametros.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    tk.Label(frame_parametros, text="Tiempo a simular (min):", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_tiempo_simulacion = tk.Entry(frame_parametros, width=10)
    entry_tiempo_simulacion.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    entry_tiempo_simulacion.insert(0, "480") # Default value for 8 hours in minutes

    tk.Label(frame_parametros, text="Mostrar desde hora (min):", font=("Roboto", 12, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_hora_desde = tk.Entry(frame_parametros, width=10)
    entry_hora_desde.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    entry_hora_desde.insert(0, "0") # Default value

    tk.Label(frame_parametros, text="Cantidad de iteraciones a mostrar:", font=("Roboto", 12, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_cant_iteraciones = tk.Entry(frame_parametros, width=10)
    entry_cant_iteraciones.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    entry_cant_iteraciones.insert(0, "50") # Default value

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
        "Cont. Clientes", "Cont. Reparaciones", "Porc. Ocup. Ayudante", "Porc. Ocup. Relojero", "Cola Max. Clientes"
    ]

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings')
    tabla.grid(row=0, column=0, sticky="nsew")

    # Configure column headings and widths
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120, anchor="center") # Adjust width as needed

    # Scrollbars
    scrollbar_horizontal = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=tabla.xview)
    scrollbar_horizontal.grid(row=1, column=0, sticky="ew")
    tabla.config(xscrollcommand=scrollbar_horizontal.set)

    scrollbar_vertical = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla.yview)
    scrollbar_vertical.grid(row=0, column=1, sticky="ns")
    tabla.config(yscrollcommand=scrollbar_vertical.set)

    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    def ejecutar_simulacion_y_mostrar():
        for i in tabla.get_children():
            tabla.delete(i) # Clear previous results

        try:
            tiempo_simulacion = float(entry_tiempo_simulacion.get())
            hora_desde = float(entry_hora_desde.get())
            cant_iteraciones = int(entry_cant_iteraciones.get())
        except ValueError:
            tk.messagebox.showerror("Error de entrada", "Por favor ingrese valores numéricos válidos.")
            return

        # Max iterations is set to 100000 as per requirements
        sim = Simulacion(tiempo_simulacion, 100000)
        vector_estado, estadisticas = sim.ejecutar_simulacion(tiempo_simulacion, cant_iteraciones, hora_desde)

        # Populate the Treeview with results, skipping the header row from sim.resultados_vector_estado
        for row in vector_estado[1:]: # Skip the headers row
            tabla.insert("", tk.END, values=row)

        # Update statistics labels
        label_prob_no_reparado.config(text=f"Prob. cliente retira no reparado: {estadisticas['prob_cliente_retira_no_listo']}")
        label_ocup_ayudante.config(text=f"Porc. ocupación ayudante: {estadisticas['porc_ocup_ayudante']}")
        label_ocup_relojero.config(text=f"Porc. ocupación relojero: {estadisticas['porc_ocup_relojero']}")
        label_cola_max.config(text=f"Cola máxima de clientes: {estadisticas['cola_max_clientes']}")


    btn_simular = tk.Button(frame_parametros, text="Simular", command=ejecutar_simulacion_y_mostrar, font=("Roboto", 12, "bold"), bg="#4CAF50", fg="white")
    btn_simular.grid(row=0, column=2, rowspan=3, padx=10, pady=5, sticky="e")

    ventana.mainloop()


if __name__ == "__main__":
     ventana_simulacion()