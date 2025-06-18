class Cola: #iterator
    def __init__(self):
        self.cola = []

    def tamanio(self):
        return len(self.cola)


    def agregar(self, paciente):
        self.cola.append(paciente)

    def siguiente(self):
        if self.cola:
            return self.cola.pop(0)
        return None