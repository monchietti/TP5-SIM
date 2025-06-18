from Modelos.Clinica import Clinica
from Modelos.ManejadorEventos import ManejadorEventos

me = ManejadorEventos(Clinica())

me.iniciar_simulacion(50)

