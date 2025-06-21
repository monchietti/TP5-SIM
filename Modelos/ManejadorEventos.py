import heapq
import random
import math
from os import truncate
import copy

from Modelos.Evento import Evento
from Modelos.Paciente import Paciente
from servicios.RungeKuttaSolver import RungeKuttaSolver

random.seed(24)

def truncar(numero):
    factor = 10 ** 2
    return int(numero * factor) / factor

def definir_complejidad(rnd_complejidad):
    if rnd_complejidad < 0.15:
        complejidad = 20
    elif rnd_complejidad >= 0.15 and rnd_complejidad < 0.5:
        complejidad = 50
    elif rnd_complejidad >= 0.5 and rnd_complejidad < 0.70:
        complejidad = 80
    elif rnd_complejidad >= 0.70 and rnd_complejidad < 1:
        complejidad = 100

    return complejidad


class ManejadorEventos:
    def __init__(self, clinica):
        self.rk_solver = RungeKuttaSolver()
        self.eventos = []  # heapq para mantener la cola de eventos ordenada
        self.clinica = clinica
        self.reloj = 0.0
        self.historial_vector = []


        self.vector = {
            "reloj":0,
            "evento":None,
            "RND_LLG": None, #llegada general
            "T_LLG": None,
            "H_LLG": None,
            "RND_LLE": None,
            "T_LLE": None,
            "H_LLE": None,
            "RND_FAG1": None, #fin atencion general 1
            "T_FAG1": None,
            "H_FAG1": None,
            "RND_FAG2": None,
            "T_FAG2": None,
            "H_FAG2": None,
            "RND_resonancia1": None, #si hay resonancia para el medico 1
            "Resonancia1": None,
            "RND_Complejidad1": None,
            "Complejidad1": None,
            "T_resonancia1": None,
            "RND_FAE1": None,  # fin atencion Emergencia 1
            "T_FAE1": None,
            "H_FAE1": None,
            "RND_resonancia2": None,  # si hay resonancia para el medico 1
            "Resonancia2": None,
            "RND_Complejidad2": None,
            "Complejidad2": None,
            "T_resonancia2": None,
            "RND_FAE2": None,
            "T_FAE2": None,
            "H_FAE2": None,
            "E_MG1": "Libre",
            "E_MG2": "Libre",
            "E_ME1": "Libre",
            "E_ME2": "Libre",
            "CG": 0,
            "CE": 0,
            "IOMG1": None, #Inicio ocupacion medico general/emergencias N (creo)
            "AcuMG1": 0, #Acumulador tiempo ocupacion Medico general/emergencias N
            "PorcOMG1": 0,
            "IOMG2": None,
            "AcuMG2": 0,
            "PorcOMG2": 0,
            "IOME1": None,
            "AcuME1": 0,
            "PorcOME1": 0,
            "IOME2": None,
            "AcuME2": 0,
            "PorcOME2": 0,
            "cant_pacientes_G": 0,
            "Acu_T_Espera_G" : 0,
            "Prom_T_Espera_G": 0,
            "cant_pacientes_E": 0,
            "Acu_T_Espera_E" : 0,
            "Prom_T_Espera_E": 0,
        }

    def agendar_evento(self, evento):
        heapq.heappush(self.eventos, evento)

    def proximo_evento(self):
        if self.eventos:
            return heapq.heappop(self.eventos)
        return None

    def generar_tiempo_exponencial(self, rnd, tasa):
        return truncar(-1/tasa * math.log(1- rnd))

    def iniciar_simulacion(self, cantidad_lineas):
        # Agendar primeras llegadas
        self.vector["reloj"] = 0
        self.vector["evento"] = "inicio simulacion"

        rnd1 = truncar(random.random())
        rnd2 = truncar(random.random())

        self.vector["RND_LLG"] = rnd1
        self.vector["RND_LLE"] = rnd2
        tiempo_llG = self.generar_tiempo_exponencial(rnd1, 18/60)
        tiempo_llE = self.generar_tiempo_exponencial(rnd2, 12/60)
        self.vector["T_LLG"] = tiempo_llG
        self.vector["T_LLE"] = tiempo_llE
        self.vector["H_LLG"] = tiempo_llG
        self.vector["H_LLE"] = tiempo_llE
        self.agendar_evento(Evento(self.reloj + tiempo_llG, "llegada_consulta"))
        self.agendar_evento(Evento(self.reloj + tiempo_llE, "llegada_emergencia"))
        lineas = 1
        while self.eventos and lineas < cantidad_lineas:
            lineas += 1
            evento = self.proximo_evento()
            self.reloj = truncar(evento.tiempo)
            self.vector["reloj"] = self.reloj
            self.procesar_evento(evento)
            self.vector["CG"] = len(self.clinica.consulta_cola.cola)
            self.vector["CE"] = len(self.clinica.emergencia_cola.cola)
            #para cada servidor mostrar la ocupacion
            for servidor in self.clinica.servidores_consulta:
                self.vector[f"IOMG{servidor.id}"] = servidor.inicio_ocupacion
                self.vector[f"AcuMG{servidor.id}"] = servidor.acumulador_ocupacion
                self.vector[f"PorcOMG{servidor.id}"] = servidor.porcentaje_ocupacion(self.reloj)

            for servidor in self.clinica.servidores_emergencia:
                self.vector[f"IOME{servidor.id}"] = servidor.inicio_ocupacion
                self.vector[f"AcuME{servidor.id}"] = servidor.acumulador_ocupacion
                self.vector[f"PorcOME{servidor.id}"] = servidor.porcentaje_ocupacion(self.reloj)

            #carga pacientes en vector estado
            for paciente in self.clinica.pacientes:

                self.vector[f"id_paciente_{paciente.id}"] = paciente.id
                self.vector[f"estado_paciente_{paciente.id}"] = paciente.estado
                self.vector[f"Hora_llegada_paciente_{paciente.id}"] = paciente.tiempo_llegada
                if paciente.tiempo_salida_cola:
                    tiempo_en_cola = paciente.tiempo_salida_cola - paciente.tiempo_llegada
                    self.vector[f"Tiempo_en_cola_paciente_{paciente.id}"] = tiempo_en_cola
                else:
                    self.vector[f"Tiempo_en_cola_paciente_{paciente.id}"] = None
            self.historial_vector.append(copy.deepcopy(self.vector))

    def procesar_evento(self, evento):
        if evento.tipo_evento == "llegada_consulta":
            paciente = Paciente("consulta", self.reloj)
            self.vector["evento"] = f"llegada consulta paciente {paciente.id}"
            self.clinica.pacientes.append(paciente)
            self.clinica.consulta_cola.agregar(paciente)
            paciente.estado = "en cola consulta"
            rnd1 = truncar(random.random())
            self.vector["RND_LLG"] = rnd1
            tiempo_llG = self.generar_tiempo_exponencial(rnd1, 18/60)
            self.vector["T_LLG"] = tiempo_llG
            self.vector["H_LLG"] = self.reloj + tiempo_llG
            self.agendar_evento(Evento(self.reloj + tiempo_llG, "llegada_consulta"))
            self.asignar_servidor(paciente, "consulta")

        elif evento.tipo_evento == "llegada_emergencia":
            tipo = "emergencia"
            paciente = Paciente(tipo, self.reloj)
            self.vector["evento"] = f"llegada emergencia paciente {paciente.id}"
            self.clinica.pacientes.append(paciente)
            paciente.estado = "en cola emergencia"
            self.clinica.emergencia_cola.agregar(paciente)
            rnd1 = truncar(random.random())
            self.vector["RND_LLE"] = rnd1
            tiempo_llE = self.generar_tiempo_exponencial(rnd1, 12/60)
            self.vector["T_LLE"] = tiempo_llE
            self.vector["H_LLE"] = self.reloj + tiempo_llE
            self.agendar_evento(Evento(self.reloj + tiempo_llE, "llegada_emergencia"))
            self.asignar_servidor(paciente, "emergencia")

        elif evento.tipo_evento == "fin_atencion":
            evento.paciente.estado = "atendido"
            servidor = evento.paciente.servidor

            #llenado vector estado
            if servidor.tipo == "emergencia":

                self.vector[f"E_ME{servidor.id}"] = "Libre"
                self.vector[f"RND_FAE{servidor.id}"] = None
                self.vector[f"T_FAE{servidor.id}"] = None
                self.vector[f"H_FAE{servidor.id}"] = None
                self.vector[f"RND_resonancia{servidor.id}"] = None
                self.vector[f"Resonancia{servidor.id}"] = None
                self.vector[f"RND_Complejidad{servidor.id}"] = None
                self.vector[f"Complejidad{servidor.id}"] = None
                self.vector[f"T_resonancia{servidor.id}"] = None
            else:
                self.vector[f"E_MG{servidor.id}"] = "Libre"
                self.vector[f"RND_FAG{servidor.id}"] = None
                self.vector[f"T_FAG{servidor.id}"] = None
                self.vector[f"H_FAG{servidor.id}"] = None

            self.vector["evento"] = f"fin atencion {servidor.tipo} paciente {evento.paciente.id}"
            servidor.ocupado = False
            servidor.paciente_actual = None

            #contador de pacientes
            if servidor.tipo == "emergencia":
                self.vector[f"cant_pacientes_E"] += 1
            else:
                self.vector[f"cant_pacientes_G"] += 1


            self.asignar_servidor_a_cola(servidor.tipo)
            if not servidor.ocupado:
                servidor.acumulador_ocupacion += self.reloj - servidor.inicio_ocupacion
                servidor.inicio_ocupacion = None


    def asignar_servidor(self, paciente, tipo):
        servidores = self.clinica.servidores_consulta if tipo == "consulta" else self.clinica.servidores_emergencia
        cola = self.clinica.consulta_cola if tipo == "consulta" else self.clinica.emergencia_cola

        for servidor in servidores:
            #se asigna un servidor libre a un cliente
            if not servidor.ocupado:
                servidor.inicio_ocupacion = self.reloj
                servidor.ocupado = True
                servidor.paciente_actual = paciente
                paciente.servidor = servidor
                paciente.estado = "siendo atendido"
                paciente.tiempo_salida_cola = self.reloj
                rnd = truncar(random.random())
                duracion = self.generar_tiempo_exponencial(rnd, servidor.tasa_atencion)
                duracion_consulta = duracion
                if tipo == "emergencia":
                    #acumulador tiempo en cola de los pacientes emergencia
                    self.vector[f"Acu_T_Espera_E"] += paciente.tiempo_salida_cola - paciente.tiempo_llegada
                    # promedio de tiempo de espera en cola de pacientes de emergencia atendidos
                    if self.vector[f"cant_pacientes_E"] != 0:
                        self.vector["Prom_T_Espera_E"] = self.vector[f"Acu_T_Espera_E"] / self.vector[f"cant_pacientes_E"]



                    #se calcula si hubo o no accidentes para las emergencias
                    rnd_resonancia = truncar(random.random())
                    tipo = "accidente" if rnd_resonancia < 0.2 else "emergencia"
                    if tipo == "accidente":
                        self.vector[f"RND_resonancia{servidor.id}"] = rnd_resonancia
                        self.vector[f"Resonancia{servidor.id}"] = "SI"
                        rnd_complejidad = truncar(random.random())
                        self.vector[f"RND_Complejidad{servidor.id}"] = rnd_complejidad
                        paciente.complejidad = definir_complejidad(rnd_complejidad)
                        self.vector[f"Complejidad{servidor.id}"] = paciente.complejidad
                        tiempo_resonancia = self.rk_solver.calcular_RK(0, 0, paciente.complejidad, 0.1)
                        self.vector[f"T_resonancia{servidor.id}"] = tiempo_resonancia
                        duracion = duracion + tiempo_resonancia

                servidor.tiempo_fin_atencion = self.reloj + duracion
                self.agendar_evento(Evento(servidor.tiempo_fin_atencion, "fin_atencion", paciente))
                cola.siguiente()  # saca el primer elemento de la cola (el paciente atendido)
                if tipo == "consulta":
                    #acumulador de tiempo en cola de los pacientes generales
                    self.vector[f"Acu_T_Espera_G"] += paciente.tiempo_salida_cola - paciente.tiempo_llegada
                    # promedio de tiempo de espera en cola de pacientes generales atendidos
                    if self.vector[f"cant_pacientes_G"] != 0:
                        self.vector["Prom_T_Espera_G"] = self.vector[f"Acu_T_Espera_G"] / self.vector[f"cant_pacientes_G"]

                    self.vector[f"RND_FAG{servidor.id}"] = rnd
                    self.vector[f"T_FAG{servidor.id}"] = duracion_consulta
                    self.vector[f"H_FAG{servidor.id}"] = duracion + self.reloj
                    self.vector[f"E_MG{servidor.id}"] = "Ocupado"
                else:
                    self.vector[f"RND_FAE{servidor.id}"] = rnd
                    self.vector[f"T_FAE{servidor.id}"] = duracion_consulta
                    self.vector[f"H_FAE{servidor.id}"] = duracion + self.reloj
                    self.vector[f"E_ME{servidor.id}"] = "Ocupado"
                break

    def asignar_servidor_a_cola(self, tipo): #consulta si hay otro cliente en la cola segun el tipo
        cola = self.clinica.consulta_cola if tipo == "consulta" else self.clinica.emergencia_cola
        if cola.cola:
            paciente = cola.cola[0] #saca el primer cliente de la cola
            self.asignar_servidor(paciente, tipo)


