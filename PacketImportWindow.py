import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from scapy.layers.inet import *
from scapy.layers.l2 import Ether
from scapy.utils import rdpcap

from Utilities import Utilities


# Clase PacketImportWindow. Esta clase recoge los metodos para mostrar e importar paquetes (reales) en un host concreto,
# de manera que dichos paquetes seran empleados posteriormente en el simulador de eventos discretos como eventos de
# generacion de paquetes.
class PacketImportWindow(tk.Frame):

    # Constructor parametrizado de la clase PacketImportWindow.
    def __init__(self, root, master, host, graph, **kw):
        super().__init__(master, **kw)
        self.port_dst = tk.StringVar()
        self.port_src = tk.StringVar()
        self.ip_dst = tk.StringVar()
        self.ip_src = tk.StringVar()
        self.mac_dst = tk.StringVar()
        self.mac_src = tk.StringVar()
        self.protocol = tk.StringVar()
        self.protocol.set('TCP')
        self.number_packets = tk.IntVar()
        self.host_src = tk.StringVar()
        self.host_dst = tk.StringVar()
        self.root = root
        self.host = host
        self.list_packets = []
        self.master = master
        self.index = 1
        self.graph = graph
        self.showProtocolsOption = None
        self.time_spawn = tk.StringVar()
        self.time_spawn.set('0.0')
        self.initialize_user_interface()

    # Getter del atributo list_packets.
    def get_list_packets(self):
        return self.list_packets

    # Funcion edit, encargada de modificar los campos de la estructura Treeview encargada de mostrar los campos de
    # cada uno de los paquetes importados en un host.
    def edit(self, mac_src, mac_dst, ip_src, ip_dst, sport, dport, protocol, time_spawn):
        selected_item = self.tree.selection()[0]
        self.tree.item(selected_item, values=(mac_src, mac_dst, ip_src, ip_dst, sport, dport, protocol, time_spawn))

    # Funcion delete, encargada de eliminar tanto de la lista de paquetes importados/creados en un host como la
    # informacion relativa a cada uno de estos paquetes en la lista de paquetes de la estructura Treeview (encargada de
    # mostrar los campos de cada uno de los paquetes importados en un host).
    def delete(self):
        if len(self.tree.selection()) > 0:
            indexes_to_delete = []
            for selected_packet in self.tree.selection():
                indexes_to_delete.append(int(selected_packet, 10) - 1)  # Guardamos el valor del índice en entero
            indexes_to_delete = sorted(indexes_to_delete,
                                       reverse=True)  # Ordenamos los índices de mayor a menor antes de borrar
            for index in indexes_to_delete:
                self.list_packets.pop(index)  # Borramos de la lista local los paquetes indicados
                self.index -= 1

            for child in self.tree.get_children():
                self.tree.delete(child)  # Vaciamos el arbol

            i = 1
            for packet in self.list_packets:
                if ('MAC' in packet[0] or 'Ethernet' in packet[0]) and 'IP' in packet[0] and (
                        'TCP' in packet[0] or 'UDP' in packet[0]):
                    if 'TCP' in packet[0]:
                        protocol = 'TCP'
                    else:
                        protocol = 'UDP'
                    # Reinsertamos los paquetes actualizados
                    self.tree.insert('', 'end', iid=i, values=(
                        i, packet[0][Ether].src, packet[0][Ether].dst, packet[0][IP].src, packet[0][IP].dst,
                        packet[0][protocol].sport,
                        packet[0][protocol].dport, protocol, packet[1]))
                    i += 1

    # Funcion load_values, encargada de cargar los valores de un paquetes seleccionado en la estructura Treeview en los
    # campos para permitir realizar alguna modificacion sobre los mismos o aniadir nuesvos paquetes con dichos campos.
    def load_values(self):
        if len(self.tree.selection()) > 0:
            selected_item = self.tree.selection()[0]
            self.mac_src.set(self.tree.item(selected_item)['values'][1])
            self.mac_dst.set(self.tree.item(selected_item)['values'][2])
            self.ip_src.set(self.tree.item(selected_item)['values'][3])
            self.ip_dst.set(self.tree.item(selected_item)['values'][4])
            self.port_src.set(self.tree.item(selected_item)['values'][5])
            self.port_dst.set(self.tree.item(selected_item)['values'][6])
            self.protocol.set(self.tree.item(selected_item)['values'][7])
            self.time_spawn.set(self.tree.item(selected_item)['values'][8])

    # Funcion apply_changes, encargada de aplicar los cambios sobre los campos de un paquete seleccionado en la
    # estructura Treeview y el propio paquete seleccionado cambiando los campos de dicho paquete por los introducidos
    # por el usuario.
    def apply_changes(self):
        if len(self.tree.selection()) > 0:
            selected_item = int(self.tree.selection()[0])
            self.list_packets[selected_item - 1][0][Ether].src = self.mac_src.get()
            self.list_packets[selected_item - 1][0][Ether].dst = self.mac_dst.get()
            self.list_packets[selected_item - 1][0][IP].src = self.ip_src.get()
            self.list_packets[selected_item - 1][0][IP].dst = self.ip_dst.get()
            if 'TCP' in self.list_packets[selected_item - 1][0]:
                transport_protocol = 'TCP'
            else:
                transport_protocol = 'UDP'
            self.list_packets[selected_item - 1][0][transport_protocol].sport = int(self.port_src.get())
            self.list_packets[selected_item - 1][0][transport_protocol].dport = int(self.port_dst.get())
            self.tree.item(selected_item, values=(
                self.tree.item(selected_item)['values'][0], self.mac_src.get(), self.mac_dst.get(), self.ip_src.get(),
                self.ip_dst.get(), self.port_src.get(), self.port_dst.get(), self.protocol.get(),
                float(self.time_spawn.get())))

    # Funcion load_packets, encargada de cargar la lista de paquetes contenida en un fichero con extension .pcap.
    def load_packets(self):

        try:
            path = filedialog.askopenfile(title='Load PCAP', initialdir='./Packets',
                                          filetypes=(('Files .pcap', '*.pcap'), (('All Files', '*.*'))))
            if path is None:
                return

            scapy_cap = rdpcap(path.name)
            is_first = True
            for packet in scapy_cap:

                if ('MAC' in packet or 'Ethernet' in packet) and 'IP' in packet and (
                        'TCP' in packet or 'UDP' in packet):
                    if is_first:
                        initial_time = packet.time
                        is_first = False

                    packet[Ether].src = self.mac_src.get()
                    packet[Ether].dst = self.mac_dst.get()
                    packet[IP].src = self.ip_src.get()
                    packet[IP].dst = self.ip_dst.get()
                    self.list_packets.append((packet, packet.time - initial_time))

                    if 'TCP' in packet:
                        protocol = 'TCP'
                    else:
                        protocol = 'UDP'

                    self.tree.insert('', 'end', iid=self.index, values=(
                        self.index, packet[Ether].src, packet[Ether].dst, packet[IP].src, packet[IP].dst,
                        packet[protocol].sport,
                        packet[protocol].dport, protocol, packet.time - initial_time))
                    self.index += 1

        except Exception as er:
            messagebox.showwarning(er)

    # Funcion add_packets, encargada de aniadir nuevos paquetes a la lista de paquetes de un host a partir de la
    # informacion de los campos introducidos por el usuario (creando nuevos paquetes mediante la libreria Scapy).
    def add_packets(self):
        utilities = Utilities()
        if self.number_packets.get() > 0 and float(self.time_spawn.get()) >= 0.0:
            if utilities.port_check(self.port_src.get()) and utilities.port_check(self.port_dst.get()):
                for i in range(1, self.number_packets.get() + 1):

                    if self.protocol.get() == 'TCP':
                        p = Ether(src=self.mac_src.get(), dst=self.mac_dst.get()) / IP(src=self.ip_src.get(),
                                                                                       dst=self.ip_dst.get()) / TCP(
                            sport=int(self.port_src.get()), dport=int(self.port_dst.get()))
                    else:
                        p = Ether(src=self.mac_src.get(), dst=self.mac_dst.get()) / IP(src=self.ip_src.get(),
                                                                                       dst=self.ip_dst.get()) / UDP(
                            sport=int(self.port_src.get()), dport=int(self.port_dst.get()))

                    self.list_packets.append((p, float(self.time_spawn.get())))
                    self.tree.insert('', 'end', iid=self.index, values=(
                        self.index, p[Ether].src, p[Ether].dst, p[IP].src, p[IP].dst,
                        p[self.protocol.get()].sport,
                        p[self.protocol.get()].dport, self.protocol.get(), float(self.time_spawn.get())))
                    self.index += 1
            else:
                message = ''
                if utilities.port_check(self.port_src.get()):
                    message += self.port_src.get()
                if utilities.port_check(self.port_dst.get()):
                    message += self.port_dst.get()
                message_final = 'Error, (' + message + ') values are not valid. \n\no   Port must be a value between 1 and 65535.'
                messagebox.showerror("Error", message_final)
        else:
            messagebox.showerror("Error",
                                 'The number of packets to insert must be greater than 0 and the packet timestamp must be greater than 0.')

    # Funcion update_values_hosts, encargada de actualizar los valores de destino de los campos de la ventana de
    # insercion de trafico.
    def update_values_hosts(self, event):
        self.mac_dst.set(self.graph.get_graph().nodes[self.showHosts.get()]['mac'])
        self.ip_dst.set(self.graph.get_graph().nodes[self.showHosts.get()]['ip'])

    # Funcion update_values_protocols, encargada de actualizar el campo de protocolo del campo de protocolo de la
    # ventana de inserccion de trafico.
    def update_values_protocols(self, event):
        self.protocol.set(self.showProtocols.get())

    # Funcion initialize_user_interface, encargada de inicializar por completo la ventana de importacion de paquetes
    # en un host, creando las diferentes estructuras de datos, botones, campos, etc; para la inserccion, modificacion,
    # importacion de paquetes en un determinado host.
    def initialize_user_interface(self):
        self.tree = ttk.Treeview(self.root)
        self.scroll = tk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.scroll.grid(column=1, sticky='nsew')
        self.tree.configure(yscrollcommand=self.scroll.set)
        self.tree['show'] = 'headings'
        self.tree["columns"] = ("1", "2", "3", "4", "5", "6", "7", '8', '9')
        self.tree.heading('1', text='Packet')
        self.tree.heading('2', text='Source MAC')
        self.tree.heading('3', text='Destination MAC')
        self.tree.heading('4', text='Source IP')
        self.tree.heading('5', text='Destination IP')
        self.tree.heading('6', text='Source Port')
        self.tree.heading('7', text='Destination Port')
        self.tree.heading('8', text='Transport Protocol')
        self.tree.heading('9', text='Timestamp')
        self.tree.column('1', minwidth=120, width=145, stretch=False)
        self.tree.column('2', minwidth=120, width=145, stretch=False)
        self.tree.column('3', minwidth=120, width=145, stretch=False)
        self.tree.column('4', minwidth=120, width=145, stretch=False)
        self.tree.column('5', minwidth=120, width=145, stretch=False)
        self.tree.column('6', minwidth=120, width=145, stretch=False)
        self.tree.column('7', minwidth=120, width=145, stretch=False)
        self.tree.column('8', minwidth=120, width=145, stretch=False)
        self.tree.column('9', minwidth=120, width=145, stretch=False)
        self.tree.grid(row=0)
        campos = tk.LabelFrame(self.root, text="Packet Parameters")
        campos.grid(row=2, padx=5, pady=15)
        tk.Label(campos, text=' ').grid(row=0, column=0)
        tk.Label(campos, text="Src Host:").grid(row=1, column=0, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="Dst Host:").grid(row=2, column=0, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="Src MAC:").grid(row=1, column=2, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="Dst MAC:").grid(row=2, column=2, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="Src IP:").grid(row=1, column=4, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="Dst IP:").grid(row=2, column=4, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="Src Port:").grid(row=1, column=6, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="Dst Port:").grid(row=2, column=6, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="Pransport protocol:").grid(row=1, column=8, sticky='w', padx=20, pady=5)
        tk.Label(campos, text="No. of packets to add:").grid(row=2, column=8, sticky='w', padx=20, pady=5)
        self.host_src.set(self.host)
        tk.Entry(campos, textvariable=self.host_src, width=10, state='disabled').grid(row=1, column=1, sticky='w')
        tk.Entry(campos, textvariable=self.mac_src, width=16, state='disabled').grid(row=1, column=3, sticky='w')
        tk.Entry(campos, textvariable=self.mac_dst, width=16, state='disabled').grid(row=2, column=3, sticky='w')
        tk.Entry(campos, textvariable=self.ip_src, width=14, state='disabled').grid(row=1, column=5, sticky='w')
        tk.Entry(campos, textvariable=self.ip_dst, width=14, state='disabled').grid(row=2, column=5, sticky='w')
        list_ip = []
        for i in list(self.graph.get_graph().nodes):
            if i[0] == 'h' and i != self.host:
                list_ip.append(i)
        self.showHosts = tk.StringVar(campos)
        self.showHosts.set(list_ip[0])
        self.update_values_hosts('')
        self.showHostsOption = tk.OptionMenu(campos, self.showHosts, *list_ip, command=self.update_values_hosts)
        self.showHostsOption.grid(row=2, column=1, sticky='W')
        tk.Entry(campos, textvariable=self.port_src, width=7).grid(row=1, column=7, sticky='w')
        tk.Entry(campos, textvariable=self.port_dst, width=7).grid(row=2, column=7, sticky='w')
        self.showProtocols = tk.StringVar(campos)
        self.showProtocols.set('TCP')
        list_protocols = ['TCP', 'UDP']
        self.showProtocolsOption = tk.OptionMenu(campos, self.showProtocols, *list_protocols,
                                                 command=self.update_values_protocols)
        self.showProtocolsOption.grid(row=1, column=9, sticky='W')
        tk.Entry(campos, textvariable=self.number_packets, width=10).grid(row=2, column=9, sticky='w')
        tk.Label(campos, text='     ').grid(row=3, column=13)
        tk.Label(campos, text='     ').grid(row=1, column=13)
        tk.Label(campos, text='     ').grid(row=2, column=13)
        tk.Label(campos, text='     ').grid(row=3, column=13)
        tk.Label(campos, text="       Timestamp:  ").grid(row=1, column=11, sticky='w')
        tk.Entry(campos, textvariable=self.time_spawn, width=7).grid(row=1, column=12, sticky='w')
        tk.Button(campos, text="Load values", command=self.load_values, height=1, width=15).grid(row=1, column=14,
                                                                                                 sticky='E', padx=5,
                                                                                                 pady=5)
        tk.Button(campos, text="Apply changes", command=self.apply_changes, height=1, width=15).grid(row=2, column=14,
                                                                                                     sticky='E', padx=5,
                                                                                                     pady=5)
        tk.Button(campos, text="Add as new packet", command=self.add_packets, height=1, width=15).grid(row=3,
                                                                                                       column=14,
                                                                                                       sticky='E',
                                                                                                       padx=5, pady=5)
        buttonFrame = tk.Frame(self.root, bd=3)
        buttonFrame.grid(row=4, column=0, sticky='N')
        tk.Button(buttonFrame, text="Delete Selected Packet", command=self.delete).grid(row=0, column=0, padx=0, pady=0)
        tk.Button(buttonFrame, text="Load Packets from...", command=self.load_packets).grid(row=0, column=1, padx=20,
                                                                                            pady=0)
        tk.Button(buttonFrame, text="Save Packets", command=self.return_list_packets).grid(row=0, column=2, padx=0,
                                                                                           pady=0)
        self.ip_src.set(self.graph.get_graph().nodes[self.host]['ip'])
        self.mac_src.set(self.graph.get_graph().nodes[self.host]['mac'])
        if len(self.master.info_window_import) > 0 and self.host in self.master.info_window_import and len(
                self.master.info_window_import[self.host]) > 0:
            for i in range(0, len(self.master.info_window_import[self.host])):
                packet, time_spawn = self.master.info_window_import[self.host][i]
                packet.show()
                if ('MAC' in packet or 'Ethernet' in packet) and 'IP' in packet and (
                        'TCP' in packet or 'UDP' in packet):
                    if 'TCP' in packet:
                        protocol = 'TCP'
                    else:
                        protocol = 'UDP'
                    self.list_packets.append((packet, time_spawn))
                    self.tree.insert('', 'end', iid=self.index, values=(
                        self.index, packet[Ether].src, packet[Ether].dst, packet[IP].src, packet[IP].dst,
                        packet[protocol].sport,
                        packet[protocol].dport, protocol, time_spawn))
                    self.index += 1

    # Funcion return_list_packets, encargada de establecer en la lista de paquetes del host al cual se han importado
    # (posiblemente) una lista de paquetes, para posteriormente, ser insertados en la lista de eventos discretos
    # en nuestro simulador.
    def return_list_packets(self):
        self.master.info_window_import[self.host] = self.list_packets
        self.root.destroy()
