class RungeKuttaSolver:
    def f(self, t, C):
        return 0.5 * C + t

    def paso(self, t, R, C, h):
        # Método de Runge-Kutta de 4º orden
        k1 = (0.5 * C + t)
        k2 = (0.5 * C + (t + h/2))
        k3 = (0.5 * C + (t + h/2))
        k4 = (0.5 * C + t + h)
        return R + (k1 + 2*k2 + 2*k3 + k4) * h/ 6

    def calcular_RK(self, t, R, C, h):
        R_siguiente = R
        corte = 200
        if C == 20 or C == 50:
            corte = 100

        while R_siguiente < corte:
            R_siguiente = self.paso(t, R_siguiente, C, h)
            t += h

        return t