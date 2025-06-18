import heapq
import random
import math

class Evento:
    def __init__(self, tiempo, tipo_evento, paciente=None):
        self.tiempo = tiempo
        self.tipo_evento = tipo_evento  # "llegada_consulta", "llegada_emergencia", "fin_atencion", etc.
        self.paciente = paciente

    def __lt__(self, otro):
        return self.tiempo < otro.tiempo


