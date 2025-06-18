from Modelos.Servidor import Servidor
from Modelos.Cola import Cola

class Clinica:
    def __init__(self):
        self.consulta_cola = Cola()
        self.emergencia_cola = Cola()
        self.servidores_consulta = [Servidor(i+1, "consulta", 6/60) for i in range(2)]
        self.servidores_emergencia = [Servidor(i+1,"emergencia", 10/60) for i in range(2)]
        self.pacientes = []
