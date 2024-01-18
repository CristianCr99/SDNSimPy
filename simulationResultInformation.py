import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *

from scapy.layers.inet import IP

import Utilities as utilities


# Clase ResultInformation. Esta recoge los metodos para preparar la informacion tras la simulacion para la creacion
# y muestra mediante ventana de dialogo de los resultados de la simulacion.
class ResultInformation(tk.Frame):

    # Constructor parametrizado de la clase ResultInformation.
    def __init__(self, root, graph, list_flow, final_time, **kw):
        super().__init__(**kw)
        self.root = root
        self.graph = graph
        self.list_flow = list_flow
        self.final_time = final_time
        self.initialize_user_interface()

    # Funcion load_graph, encargada de cargar el grafico de un flujo de un host particular.
    def load_graph(self):
        if len(self.tree.selection()) > 0:
            selected_item = self.tree.selection()[0]
            host_flow = self.tree.item(selected_item)['values'][0]
            self.img = PhotoImage(file='./GraphsImages/' + host_flow + '.png')
            self.canvas_img.create_image(0, 0, anchor=NW, image=self.img)

    # Funcion load_graph_2, encargada de cargar el grafico de carga de un enlace concreto.
    def load_graph_2(self):
        if self.n != '':
            self.img_2 = PhotoImage(file='./GraphsImages/Link_Load_' + self.n.get() + '.png')
            self.canvas_img_2.create_image(0, 0, anchor=NW, image=self.img_2)

    # Funcion initialize_user_interface, encargada de inicializar la ventana en la que se mostraran los graficos
    # resultantes a partir de la informacion obtenida tras la ejecucion de la simulacion.
    def initialize_user_interface(self):

        self.root.geometry("1280x720")
        self.campos = tk.LabelFrame(self.root, text='Information on the delay of each flow')
        self.campos.pack(padx=5, pady=5)
        self.tree = ttk.Treeview(self.campos, height=13)
        self.tree['show'] = 'headings'
        self.tree["columns"] = ("1", "2", "3", "4", "5", "6")
        self.tree.heading('1', text='Flow')
        self.tree.heading('2', text='Src IP')
        self.tree.heading('3', text='Dst IP')
        self.tree.heading('4', text='Src Port')
        self.tree.heading('5', text='Dst Port')
        self.tree.heading('6', text='Transp. Protocol')
        self.tree.column('1', minwidth=50, width=50, stretch=False)
        self.tree.column('2', minwidth=110, width=110, stretch=False)
        self.tree.column('3', minwidth=110, width=110, stretch=False)
        self.tree.column('4', minwidth=70, width=70, stretch=False)
        self.tree.column('5', minwidth=70, width=70, stretch=False)
        self.tree.column('6', minwidth=90, width=90, stretch=False)
        self.tree.grid(row=0, column=0, padx=5, pady=5)
        tk.Button(self.root, text=" Load Graph ", command=self.load_graph, height=1, width=15).pack()

        for node in self.graph.get_graph().nodes:
            if node[0] == 'h' and node in self.list_flow:
                i = 1
                for flow in self.list_flow[node].items():
                    packet_delay_list = flow[1].get_packet_delay_list()
                    list_delays = [i[0] for i in packet_delay_list]
                    util = utilities.Utilities()
                    packet = flow[1].get_packet()

                    if 'TCP' in packet:
                        protocol = 'TCP'
                    else:
                        protocol = 'UDP'

                    self.tree.insert('', 'end', iid=node + '_' + str(i), values=(
                        node + '_' + str(i), packet[IP].src, packet[IP].dst, packet[protocol].sport,
                        packet[protocol].dport, protocol))

                    util.create_graph(y=list_delays, x=list(range(1, len(list_delays) + 1)),
                                      x_label='Packet (number)', y_label='Delay (ms)',
                                      title_graph='Delay per Packet - Node: ' + node + ' Flow: ' + str(i),
                                      name=node + '_' + str(i) + '.png',
                                      dpi=80, bbox_inches='tight', x_range_min=1, is_delay=True)

                    i += 1

        self.campos_load = tk.LabelFrame(self.root, text='Loading information for each link')
        self.campos_load.pack(padx=5, pady=5)

        ttk.Label(self.campos_load, text="Select the Link :").grid(row=0, column=0, sticky='NW', padx=5, pady=5)

        self.n = tk.StringVar()

        links_list = []

        for link in self.graph.get_graph().edges(data=True):

            if 'load' in link[2]:

                lista = (link[2]['load']).copy()
                lista.reverse()
                seen = set()
                list2 = []
                for i in lista:
                    list2.append((float(i[0]), i[1]))

                Output = [(a, b) for a, b in list2 if not (a in seen or seen.add(a))]
                Output.reverse()

                x = []
                y = []
                for data in Output:
                    x.append(data[0])
                    y.append(data[1])

                if 0 < len(x) == len(y) > 0:
                    links_list.append('[' + link[0] + ',' + link[1] + ']')
                    if x[0] != 0:
                        x.insert(0, 0)
                        y.insert(0, 0)
                    if x[-1] != self.final_time:
                        x.append(self.final_time / 1000)
                        y.append(0)
                    util.create_graph(y=y, x_label='Time',
                                      x=x, y_label='Load (Bytes)',
                                      title_graph='Link Load: [' + link[0] + ',' + link[1] + ']',
                                      name='Link_Load_[' + link[0] + ',' + link[1] + ']' + '.png',
                                      dpi=80, bbox_inches='tight', x_range_min=0, is_delay=False)

        self.showHostsOption = tk.OptionMenu(self.campos_load, self.n, *links_list)
        self.showHostsOption.grid(row=0, column=1, sticky='NW', padx=5, pady=5)
        self.canvas_img = Canvas(self.campos, width=700, height=290)
        self.canvas_img.grid(row=0, column=1, padx=5, pady=5)
        self.canvas_img_2 = Canvas(self.campos_load, width=1000, height=290)
        self.canvas_img_2.grid(row=0, column=2, padx=10, pady=5)

        if len(links_list[0]) > 0:
            self.n.set(links_list[0])

        tk.Button(self.root, text=" Load Graph ", command=self.load_graph_2, height=1, width=15).pack()
