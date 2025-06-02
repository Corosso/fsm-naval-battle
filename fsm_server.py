class Barco:
    def __init__(self, coordenadas):
        self.coordenadas = set(coordenadas)
        self.impactos = set()

    def recibir_impacto(self, coord):
        if coord in self.coordenadas:
            self.impactos.add(coord)
            return True
        return False

    def esta_hundido(self):
        return self.coordenadas == self.impactos


class FSMServer:
    def __init__(self, lista_barcos):
        self.q1 = "q1"  # Flota intacta
        self.q2 = "q2"  # Impactado
        self.q3 = "q3"  # Hundido
        self.q4 = "q4"  # Derrota
        self.state = self.q1
        self.barcos = [Barco(coords) for coords in lista_barcos]  # lista de listas
        self.historial = set()  # para evitar disparos repetidos

    def process_message(self, msg):
        valid_coords = [f"{chr(r)}{c}" for r in range(65, 70) for c in range(1, 6)]

        if msg == "A0":
            return "200 OK"
        if msg == "GET_SHIPS":
            todas = [c for barco in self.barcos for c in barco.coordenadas]
            return ",".join(sorted(todas))

        if msg not in valid_coords:
            return "404 Not Found"
        if msg in self.historial:
            return "404-fallido"  # disparo repetido = agua

        self.historial.add(msg)

        for barco in self.barcos:
            if barco.recibir_impacto(msg):
                if barco.esta_hundido():
                    if all(b.esta_hundido() for b in self.barcos):
                        self.state = "q4"
                        return "500-hundido"
                    else:
                        self.state = "q3"
                        return "200-hundido"
                else:
                    self.state = "q2"
                    return "202-impactado"


        return "404-fallido"
