# Clase DiscreteEvents, encargada de recopilar la informacion de los eventeos que tienen lugar en la red junto a los
# diferentes paquetes geredados por los hosts y aquellos paquetes generados a partir de estos.
class DiscreteEvents:

    # Contructor parametrizado de la clase DiscreteEvents.
    def __init__(self, initial_event_list=None, initial_packets_list=None, initial_openflow_list=None):
        self.list_events = initial_event_list
        self.list_packets = initial_packets_list
        self.list_packets_openflow = initial_openflow_list

    # Getter get_list_events, encargado de devolver la lista de eventos.
    def get_list_events(self):
        return self.list_events

    # Getter del atributo list_packets.
    def get_list_packets(self):
        return self.list_packets

    # Getter del atributo list_packets_openflow.
    def get_list_packets_openflow(self):
        return self.list_packets_openflow

    # Funcion queue_list_events, encargada de encolar en la lista de eventos un nuevo evento.
    def queue_list_events(self, x):
        self.list_events.append(x)  # encolamos al final de la lista

    # Funcion unqueue_list_events, encargada de desencolar un evento de la lista de eventos (el primer evento de la cola
    # ), devolviendo 0 si no hay eventos.
    def unqueue_list_events(self):
        try:
            return self.list_events.pop(0)
        except:
            return 0

    # Funcion is_empty_list_events, edvuelve True si la cola esta vacía, False si no lo esta.
    def is_empty_list_events(self):
        return self.list_events == []

    # Funcion inser_event, encargado de insertar un evento en la cola de eventos en la posicion en la cual le
    # corresponde dependiendo del tiempo de tratamiento de dicho evento.
    def inser_event(self, new_event):
        j = 0
        for event in self.list_events:
            if event['time_spawn'] > new_event['time_spawn']:
                self.list_events = self.list_events[:j] + [new_event] + self.list_events[j:]
                return
            j += 1
        self.list_events.append(new_event)
