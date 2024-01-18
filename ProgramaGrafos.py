from __future__ import print_function

import uuid
from builtins import range

import networkx as nx
from scapy.layers.inet import *


# Clase FlowEntry, encargada principalmente de  simular la estructura de una entrada de flujo de un switch openflow
# conteniendo asi, todos los campos correspondientes de dicha entrada de flujo y las funciones para acceder a dichos
# campos.
class FlowEntry:

    # Constructor parametrizado de la clase FlowEntry.
    def __init__(self, mac_src, mac_dst, ip_src, ip_dst, transport_protocol, port_src, port_dst, action):
        self.mac_src = mac_src
        self.mac_dst = mac_dst
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.port_src = port_src
        self.port_dst = port_dst
        self.transport_protocol = transport_protocol
        self.counter_packet_number = 0
        self.counter_packet_byte = 0
        self.action = action

    # Getter del atributo mac_src.
    def get_ip_src(self):
        return (self.ip_src)

    # Getter del atributo mac_dst.
    def get_ip_dst(self):
        return (self.ip_dst)

    # Getter del atributo ip_src.
    def get_mac_src(self):
        return (self.mac_src)

    # Getter del atributo ip_dst.
    def get_mac_dst(self):
        return (self.mac_dst)

    # Getter del atributo port_src.
    def get_port_src(self):
        return (self.port_src)

    # Getter del atributo port_dst.
    def get_port_dst(self):
        return (self.port_dst)

    # Getter del atributo transport_protocol.
    def get_transport_protocol(self):
        return (self.transport_protocol)

    # Getter del atributo counter_packet_number.
    def get_action(self):
        return (self.action)

    # Getter del atributo counter_packet_byte.
    def get_counter_packet_number(self):
        return self.counter_packet_number

    # Getter del atributo action.
    def get_counter_packet_byte(self):
        return self.counter_packet_byte

    # Setter del atributo counter_packet_number.
    def set_counter_packet_number(self, counter_packet_number):
        self.counter_packet_number = counter_packet_number

    # Setter del atributo counter_packet_byte.
    def set_counter_packet_byte(self, counter_packet_byte):
        self.counter_packet_byte = counter_packet_byte


# Clase NetworkTopology, encargada de recoger la topologia de nuestro simulador, con las caracteristicas de los
# diferentes nodos de la red (hosts, switches, controladores y enlaces) y las diferentes funciones para el tratamiento
# de la informacion en los mismos.
class NetworkTopology(object):

    # Constructor por defecto de la clase NetworkTopology.
    def __init__(self):
        self.G = nx.Graph()
        self.proactive = True

    # Getter del atributo G.
    def get_graph(self):
        return (self.G)

    # Setter del atributo G.
    def set_graph(self, G):
        self.G = G

    # Funcion add_switch, encargada de aniadir un switch junto a su lista de tablas de flujo como atributo de dicho
    # nodo.
    def add_switch(self, num_switch, flow_table=[]):
        self.G.add_node(num_switch, type='switch', name='s' + str(num_switch), flow_table=flow_table)

    # Funcion add_host, encargada de aniadir un host al grafo.
    def add_host(self, num_host):
        self.G.add_node(num_host, type='host', name='h' + str(num_host))

    # Funcion add_controller, encargada de aniadir un controlador al grafo.
    def add_controller(self, num_controller):
        self.G.add_node(num_controller, type='controller', name='c' + str(num_controller))

    # Funcion add_link, encargada de aniadir un nuevo enlace a nuestro nodo (junto al peso y a la carga asociada a dicho
    # enlace).
    def add_link(self, node_a, node_b, weight_link):
        self.G.add_edge(node_a, node_b, weight=weight_link, load=[])

    # Funcion add_flow_entry_to_node, encargada de aniadir una nueva entrada de flujo a un nodo (switch) concreto.
    def add_flow_entry_to_node(self, node, flowentry):

        for flowent in self.G.nodes[node]['flow_table']:
            if flowent.get_mac_src() == flowentry.get_mac_src() and flowent.get_mac_dst() == flowentry.get_mac_dst() and flowent.get_ip_src() == flowentry.get_ip_src() and flowent.get_ip_dst() == flowentry.get_ip_dst() and flowent.get_port_src() == flowentry.get_port_src() and flowent.get_port_dst() == flowentry.get_port_dst() and flowent.get_transport_protocol() == flowentry.get_transport_protocol():
                return
        self.G.nodes[node]['flow_table'].append(flowentry)

    # Setter del atributo list_Packets_to_send.
    def set_list_packets_to_send(self, list):
        self.list_Packets_to_send = list

    # Funcion match_and_action, encargada de comprobar un paquete determinado hace matching con alguna entrada de flujo
    # de la tabla de flujo de un switch concreto.
    def match_and_action(self, switch, packet):

        for i in (self.G.nodes[switch]['flow_table']):

            if 'TCP' in packet:
                protocol = 'TCP'
            else:
                protocol = 'UDP'

            if i.get_mac_src() == packet[Ether].src or i.get_mac_src() == '*' and i.get_mac_dst() == packet[
                Ether].src or i.get_mac_dst() == '*' \
                    and i.get_ip_src() == packet[IP].src and i.get_ip_dst() == packet[
                IP].dst and i.get_transport_protocol() == protocol \
                    and i.get_port_src() == packet[protocol].sport and i.get_port_dst() == packet[protocol].dport:
                i.set_counter_packet_number(i.get_counter_packet_number() + 1)
                i.set_counter_packet_byte(i.get_counter_packet_byte() + len(packet))

                return i.get_action()
        return 0

    # Funcion find_hosts_by_ip_packet, encargada de buscar el host de la topologia con el direccionamiento del paquete
    # pasado como argumento.
    def find_hosts_by_ip_packet(self, packet):
        src_host = None
        dst_host = None
        for i in list(self.G.nodes):
            if i[0] == 'h':
                if self.G.nodes[i]['ip'] == packet[IP].src:
                    src_host = i
                if self.G.nodes[i]['ip'] == packet[IP].dst:
                    dst_host = i
        return src_host, dst_host

    # Funcion controller_action. Esta contiene la logica del controlador y devuelve la accion a realizar.
    def controller_action(self, miniNAM, packet, src_host, dst_host, switch, proactive):

        path = nx.dijkstra_path(self.G, src_host, dst_host, weight='bw')

        if 'TCP' in packet:
            protocol = 'TCP'
        else:
            protocol = 'UDP'

        for i in range(1, len(path) - 1):

            if proactive == True and path[i]:
                miniNAM.display_multiple_packet('c0', path[i], None, True, 'Flow_Mod', 'c0' + '->' + path[i])
                self.add_flow_entry_to_node(path[i], FlowEntry('*', '*', packet[IP].src,
                                                               packet[IP].dst, protocol, packet[protocol].sport,
                                                               packet[protocol].dport, path[i + 1]))

            if path[i] == switch:
                action = path[i + 1]

        miniNAM.displayPacket('c0', switch, None, True, 'Packet_Out', 'c0' + '->' + switch)
        return action

    # Funcion processing_event_packet_generation, encargada de tratar los eventos de tipo generacion de paquetes y
    # se encarga de generar eventos de propagacion de paquetes.
    def processing_event_packet_generation(self, event, list_packets):

        src_host, dst_host = self.find_hosts_by_ip_packet(list_packets[event['packet_id']])

        if src_host is not None and dst_host is not None:

            if self.G.degree(src_host) >= 1:  # Puede estar conectado a mas de un switch

                listEnlaces = list(self.G.edges(src_host))
                Switch = tuple(listEnlaces[0])[1]  # Cogemos el Switch al cual esta conectado [1]

                event = {'type': 'packet_propagation',
                         'src': src_host,
                         'dst': Switch,
                         'time_spawn': event['time_spawn'],
                         'packet_id': event['packet_id']
                         }
            return event
        return 0

    # Funcion processing_event_packet_propagation2, encargada de procesar los eventos de tipo propagacion. Ademas,
    # una vez tradatos dichos eventos, genera eventos de procesamiento (en el nodo de destino del enlace) de los
    # paquetes propagados por un enlace determinado y realiza la animacion del paquete propagandose por un enlace.
    def processing_event_packet_propagation2(self, event, list_packets, list_openflow, miniNAM):

        if miniNAM.appPrefs['flowTime'] == 30:
            animation_propagation_time = 3.5
        else:
            animation_propagation_time = 1.0

        if event['dst'] == 'c0' or event['src'] == 'c0':
            propagation_delay = 0.06 + animation_propagation_time
            is_openflow = True
            type_message = list_openflow[event['openflow_id']]['type']
            load_packet = list_openflow[event['openflow_id']]['size']
        else:

            load_packet = len(list_packets[event['packet_id']])
            propagation_delay = (self.G.edges[event['src'], event['dst']]['distance'] / \
                                 self.G.edges[event['src'], event['dst']]['propagation_speed'] + load_packet /
                                 (1 / self.G.edges[event['src'], event['dst']]['bw'])) + animation_propagation_time
            is_openflow = False
            type_message = None

        if 'load' in self.G.edges[event['src'], event['dst']] and len(
                self.G.edges[event['src'], event['dst']]['load']) > 0:
            last_load = self.G.edges[event['src'], event['dst']]['load'][-1][1]
        else:
            last_load = 0

        new_load = last_load + load_packet

        if 'load' in self.G.edges[event['src'], event['dst']]:
            print((float(event['time_spawn']), new_load))
            self.G.edges[event['src'], event['dst']]['load'].append((float(event['time_spawn']), new_load))  # TODO ooooooooooo

        if event['dst'] == 'c0':
            type = 'packet_processing_controller'
        elif event['dst'][0] == 'h':
            type = 'packet_processing_host'
        else:
            type = 'packet_processing_switch'

        src_host, dst_host = self.find_hosts_by_ip_packet(list_packets[event['packet_id']])

        # Con esta funcion lanzamos la animacion del movimiento de un paquete (ejecutado por un hilode forma
        # simultranea)
        miniNAM.display_multiple_packet(event['src'], event['dst'], list_packets[event['packet_id']], is_openflow,
                                        type_message, src_host + '->' + dst_host, propagation_delay)

        if 'openflow_id' in event:
            event = {'type': type,
                     'src': event['src'],
                     'dst': event['dst'],
                     'time_spawn': event['time_spawn'] + propagation_delay,
                     'packet_id': event['packet_id'],
                     'openflow_id': event['openflow_id']
                     }
            return event
        else:
            event = {'type': type,
                     'src': event['src'],
                     'dst': event['dst'],
                     'time_spawn': event['time_spawn'] + propagation_delay,
                     'packet_id': event['packet_id']
                     }
            return event

    # Funcion processing_event_packet_match_and_action_switch, encargada de procesar eventos de procesamiento de
    # paquetes en un switch, generando los diferentes eventos (de propagacion de paquetes) tras el procesamiento de
    # estos.
    def processing_event_packet_match_and_action_switch(self, event, list_packets, list_openflow):
        if 'openflow_id' in event:
            if list_openflow[event['openflow_id']]['type'] == 'packet_out':
                if 'TCP' in list_packets[event['packet_id']]:
                    protocol = 'TCP'
                else:
                    protocol = 'UDP'

                self.add_flow_entry_to_node(event['dst'], FlowEntry('*', '*', list_packets[event['packet_id']][IP].src,
                                                                    list_packets[event['packet_id']][IP].dst, protocol,
                                                                    list_packets[event['packet_id']][protocol].sport,
                                                                    list_packets[event['packet_id']][protocol].dport,
                                                                    list_openflow[event['openflow_id']]['action']))

                if 'load' in self.G.edges[event['src'], event['dst']] and len(
                        self.G.edges[event['src'], event['dst']]['load']) > 0:
                    last_load = self.G.edges[event['src'], event['dst']]['load'][-1][1]
                else:
                    last_load = 0
                load_packet = list_openflow[event['openflow_id']]['size']
                new_load = last_load - load_packet
                if 'load' in self.G.edges[event['src'], event['dst']]:
                    self.G.edges[event['src'], event['dst']]['load'].append((event['time_spawn'], new_load))  # TODO ooo

                event = {'type': 'packet_propagation',
                         'src': event['dst'],
                         'dst': list_openflow[event['openflow_id']]['action'],
                         'time_spawn': event['time_spawn'] + 0.1 + 0.1,  # TODO Preguntar esta parte :(
                         'packet_id': event['packet_id']
                         }

                return event
            elif list_openflow[event['openflow_id']]['type'] == 'flow_mood':
                if 'TCP' in list_packets[event['packet_id']]:
                    protocol = 'TCP'
                else:
                    protocol = 'UDP'
                self.add_flow_entry_to_node(event['dst'], FlowEntry('*', '*', list_packets[event['packet_id']][IP].src,
                                                                    list_packets[event['packet_id']][IP].dst, protocol,
                                                                    list_packets[event['packet_id']][protocol].sport,
                                                                    list_packets[event['packet_id']][protocol].dport,
                                                                    list_openflow[event['openflow_id']]['action']))

                if 'load' in self.G.edges[event['src'], event['dst']] and len(
                        self.G.edges[event['src'], event['dst']]['load']) > 0:
                    last_load = self.G.edges[event['src'], event['dst']]['load'][-1][1]
                else:
                    last_load = 0
                load_packet = list_openflow[event['openflow_id']]['size']
                new_load = last_load - load_packet

                if 'load' in self.G.edges[event['src'], event['dst']]:
                    self.G.edges[event['src'], event['dst']]['load'].append((event['time_spawn'], new_load))  # TODO ooo

                return 0
        else:
            for i in (self.G.nodes[event['dst']]['flow_table']):
                packet = list_packets[event['packet_id']]
                if 'TCP' in packet:
                    protocol = 'TCP'
                else:
                    protocol = 'UDP'

                if i.get_mac_src() == packet[Ether].src or i.get_mac_src() == '*' and i.get_mac_dst() == packet[
                    Ether].dst or i.get_mac_dst() == '*' \
                        and i.get_ip_src() == packet[IP].src and i.get_ip_dst() == packet[
                    IP].dst and i.get_transport_protocol() == protocol \
                        and i.get_port_src() == packet[protocol].sport and i.get_port_dst() == packet[protocol].dport:
                    i.set_counter_packet_number(i.get_counter_packet_number() + 1)
                    i.set_counter_packet_byte(i.get_counter_packet_byte() + len(packet))

                    if 'load' in self.G.edges[event['src'], event['dst']] and len(
                            self.G.edges[event['src'], event['dst']]['load']) > 0:
                        last_load = self.G.edges[event['src'], event['dst']]['load'][-1][1]
                    else:
                        last_load = 0
                    load_packet = len(packet)
                    new_load = last_load - load_packet

                    if 'load' in self.G.edges[event['src'], event['dst']]:
                        self.G.edges[event['src'], event['dst']]['load'].append(
                            (event['time_spawn'], new_load))  # TODO ooo

                    event = {'type': 'packet_propagation',
                             'src': event['dst'],
                             'dst': i.get_action(),
                             'time_spawn': event['time_spawn'] + 0.1,
                             'packet_id': event['packet_id']
                             }
                    return event

            packet = list_packets[event['packet_id']]
            if 'load' in self.G.edges[event['src'], event['dst']] and len(
                    self.G.edges[event['src'], event['dst']]['load']) > 0:
                last_load = self.G.edges[event['src'], event['dst']]['load'][-1][1]
            else:
                last_load = 0

            load_packet = len(packet)
            new_load = last_load - load_packet

            if 'load' in self.G.edges[event['src'], event['dst']]:
                self.G.edges[event['src'], event['dst']]['load'].append((event['time_spawn'], new_load))  # TODO ooo
        id = uuid.uuid4()
        event = {'type': 'packet_propagation',
                 'src': event['dst'],
                 'dst': 'c0',
                 'time_spawn': event['time_spawn'] + 0.1,
                 'packet_id': event['packet_id'],
                 'openflow_id': id
                 }
        list_openflow[id] = {'type': 'packet_in', 'size': 50}
        return event

    # Funcion processing_event_packet_controller_action, encargado de procesar los eventos de procesamiento en el
    # controlador. Esta funcion genera eventos de propagacion correspondientes a mensajes OpenFlow.
    def processing_event_packet_controller_action(self, event, list_packets, list_openflow_messages,
                                                  reactive_proactive):

        packet = list_packets[event['packet_id']]
        src_host, dst_host = self.find_hosts_by_ip_packet(packet)
        path = nx.dijkstra_path(self.G, src_host, dst_host, weight='bw')
        list_new_events = []

        if 'load' in self.G.edges[event['src'], event['dst']] and len(
                self.G.edges[event['src'], event['dst']]['load']) > 0:
            last_load = self.G.edges[event['src'], event['dst']]['load'][-1][1]
        else:
            last_load = 0
        load_packet = len(packet)
        new_load = last_load - load_packet
        if 'load' in self.G.edges[event['src'], event['dst']]:
            self.G.edges[event['src'], event['dst']]['load'].append((event['time_spawn'], new_load))

        for i in range(1, len(path) - 1):
            if path[i] == event['src']:
                id = uuid.uuid4()
                list_new_events.append({'type': 'packet_propagation',
                                        'src': event['dst'],
                                        'dst': event['src'],
                                        'time_spawn': event['time_spawn'] + 0.1,
                                        'packet_id': event['packet_id'],
                                        'openflow_id': id
                                        })

                list_openflow_messages[id] = {'type': 'packet_out', 'action': path[i + 1],
                                              'size': 50}  # TODO ver el tamanio real de un mensaje opnflow (p_out) y ponerlo aqui

            if reactive_proactive == 1 and path[i] and path[i] != event['src']:
                id = uuid.uuid4()
                list_new_events.append({'type': 'packet_propagation',
                                        'src': event['dst'],
                                        'dst': path[i],
                                        'time_spawn': event['time_spawn'] + 0.1,
                                        'packet_id': event['packet_id'],
                                        'openflow_id': id
                                        })
                list_openflow_messages[id] = {'type': 'flow_mood', 'action': path[i + 1],
                                              'size': 50}  # TODO ver el tamanio real de un mensaje opnflow (f_mood) y ponerlo aqui
        return list_new_events
