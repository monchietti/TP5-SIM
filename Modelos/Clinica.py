from Modelos.Servidor import Servidor
from Modelos.Cola import Cola

class Clinica:
    def __init__(self, tasa_consulta, tasa_emergencia):
        self.consulta_cola = Cola()
        self.emergencia_cola = Cola()
        self.servidores_consulta = [Servidor(i+1, "consulta", tasa_consulta) for i in range(2)]
        self.servidores_emergencia = [Servidor(i+1,"emergencia", tasa_emergencia) for i in range(2)]
        self.pacientes = []
