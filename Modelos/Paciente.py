class Paciente:
    _cont_pacientes = 0
    def __init__(self, tipo, tiempo_llegada):
        Paciente._cont_pacientes += 1
        self.id = Paciente._cont_pacientes
        self.tipo = tipo  # "consulta", "emergencia", "accidente"
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_salida_cola = None
        self.complejidad = None  # Solo si es accidente
        self.estado = None







