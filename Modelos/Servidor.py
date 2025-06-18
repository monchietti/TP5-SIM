class Servidor:

    def __init__(self,id, tipo, tasa_atencion):
        self.id = id
        self.tipo = tipo  # "consulta" o "emergencia"
        self.tasa_atencion = tasa_atencion
        self.ocupado = False
        self.paciente_actual = None
        self.tiempo_fin_atencion = None
        self.inicio_ocupacion = None
        self.acumulador_ocupacion = 0

    def porcentaje_ocupacion(self, reloj):
        return self.acumulador_ocupacion / reloj * 100
