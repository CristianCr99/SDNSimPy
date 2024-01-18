# Clase flow_information, encargada de recopilar y ordenar (segun el instante de tiempo) la informacion relativa a un
# flujo particular.
class flow_information():

    # Constructor por defecto de la clase flow_information.
    def __init__(self, packet):
        self.packet = packet
        self.packet_delay_list = []

    # Getter del atributo packet.
    def get_packet(self):
        return self.packet

    # Getter del atributo packet_delay_list.
    def get_packet_delay_list(self):
        return self.packet_delay_list

    # Setter del atributo packet.
    def set_packet(self, packet):
        self.packet = packet

    # Setter del atributo packet_delay_list.
    def set_packet_delay_list(self, packet_delay_list):
        self.packet_delay_list = packet_delay_list

    # Funcion add_delay, encargada de aniadir a la lista de delay de un flujo un nuevo delay de un paquete
    # correspondiente a dicho flujo en un intsnate determinado (para hubicarlo ordenadamente en la lista segun
    # el instante de tiempo).
    def add_delay(self, delay, time_generation):
        j = 0
        for i in self.packet_delay_list:
            if time_generation < i[1]:
                self.packet_delay_list = self.packet_delay_list[:j] + [
                    (delay, time_generation)] + self.packet_delay_list[j:]
                return

            j += 1
        self.packet_delay_list.append((delay, time_generation))
