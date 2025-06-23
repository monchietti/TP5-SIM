import tkinter as tk
from tkinter import ttk, messagebox
from ManejadorEventos import ManejadorEventos
from Modelos.Clinica import Clinica
import tkinter.font as tkFont
from servicios.valoresRungeKutta import valoresRK


class InterfazSimulacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación - Vector de Estado")
        self.root.geometry("1400x750")

        # Entrada de parámetros
        frame_input = tk.Frame(root)
        frame_input.pack(pady=5)

        # Parámetros de simulación
        self.campos = {}
        parametros = [
            ("Simular N líneas:", "1000"),
            ("Mostrar desde la fila:", "0"),
            ("Tasa atención general:", "0.1"),
            ("Tasa atención emergencias:", "0.1667"),
            ("Llegada pacientes generales (min):", "0.3"),
            ("Llegada pacientes emergencia (min):", "0.2"),
        ]

        for label_text, valor_default in parametros:
            tk.Label(frame_input, text=label_text).pack(side="left", padx=2)
            entrada = tk.Entry(frame_input, width=6)
            entrada.insert(0, valor_default)
            entrada.pack(side="left", padx=2)
            self.campos[label_text] = entrada

        # Botón de simulación
        self.boton = tk.Button(frame_input, text="Iniciar Simulación", command=self.simular)
        self.boton.pack(side="left", padx=10)

        # Frame para tabla
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

        # Última fila
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

        self.tabla.bind("<ButtonRelease-1>", self.celda_clickeada)

    def simular(self):
        try:
            cantidad_lineas = int(self.campos["Simular N líneas:"].get())
            inicio = int(self.campos["Mostrar desde la fila:"].get())
            tasa_gen = float(self.campos["Tasa atención general:"].get())
            tasa_emer = float(self.campos["Tasa atención emergencias:"].get())
            llegada_gen = float(self.campos["Llegada pacientes generales (min):"].get())
            llegada_emer = float(self.campos["Llegada pacientes emergencia (min):"].get())

            if cantidad_lineas <= 0 or inicio < 0 or tasa_gen <= 0 or tasa_emer <= 0 or llegada_gen <= 0 or llegada_emer <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror("Error", "Verifica que todos los campos sean numéricos y mayores que cero.")
            return

        clinica = Clinica(tasa_gen, tasa_emer)
        manejador = ManejadorEventos(clinica)
        manejador.iniciar_simulacion(cantidad_lineas, llegada_gen, llegada_emer)

        vectores = manejador.historial_vector
        if not vectores:
            messagebox.showerror("Error", "No se generaron vectores.")
            return

        fin = min(inicio + 300, len(vectores))
        vista = vectores[inicio:fin]
        ultima_fila = vectores[-1]

        self.tabla.delete(*self.tabla.get_children())
        columnas = list(vista[-1].keys())[0:54 + 10*4]
        self.tabla["columns"] = columnas

        fuente = tkFont.Font()
        for col in columnas:
            ancho_texto = fuente.measure(col) + 20
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho_texto, anchor="center", minwidth=100)


        for fila in vista:
                valores = []
                for col in columnas:
                    try:
                        if fila[col] is None:
                            valores.append("---")
                        else:
                            valores.append(fila[col])
                    except Exception as e:
                        valores.append("---")
                self.tabla.insert("", "end", values=valores)



        self.tabla_ultima.delete(*self.tabla_ultima.get_children())
        self.tabla_ultima["columns"] = columnas

        for col in columnas:
            ancho_texto = fuente.measure(col) + 20
            self.tabla_ultima.heading(col, text=col)
            self.tabla_ultima.column(col, width=ancho_texto, anchor="center", minwidth=100)

        valores = [ultima_fila[col] for col in columnas]
        self.tabla_ultima.insert("", "end", values=valores)

    def celda_clickeada(self, event):
        region = self.tabla.identify("region", event.x, event.y)
        if region != "cell":
            return

        col_id = self.tabla.identify_column(event.x)
        col_index = int(col_id[1:]) - 1  # columnas empiezan en "#1"

        # Obtener el nombre de la columna clickeada
        col_name = self.tabla["columns"][col_index]
        if not col_name.startswith("T_resonancia"):
            return

        item_id = self.tabla.identify_row(event.y)
        if not item_id:
            return

        valores = self.tabla.item(item_id)["values"]

        # Suponiendo que "complejidad" está en una columna conocida
        # Podés ajustarlo si tenés el nombre de la columna
        try:
            numero_medico = col_name[-1]
            idx_complejidad = self.tabla["columns"].index(f"Complejidad{numero_medico}")
            complejidad = int(valores[idx_complejidad])
        except:
            messagebox.showerror("Error", "No se pudo determinar la complejidad.")
            return

        self.mostrar_matriz_runge_kutta(complejidad)

    def mostrar_matriz_runge_kutta(self, complejidad):
        matriz = valoresRK(complejidad)

        if not matriz:
            messagebox.showerror("Error", f"No hay matriz definida para complejidad {complejidad}.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title(f"Matriz Runge-Kutta - Complejidad {complejidad}")
        ventana.geometry("600x300")

        # Frame principal
        frame = tk.Frame(ventana)
        frame.pack(expand=True, fill="both")

        # Scrollbars
        scroll_y = ttk.Scrollbar(frame, orient="vertical")
        scroll_x = ttk.Scrollbar(frame, orient="horizontal")

        # Treeview como tabla
        tree = ttk.Treeview(frame, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        tree.pack(expand=True, fill="both")

        # Definir columnas según la cantidad de elementos
        columnas = ["t", "R", "K1", "t+h/2", "K2", "t+h * 1/2", "K3", "t+h", "K4", "Ri+1"]
        tree["columns"] = columnas

        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center", minwidth=60)

        # Cargar filas
        for i, fila in enumerate(matriz):
            valores = [str(x) for x in fila]
            item_id = tree.insert("", "end", values=valores)

            # Pintar última fila, primera columna
            if i == len(matriz) - 1:
                # Usar tag para estilizar
                tree.tag_configure("verde", background="#c8f7c5")  # verde suave
                tree.item(item_id, tags=("verde",))

        # Aplicar estilo más visible si lo deseas
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10))


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazSimulacion(root)
    root.mainloop()
