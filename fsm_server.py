
HOST = 'localhost'
PORT = 65432
#clase para manejar el servidor FSM
class FSMServer:
    def __init__(self, barcos):
        self.state = "WAITING"
        self.barcos = set(barcos)
        self.hits = set()

    def process_message(self, msg):
        valid_coords = [f"{chr(r)}{c}" for r in range(65, 70) for c in range(1, 6)]

        if msg == "A0":
            return "200 OK"
        if msg == "GET_SHIPS":
            respuesta = ",".join(self.barcos)  # barcos es la lista o set con las posiciones de los barcos            
            return respuesta
        elif msg not in valid_coords:
            return "404 Not Found"
        elif msg in self.barcos:
            self.hits.add(msg)
            if self.hits == self.barcos:
                return "WIN"  # Todos los barcos hundidos
            else:
                return "HIT"
        else:
            return "MISS"
