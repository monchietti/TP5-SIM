import tkinter as tk
from tkinter import ttk, messagebox
from ManejadorEventos import ManejadorEventos
from Modelos.Clinica import Clinica  # Asegurate de tener esta clase
import copy
import tkinter.font as tkFont  # Asegurate de importar esto arriba


class InterfazSimulacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación - Vector de Estado")
        self.root.geometry("1400x700")  # Ventana más grande

        # Entrada de parámetros
        frame_input = tk.Frame(root)
        frame_input.pack(pady=5)

        # Cantidad de líneas
        tk.Label(frame_input, text="Simular N líneas:").pack(side="left")
        self.entrada_n = tk.Entry(frame_input, width=6)
        self.entrada_n.pack(side="left", padx=5)
        self.entrada_n.insert(0, "1000")  # valor por defecto

        # Fila de inicio
        tk.Label(frame_input, text="Mostrar desde la fila:").pack(side="left")
        self.entrada_inicio = tk.Entry(frame_input, width=6)
        self.entrada_inicio.pack(side="left")
        self.entrada_inicio.insert(0, "0")

        # Botón
        self.boton = tk.Button(frame_input, text="Iniciar Simulación", command=self.simular)
        self.boton.pack(side="left", padx=10)

        # Frame para tabla y scroll
        frame_tabla = tk.Frame(root)
        frame_tabla.pack(expand=True, fill="both")

        self.scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical")
        self.scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")

        self.tabla = ttk.Treeview(
            frame_tabla,
            show="headings",
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )

        self.scroll_y.config(command=self.tabla.yview)
        self.scroll_x.config(command=self.tabla.xview)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        # Última fila del vector
        # Frame para mostrar la última fila
        frame_ultima = tk.Frame(root)
        frame_ultima.pack(fill="both", padx=10, pady=5)

        tk.Label(frame_ultima, text="Última fila del vector de estado:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.scroll_x_ultima = ttk.Scrollbar(frame_ultima, orient="horizontal")
        self.tabla_ultima = ttk.Treeview(
            frame_ultima,
            show="headings",
            xscrollcommand=self.scroll_x_ultima.set,
            height=1
        )
        self.scroll_x_ultima.config(command=self.tabla_ultima.xview)

        self.tabla_ultima.pack(side="top", fill="x")
        self.scroll_x_ultima.pack(side="bottom", fill="x")

    def simular(self):
        try:
            cantidad_lineas = int(self.entrada_n.get())
            if cantidad_lineas <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido de líneas (> 0)")
            return

        try:
            inicio = int(self.entrada_inicio.get())
            if inicio < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para el inicio.")
            return

        clinica = Clinica()
        manejador = ManejadorEventos(clinica)
        manejador.iniciar_simulacion(cantidad_lineas)

        vectores = manejador.historial_vector
        if not vectores:
            messagebox.showerror("Error", "No se generaron vectores.")
            return

        fin = min(inicio + 300, len(vectores))
        vista = vectores[inicio:fin]
        ultima_fila = vectores[-1]

        self.tabla.delete(*self.tabla.get_children())
        # no mostrar cada paciente (esto se tiene que cambiar)
        columnas = list(vista[0].keys())[0:50]
        self.tabla["columns"] = columnas

        # Calcular el ancho dinámico según el texto del encabezado
        fuente = tkFont.Font()
        for col in columnas:
            ancho_texto = fuente.measure(col) + 20  # ancho del texto + padding
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho_texto, anchor="center", minwidth=100)

        n = 0
        for fila in vista:
            valores = [fila[col] for col in columnas]
            n += 1
            self.tabla.insert("", "end", values=valores)

        resumen = "\n".join([f"{clave}: {valor}" for clave, valor in ultima_fila.items()])
        # Mostrar última fila del vector de estado de forma horizontal
        self.tabla_ultima.delete(*self.tabla_ultima.get_children())
        self.tabla_ultima["columns"] = columnas

        for col in columnas:
            ancho_texto = fuente.measure(col) + 20
            self.tabla_ultima.heading(col, text=col)
            self.tabla_ultima.column(col, width=ancho_texto, anchor="center", minwidth=100)

        valores = [ultima_fila[col] for col in columnas]
        self.tabla_ultima.insert("", "end", values=valores)


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazSimulacion(root)
    root.mainloop()

