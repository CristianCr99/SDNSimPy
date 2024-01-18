import json
import math
import os
import threading
import tkinter.filedialog
import tkinter.font
import tkinter.simpledialog
from cmath import pi
from json import JSONEncoder
from math import atan2, sin, cos
from struct import *
from threading import Thread
from tkinter import *
from tkinter import filedialog

import networkx as nx
from PIL import Image, ImageDraw
from PIL import ImageTk as itk
from networkx.readwrite import json_graph
from scapy.layers.inet import *
from ttkbootstrap import Style

import FlowInformation as fl_inf
import InfoLinkWindow as info_link
import InfoSwitchWindow as info_switch
import PacketImportWindow as p_import_w
import ProgramaGrafos as p
import Threads as t
import customizetopology as edit
import simulationResultInformation as resultInfor
from DiscreteEvents import DiscreteEvents


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


try:
    import queue
except ImportError:
    import Queue as queue

from collections import OrderedDict

SDN_Simulator_VERSION = "1.0.0"
if 'PYTHONPATH' in os.environ:
    sys.path = os.environ['PYTHONPATH'].split(':') + sys.path
FLOWTIMEDEF = 'Slow'
FLOWTIME = OrderedDict([('Slow', 30), ('Fast', 1)])
LinkTime = 0.1


# Clase PrefsDialog, encargada de establecer las preferencias de las ventanas de dialogo.
class PrefsDialog(tkinter.simpledialog.Dialog):

    # Constructor parametrizado de la clase PrefsDialog.
    def __init__(self, parent, title, prefDefaults, simulation_running):

        self.prefValues = prefDefaults
        self.simulation_is_running = simulation_running

        tkinter.simpledialog.Dialog.__init__(self, parent, title)

    # Funcion body, encargada de crear el cuerpo de la ventana de dialogo.
    def body(self, master):
        self.rootFrame = master

        self.typeColorsOpenFlow = LabelFrame(self.rootFrame, text='Openflow Packet Type Colors', padx=5, pady=5)
        self.typeColorsOpenFlow.grid(row=4, column=0, columnspan=2, sticky=EW, padx=5, pady=10)
        for i in range(3):
            self.typeColorsOpenFlow.columnconfigure(i, weight=1)
        self.typeColors = self.prefValues['typeColors']

        Label(self.typeColorsOpenFlow, text="General").grid(row=0, column=0, sticky=W, padx=10)
        self.OpenFlowColor = StringVar(self.typeColorsOpenFlow)
        self.OpenFlowColor.set(self.typeColors["OpenFlow"])
        self.OpenFlowColorMenu = OptionMenu(self.typeColorsOpenFlow, self.OpenFlowColor, "None", "Red", "Green", "Blue",
                                            "Purple", 'Brown', 'Cyan', 'Orange', 'Violet')
        self.OpenFlowColorMenu.grid(row=1, column=0, sticky=W, padx=10)

        Label(self.typeColorsOpenFlow, text="Packet In").grid(row=0, column=1, sticky=W, padx=10)
        self.PacketInColor = StringVar(self.typeColorsOpenFlow)
        self.PacketInColor.set(self.typeColors["packet_in"])
        self.PacketInColorMenu = OptionMenu(self.typeColorsOpenFlow, self.PacketInColor, "None", "Red", "Green", "Blue",
                                            "Purple", 'Brown', 'Cyan', 'Orange', 'Violet')
        self.PacketInColorMenu.grid(row=1, column=1, sticky=W, padx=10)

        Label(self.typeColorsOpenFlow, text="Packet Out").grid(row=0, column=2, sticky=W, padx=10)
        self.PacketOutColor = StringVar(self.typeColorsOpenFlow)
        self.PacketOutColor.set(self.typeColors["packet_out"])
        self.PacketOutColorMenu = OptionMenu(self.typeColorsOpenFlow, self.PacketOutColor, "None", "Red", "Green",
                                             "Blue", "Purple",
                                             'Brown', 'Cyan', 'Orange', 'Violet')
        self.PacketOutColorMenu.grid(row=1, column=2, sticky=W, padx=10)

        Label(self.typeColorsOpenFlow, text="Flow Mood").grid(row=0, column=3, sticky=W, padx=10)
        self.FlowModColor = StringVar(self.typeColorsOpenFlow)
        self.FlowModColor.set(self.typeColors["flow_mood"])
        self.FlowModColorMenu = OptionMenu(self.typeColorsOpenFlow, self.FlowModColor, "None", "Red", "Green", "Blue",
                                           "Purple",
                                           'Brown', 'Cyan', 'Orange', 'Violet')
        self.FlowModColorMenu.grid(row=1, column=3, sticky=W, padx=10)

        self.typeColorsData = LabelFrame(self.rootFrame, text='Data Packet Type Colors', padx=5, pady=5)
        self.typeColorsData.grid(row=5, column=0, columnspan=2, sticky=EW, padx=5, pady=5)
        for i in range(3):
            self.typeColorsData.columnconfigure(i, weight=1)

        Label(self.typeColorsData, text="TCP").grid(row=0, column=1, sticky=W, padx=10)
        self.TCPColor = StringVar(self.typeColorsData)
        self.TCPColor.set(self.typeColors["TCP"])
        self.TCPColorMenu = OptionMenu(self.typeColorsData, self.TCPColor, "None", "Red", "Green", "Blue", "Purple",
                                       'Brown', 'Cyan', 'Orange', 'Violet')
        self.TCPColorMenu.grid(row=1, column=1, sticky=W, padx=10)

        Label(self.typeColorsData, text="UDP").grid(row=0, column=2, sticky=W, padx=10)
        self.UDPColor = StringVar(self.typeColorsData)
        self.UDPColor.set(self.typeColors["UDP"])
        self.UDPColorMenu = OptionMenu(self.typeColorsData, self.UDPColor, "None", "Red", "Green", "Blue", "Purple",
                                       'Brown', 'Cyan', 'Orange', 'Violet')
        self.UDPColorMenu.grid(row=1, column=2, sticky=W, padx=10)

        Label(self.typeColorsData, text="General").grid(row=0, column=0, sticky=W, padx=10)
        self.UsertrafficColor = StringVar(self.typeColorsData)
        self.UsertrafficColor.set(self.typeColors["Usertraffic"])
        self.UsertrafficColorMenu = OptionMenu(self.typeColorsData, self.UsertrafficColor, "None", "Red", "Green",
                                               "Blue", "Purple", 'Brown', 'Cyan', 'Orange', 'Violet')
        self.UsertrafficColorMenu.grid(row=1, column=0, sticky=W, padx=10)

        Label(self.rootFrame, text="IP address on packets:").grid(row=7, sticky=W, padx=10, pady=10)
        self.showAddrVar = StringVar(self.rootFrame)
        self.showaddrOption = OptionMenu(self.rootFrame, self.showAddrVar, "Source and Destination", "None")
        self.showaddrOption.grid(row=7, column=1, sticky=W)
        self.showAddrVar.set(self.prefValues['showAddr'])

        if self.simulation_is_running == True:
            state_menu = 'disabled'
        else:
            state_menu = 'normal'

        Label(self.rootFrame, text="Packet Flow Speed:").grid(row=8, sticky=W, padx=10, pady=10)
        self.flowTime = StringVar(self.rootFrame)
        self.flowTime.set(list(FLOWTIME.keys())[list(FLOWTIME.values()).index(self.prefValues['flowTime'])])
        self.flowTimeMenu = OptionMenu(self.rootFrame, self.flowTime, *FLOWTIME.keys())
        self.flowTimeMenu.configure(state=state_menu)
        self.flowTimeMenu.grid(row=8, column=1, sticky=W)

        Label(self.rootFrame, text="Proactive mode controller:").grid(row=9, sticky=W, padx=5, pady=5)
        self.reactive_proactive = IntVar()
        self.cs_reactive_proactive = Checkbutton(self.rootFrame, variable=self.reactive_proactive)
        self.cs_reactive_proactive.configure(state=state_menu)
        self.cs_reactive_proactive.grid(row=9, column=1, sticky=W, padx=5, pady=10)
        if self.prefValues['reactive_proactive'] == 0:
            self.cs_reactive_proactive.deselect()
        else:
            self.cs_reactive_proactive.select()

    # Funcion apply, encargada de establecer los valores introducidos de los diferentes campos de la ventana de
    # dialogo.
    def apply(self):

        flowTime = FLOWTIME[self.flowTime.get()]
        # self.typeColors['ARP'] = str(self.ARPColor.get())
        self.typeColors['TCP'] = str(self.TCPColor.get())
        self.typeColors['OpenFlow'] = str(self.OpenFlowColor.get())
        self.typeColors['UDP'] = str(self.UDPColor.get())
        self.typeColors['Usertraffic'] = str(self.UsertrafficColor.get())
        self.typeColors['Packet_In'] = str(self.PacketInColor.get())
        self.typeColors['Packet_Out'] = str(self.PacketOutColor.get())
        self.typeColors['Flow_Mod'] = str(self.FlowModColor.get())
        self.typeColors['Flow_Mod'] = str(self.FlowModColor.get())
        typeColors = self.typeColors

        self.result = {'flowTime': flowTime,
                       'typeColors': typeColors,
                       'showAddr': self.showAddrVar.get(),
                       'reactive_proactive': self.reactive_proactive.get()
                       }


# Clase SDN_Simulator. Es la principal clase de esta heramienta de simulacion. Recoge los metodos mas relevantes
# para realizar la simulacion; desde la interfaz grafica hasta la logica que gobierna el funcionamiento del simulador
# (haciendo llamada a las funciones principales de otras clases para el funcionamiento completo del simulador).
class SDN_Simulator(Frame, Thread):

    # Constructor por defecto de la clase SDN_Simulator.
    def __init__(self, parent=None, cheight=720, cwidth=1280, locations={}):

        Frame.__init__(self, parent)
        self.__running = threading.Event()
        self.__flag = threading.Event()
        self.list_threads = []
        self.list_processed_events = []
        self.action = None
        self.info_window_import = {}
        self.simulation_is_running = False

        # Preferencias por defecto:
        self.appPrefs = {
            'flowTime': FLOWTIME[FLOWTIMEDEF],
            'typeColors': {'Usertraffic': 'Purple', 'TCP': 'Orange', 'OpenFlow': 'Blue', 'UDP': 'Brown',
                           'packet_in': 'Cyan', 'packet_out': 'Green', 'flow_mood': 'Violet'},
            'showAddr': 'Source and destination',
            'reactive_proactive': 1  # 1 es proactivo y 0 reactivo
        }

        self.HOST_COLORS = ['#E57300', '#FF66B2', '#fa0004', '#b1b106', '#957aff', '#FF00FF', '#2f90d0', '#818c8d',
                            '#A93226', '#1b2ef8', '#3ef979', '#7c2ff9']
        self.Controller_Color = '#9D9D9D'
        self.images = miniImages()

        # Titulo
        self.appName = 'SDN Simulator'
        self.top = self.winfo_toplevel()
        self.top.title(self.appName)

        # Menu bar
        self.createMenubar()

        self.cheight, self.cwidth = cheight, cwidth
        self.cframe, self.canvas = self.createCanvas()
        self.top.geometry("%dx%d%+d%+d" % (self.cwidth, self.cheight, 0, 0))  # CRISTIAN: QUITAR PARA QUE NO SE MUEVA

        self.cframe.grid(column=1, row=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.pack(expand=True, fill='both')

        self.aboutBox = None
        self.infoBox = None

        self.nodeBindings = self.createNodeBindings()
        self.nodePrefixes = {'LegacyRouter': 'r', 'LegacySwitch': 's', 'Switch': 's', 'Host': 'h', 'Controller': 'c'}
        self.widgetToItem = {}
        self.itemToWidget = {}
        self.Nodes = []
        self.intfData = []

        self.link = self.linkWidget = None

        self.selection = None

        # Fijaciones del teclado y de las ventanas emergentes:
        self.bind('<Control-q>', lambda event: self.quit())
        self.focus()
        self.canvas.bind('<Button-1>', self.setFocus)
        self.hostPopup = Menu(self.top, tearoff=0, takefocus=1)
        self.hostPopup.add_command(label='Traffic Insertion', command=self.traffic_insertion)
        self.hostPopup.bind("<FocusOut>", self.popupFocusOut)
        self.legacyRouterPopup = Menu(self.top, tearoff=0, takefocus=1)
        self.legacyRouterPopup.add_command(label='Router Options')
        self.legacyRouterPopup.add_separator()
        self.legacyRouterPopup.bind("<FocusOut>", self.popupFocusOut)
        self.switchPopup = Menu(self.top, tearoff=0, takefocus=1)
        self.switchPopup.add_command(label='Switch Details', command=self.show_switch_info)
        self.linkPopup = Menu(self.top, tearoff=0, takefocus=1)
        self.linkPopup.add_command(label='Link Details', command=self.link_details)
        self.linkPopup.bind("<FocusOut>", self.popupFocusOut)

        # Initalizacion de la gestion de eventos
        self.linkx = self.linky = self.linkItem = None
        self.lastSelection = None

        # Inicializacion del modelo
        self.packetImage = []
        self.flowQueues = {}
        self.links = {}
        self.cli = None

        # Configuracion de valores cuando se llama a la clase SDN_Simulator desde un script
        self.nodelocations = locations
        self.options = None
        self.args = None
        self.validate = None
        self.active = True
        self.traffic_hosts = None

        # Reunimos informacion sobre la topología y creamos los nodos
        self.TopoInfo()
        self.createNodes()
        self.chronometer = Label(self.cframe, text='\n Simulation Time \n\n00:00:000', padx=3, pady=3, relief="ridge")
        self.chronometer.grid(row=0, column=1, sticky='NE', padx=3, pady=3)
        self.stop_simulation = False
        self.time_pause = 0
        self.time_start_pause = 0

        # cerramos la ventana
        Wm.wm_protocol(self.top, name='WM_DELETE_WINDOW', func=self.quit)

    # Funcion get__t_event, encargada de devolver la bandera y el proceso en ejecucion.
    def get__t_event(self):
        return self.__flag, self.__running

    # Funcion setCustom, encargada de establecer los parametros personalizados para Mininet.
    def setCustom(self, name, value):

        if name in ('topos', 'switches', 'hosts', 'controllers'):
            param = name.upper()
            try:
                globals()[param].update(value)
                globals()[str(param + '_TYPES')].append(value.keys()[0])
            except:
                pass
        elif name == 'validate':
            self.validate = value

        elif name == 'locations':
            self.nodelocations = value

        else:
            globals()[name] = value

    # Funcion configs, encargada de la carga de configuraciones personalizadas.
    def configs(self, _option, _opt_str, value, _parser):

        fileName = value

        if not os.path.isfile(fileName):
            return
        f = open(fileName, 'r')
        loadedPrefs = self.convertJsonUnicode(json.load(f))
        # Cargamos las preferencias de la aplicacion
        if 'preferences' in loadedPrefs:
            self.appPrefs = dict(self.appPrefs.items() + loadedPrefs['preferences'].items())
        if 'filters' in loadedPrefs:
            self.appFilters = dict(self.appFilters.items() + loadedPrefs['filters'].items())
        f.close()

    # Funcion TopoInfo, encargada de establecer los parametros (direcciones ip, puertos...) a los diferentes elementos
    # cargados en el grafo que contiene toda la informacion de la topologia.
    def TopoInfo(self):
        for i in graph.get_graph().nodes():
            if i[0] == 'c':
                ip = ''
                port = ''
                if 'ip' in graph.get_graph().nodes()[i]:
                    ip = graph.get_graph().nodes()[i]['ip']
                if 'port' in graph.get_graph().nodes()[i]:
                    port = graph.get_graph().nodes()[i]['port']
                self.Nodes.append(
                    {'name': i, 'widget': None, 'type': 'Controlador', 'ip': ip,
                     'port': port,
                     'color': self.Controller_Color})
            elif i[0] == 's':
                self.Nodes.append(
                    {'name': i, 'widget': None, 'type': "Switch", 'dpid': None, 'color': None, 'controllers': []})
            elif i[0] == 'h':
                self.Nodes.append(
                    {'name': i, 'widget': None, 'type': "Host", 'ip': graph.get_graph().nodes()[i]['ip'],
                     'color': None})

    # Funcion crateNodes, encargada de dibujar los widgets de los nodos (junto a sus enlaces)
    def createNodes(self):
        for node in self.Nodes:
            if not self.findWidgetByName(node['name']):
                self.newNamedNode(node, float(graph.get_graph().nodes()[node['name']]['x']),
                                  float(graph.get_graph().nodes()[node['name']]['y']))

        # Bibujamos los enlaces de los nodos
        for i in list(graph.get_graph().edges()):
            self.drawLink(i[0], i[1])

        # Dibujamos los enlaces del controlador
        for switch in self.Nodes:
            try:
                for ctrlr in switch['controllers']:
                    self.drawLink(ctrlr, switch['name'])
            except:
                pass

    # Funcion createPacket, encargada de mostrar en nuestro lienzo (canvas) un paqueye llamando a la funcion
    # displayPacket para ello.
    def createPacket(self, src, dst, PacketInfo):
        try:
            # Obtenemos la cola en la que se debe aniadir el paquete
            q = self.getQueue(PacketInfo)
            if q is not None:
                # Refrescamos una cola si crece por encima de los 100 paquetes
                if q.qsize() > 100:
                    self.clearQueue(q)
                # Crear un hilo para mostrar el paquete y añadirlo a la cola
                thr = Thread(target=self.displayPacket, args=(src, dst, PacketInfo))
                thr.daemon = True
                q.put(thr)
        except Exception as e:
            print(e)

    # Funcion displayPacket, encargada de dibujar el paquete y moverlo por nuestro lienzo empleando para ello la
    # funcion movePacket.
    def displayPacket(self, src, dst, Packet, is_openflow, type_openflow, h_src_dst, time, flag, running):
        try:
            c = self.canvas
            s = self.findWidgetByName(src)
            d = self.findWidgetByName(dst)
            srcx, srcy = c.coords(self.widgetToItem[s])
            dstx, dsty = c.coords(self.widgetToItem[d])

            # Dibujamos una forma de rectangulo para el paquete
            if is_openflow and type_openflow == 'packet_out':
                image1 = Image.new("RGBA", (90, 15))
                draw = ImageDraw.Draw(image1)
                draw.polygon([(0, 0), (0, 15), (90, 15), (90, 0)], "black")
            else:
                image1 = Image.new("RGBA", (45, 15))
                draw = ImageDraw.Draw(image1)
                draw.polygon([(0, 0), (0, 15), (45, 15), (45, 0)], "black")

            if is_openflow:
                color_by_type_packet = self.appPrefs['typeColors']['OpenFlow']
            else:
                color_by_type_packet = self.appPrefs['typeColors']['Usertraffic']

            draw.polygon([(15, 0), (15, 15), (45, 15), (45, 0)], color_by_type_packet)
            if type_openflow == 'packet_out':
                draw.polygon([(15 + 45, 0), (15 + 45, 15), (45 + 45, 15), (45 + 45, 0)], color_by_type_packet)

            if not is_openflow:
                try:
                    if 'UDP' in Packet:
                        protocol = 'UDP'
                    elif 'TCP' in Packet:
                        protocol = 'TCP'
                    ip_color = self.appPrefs['typeColors'][protocol]
                except:
                    ip_color = 'pink'
            else:
                try:
                    ip_color = self.appPrefs['typeColors'][type_openflow]
                except:
                    ip_color = 'pink'
                    print('Excepción:', type_openflow)

            if ip_color is not None:
                draw.polygon([(0, 0), (0, 15), (15, 15), (15, 0)], ip_color)
                if type_openflow == 'packet_out':
                    draw.polygon([(0 + 45, 0), (0 + 45, 15), (15 + 45, 15), (15 + 45, 0)],
                                 self.appPrefs['typeColors']['flow_mood'])

            # Si el origen y destino no se muestra, entonces gira el paquete a lo largo del enlace
            if self.appPrefs['showAddr'] == 'None':
                angle = -1 * atan2(dsty - srcy, dstx - srcx)
                dx = 7 * sin(angle)
                dy = 7 * cos(angle)
                angle = 180 * angle / pi
                packetImage = itk.PhotoImage(image1.rotate(angle, expand=True))
            else:
                angle = -1 * atan2(dsty - srcy, dstx - srcx)
                dx = 10 * sin(angle)
                dy = 10 * cos(angle)
                angle = 180 * angle / pi
                draw.text((0, 0), h_src_dst)
                draw.text((45, 0), h_src_dst)
                packetImage = itk.PhotoImage(image1)

            self.packetImage.append(packetImage)
            packet = c.create_image(srcx + dx, srcy + dy, image=packetImage)
            deltax = (dstx - srcx) / 50
            deltay = (dsty - srcy) / 50
            delta = deltax, deltay

            t = (float(self.appPrefs['flowTime']) * float(100) / 50000.0)

            self.movePacket(packet, packetImage, delta, t)

        except Exception:
            print('Excepcion!')

    # Funcion display_multiple_packet, encargada de ejecutar la animacion de un paquete por nuestro lienzo mediante
    # la llamada de la funcion displayPacket, realizando dicha ejecucion en un hilo ejecutandose dicha animacion
    # paralelamente al programa principal.
    def display_multiple_packet(self, src, dst, Packet, is_openflow, type_openflow, h_src_dst, time):
        arr = [src, dst, Packet, is_openflow, type_openflow, h_src_dst, time, self.__flag, self.__running]
        new_thread = t.run_process(target=self.displayPacket, args=arr)
        new_thread.start()
        self.list_threads.append(new_thread)

    # Funcion movePacket, encargada de realizar exclusivamente la animacion del paquete a desplazar por el lienzo. En
    # esta funcion tambien se establece el punto de parada del proceso que ejecuta esta funcion (mediante señales) con
    # el fin de poder detener la ejecucion de las animaciones de los paquetes desplazandose por nuestro lienzo.
    def movePacket(self, packet, image, delta, t):
        c = self.canvas
        i = 0
        # Movemos el paquete en 50 pasos y luego eliminamos la imagen
        self.__flag.set()
        self.__running.set()
        # tiempo_inicial = time.time()
        while i < 50:
            self.__flag.wait()  # Punto de parada de la animacion cuando recibe una senial con dicho proposito
            i += 1
            c.move(packet, delta[0], delta[1])
            c.update()
            time.sleep(t)
        # print('Time: ' + str(time.time() - tiempo_inicial))
        c.delete(packet)

        self.packetImage.remove(image)

    def getQueue(self, PacketInfo):
        eth_protocol, ip_protocol = PacketInfo['eth_protocol'], PacketInfo['ip_protocol']
        s_addr, d_addr = PacketInfo['s_addr'], PacketInfo['d_addr']
        interface = PacketInfo['interface']
        addr1, addr2 = s_addr, d_addr

        t = float(self.appPrefs['flowTime']) * float(PacketInfo['time']) / 50000

        if self.appPrefs['flowTime'] == 1 or self.appPrefs['identifyFlows'] == 0:
            q_name = ip_protocol + addr1 + addr2 + interface
            if q_name in self.flowQueues:
                return self.flowQueues[q_name]
            else:
                self.flowQueues[q_name] = queue.Queue()
                qt = Thread(target=self.startQueue, args=(self.flowQueues[q_name], t))
                qt.daemon = True
                qt.start()
                return self.flowQueues[q_name]
        else:
            q_name1 = ip_protocol + addr1 + addr2
            q_name2 = ip_protocol + addr2 + addr1
            if q_name1 in self.flowQueues:
                return self.flowQueues[q_name1]
            elif q_name2 in self.flowQueues:
                return self.flowQueues[q_name2]
            else:
                self.flowQueues[q_name1] = queue.Queue()
                qt = Thread(target=self.startQueue, args=(self.flowQueues[q_name1], t))
                qt.daemon = True
                qt.start()
                return self.flowQueues[q_name1]

    def startQueue(self, q, t):
        while True:
            thr = q.get()
            # For realtime display, empty queue more frequently to display up-to-date packets
            if self.appPrefs['flowTime'] == 1:
                while not q.empty():
                    q.task_done()
                    thr = q.get()
            thr.start()

            while thr.isAlive():
                time.sleep(t)
                pass
            try:
                q.task_done()
            except:
                pass

    # Funcion clearQueue, encargada de borrar la cola y eliminar todos los paquetes en cola.
    def clearQueue(self, qu=None):
        if qu is None:
            for q in self.flowQueues:
                while not self.flowQueues[q].empty():
                    self.flowQueues[q].task_done()
                    self.flowQueues[q].get()
        else:
            while not qu.empty():
                qu.task_done()
                qu.get()

    # Funcion createCanvas, encargada de crear y devolver nuestro marco de lienzo desplazable.
    def createCanvas(self):

        f = Frame(self)
        canvas = Canvas(f, width=self.cwidth, height=self.cheight)

        # Scroll bars (Barras de desplazamiento)
        xbar = Scrollbar(f, orient='horizontal', command=canvas.xview)
        ybar = Scrollbar(f, orient='vertical', command=canvas.yview)
        canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)

        # Cambiamos el tamanio de la caja
        resize = Label(f, bg='white')

        # Disenio
        canvas.grid(row=0, column=1, sticky='nsew')
        ybar.grid(row=0, column=2, sticky='ns')
        xbar.grid(row=1, column=1, sticky='ew')
        resize.grid(row=1, column=2, sticky='nsew')

        # Comportamiento del cambio de tamanio
        f.rowconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)
        f.grid(row=0, column=0, sticky='nsew')
        f.bind('<Configure>', lambda event: self.updateScrollRegion())

        return f, canvas

    # Funcion updateScrollRegion, encargada de actualizar la región de desplazamiento del lienzo para contener todos los
    # elementos de la topologia.
    def updateScrollRegion(self):
        bbox = self.canvas.bbox('all')
        if bbox is not None:
            self.canvas.configure(scrollregion=(0, 0, bbox[2],
                                                bbox[3]))

    # Funcion canvasx, encargada de convertir la coordenada x de la raiz a la coordenada del lienzo.
    def canvasx(self, x_root):
        c = self.canvas
        return c.canvasx(x_root) - c.winfo_rootx()

    # Funcion canvasy, encargada de convertir la coordenada y de la raíz a la coordenada del lienzo.
    def canvasy(self, y_root):
        c = self.canvas
        return c.canvasy(y_root) - c.winfo_rooty()

    def popupFocusOut(self, event=None):
        event.widget.unpost()

    def setFocus(self, event=None):
        event.widget.focus_set()

    # Funcion findWidgetByName, encargada de encontrar un widget por su nombre.
    def findWidgetByName(self, name):
        for widget in self.widgetToItem:
            if name == widget['text']:
                return widget

    # Funcion findItem, encargada de encontrar items en un lugar de nuestro lienzo.
    def findItem(self, x, y):
        items = self.canvas.find_overlapping(x, y, x, y)
        if len(items) == 0:
            return None
        else:
            return items[0]

    # Funcion nodeIcon, encargada de crear un nuevo icono de nodo.
    def nodeIcon(self, node, name, color):
        icon = Button(self.canvas, image=self.images[node],
                      text=name, compound='top')
        icon.config(highlightbackground=color, highlightcolor=color, highlightthickness=3)
        bindtags = [str(self.nodeBindings)]
        bindtags += list(icon.bindtags())
        icon.bindtags(tuple(bindtags))
        return icon

    # Funcion newNamedNode, encargada de aniadir a un icono de un nodo un nombre.
    def newNamedNode(self, Node, x, y):
        name = Node['name']
        type = Node['type']
        color = None
        c = self.canvas
        node = 'Switch'
        if type == "Router":
            node = 'LegacyRouter'
        elif type == "Switch":
            node = 'Switch'
        elif type == 'Host':
            node = 'Host'
            color = None
        elif type == 'Controlador':
            node = 'Controller'
            color = self.Controller_Color

        icon = self.nodeIcon(node, name, color)
        item = self.canvas.create_window(x, y, anchor='c', window=icon,
                                         tags=node)
        self.widgetToItem[icon] = item
        self.itemToWidget[item] = icon
        self.selectItem(item)
        icon.links = {}

        Node['color'], Node['widget'] = color, item

        icon.bind('<Button-1>', self.setFocus)
        if 'Switch' == node:
            icon.bind('<Button-3>', self.do_switchPopup)
        if 'LegacyRouter' == node:
            icon.bind('<Button-3>', self.do_legacyRouterPopup)
        if 'LegacySwitch' == node:
            icon.bind('<Button-3>', self.do_legacySwitchPopup)
        if 'Host' == node:
            icon.bind('<Button-3>', self.do_hostPopup)
        if 'Controller' == node:
            icon.bind('<Button-3>', self.do_controllerPopup)
        self.updateScrollRegion()

    # Funcion createNodeBindings, encargada de crear un conjunto de enlaces para los nodos.
    def createNodeBindings(self):
        bindings = {
            '<ButtonPress-1>': self.selectNode,
            '<B1-Motion>': self.dragNodeAround,
            '<Enter>': self.enterNode,
            '<Leave>': self.leaveNode
        }
        l = Label()
        for event, binding in bindings.items():
            l.bind(event, binding)
        return l

    # Funcion selectItem, encargada de seleccionar un elemento y recordar la seleccion anterior.
    def selectItem(self, item):
        self.lastSelection = self.selection
        self.selection = item

    # Funcion enterNode, encargada de seleccionar el nodo de entrada.
    def enterNode(self, event):
        self.selectNode(event)

    # Funcion leaveNode, encargada de restaurar la antigua selección al salir.
    def leaveNode(self, _event):
        self.selectItem(self.lastSelection)

    # Funcion selectNode, encargada de Seleccionar el nodo sobre el que se ha hecho clic.
    def selectNode(self, event):
        item = self.widgetToItem.get(event.widget, None)
        self.selectItem(item)

    # Funcion dragNodeAround, encargada de arrastrar un nodo en el lienzo.
    def dragNodeAround(self, event):
        c = self.canvas
        x = self.canvasx(event.x_root)
        y = self.canvasy(event.y_root)
        w = event.widget
        item = self.widgetToItem[w]
        c.coords(item, x, y)
        for dest in w.links:
            link = w.links[dest]
            item = self.widgetToItem[dest]
            x1, y1 = c.coords(item)
            c.coords(link, x, y, x1, y1)
        self.updateScrollRegion()

    # Funcion createControlLinkBindings, encargada de crear un conjunto de enlaces para los nodos (controlador).
    def createControlLinkBindings(self):

        def select(_event, link=self.link):
            self.selectItem(link)

        def highlight(_event, link=self.link):
            self.selectItem(link)
            self.canvas.itemconfig(link, fill='#29D3A7')

        def unhighlight(_event, link=self.link):
            self.canvas.itemconfig(link, fill='#95A5A6')

        self.canvas.tag_bind(self.link, '<Enter>', highlight)
        self.canvas.tag_bind(self.link, '<Leave>', unhighlight)
        self.canvas.tag_bind(self.link, '<ButtonPress-1>', select)

    # Funcion createDataLinkBindings, encargada de crear un conjunto de enlaces para los nodos (Switches).
    def createDataLinkBindings(self):

        def select(_event, link=self.link):
            self.selectItem(link)
            self.canvas.focus_set()

        def highlight(_event, link=self.link):
            self.selectItem(link)
            self.canvas.itemconfig(link, fill='#29D3A7')

        def unhighlight(_event, link=self.link):
            self.canvas.itemconfig(link, fill='purple')

        self.canvas.tag_bind(self.link, '<Enter>', highlight)
        self.canvas.tag_bind(self.link, '<Leave>', unhighlight)
        self.canvas.tag_bind(self.link, '<ButtonPress-1>', select)
        self.canvas.tag_bind(self.link, '<Button-3>', self.do_linkPopup)

    # Funcion drawLink, encargada de preparar un enlace para su creacion final mediante la funcion addLink.
    def drawLink(self, src, dst):

        w = self.findWidgetByName(src)
        item = self.widgetToItem[w]

        x, y = self.canvas.coords(item)
        self.link = self.canvas.create_line(x, y, x, y, width=4,
                                            fill='purple', tag='link')
        self.linkx, self.linky = x, y
        self.linkWidget = w
        self.linkItem = item

        source = self.linkWidget
        c = self.canvas

        dest = self.findWidgetByName(dst)
        x, y = c.coords(self.widgetToItem[dest])

        if (source is None or dest is None or source == dest
                or dest in source.links or source in dest.links):
            return
        # Por ahora, no permitimos que los hosts se vinculen directamente
        stags = self.canvas.gettags(self.widgetToItem[source])
        dtags = self.canvas.gettags(self.widgetToItem[dest])
        if (('Host' in stags and 'Host' in dtags) or
                ('Controller' in dtags and 'LegacyRouter' in stags) or
                ('Controller' in stags and 'LegacyRouter' in dtags) or
                ('Controller' in dtags and 'LegacySwitch' in stags) or
                ('Controller' in stags and 'LegacySwitch' in dtags) or
                ('Controller' in dtags and 'Host' in stags) or
                ('Controller' in stags and 'Host' in dtags) or
                ('Controller' in stags and 'Controller' in dtags)):
            return

        if 'Controller' in stags or 'Controller' in dtags:
            linkType = 'control'

            c.itemconfig(self.link, dash=(6, 4, 2, 4), fill='#95A5A6')
            self.createControlLinkBindings()
        else:
            linkType = 'data'
            self.createDataLinkBindings()
        c.itemconfig(self.link, tags=c.gettags(self.link) + (linkType,))

        x, y = c.coords(self.widgetToItem[dest])
        c.coords(self.link, self.linkx, self.linky, x, y)
        self.addLink(source, dest, linktype=linkType)

        self.link = self.linkWidget = None

    # Funcion addLink, encargada de aniadir al modelo un enlace.
    def addLink(self, source, dest, linktype='data', linkopts=None):
        if linkopts is None:
            linkopts = {}
        source.links[dest] = self.link
        dest.links[source] = self.link
        self.links[self.link] = {'type': linktype,
                                 'src': source,
                                 'dest': dest,
                                 'linkOpts': linkopts}

    # Funcion createMenubar, encargada de crear la barra de menu bar de nuestro simulador, que contendra las diferentes
    # opciones.
    def createMenubar(self):

        mbar = Menu(self.top)
        self.top.configure(menu=mbar)

        fileMenu = Menu(mbar, tearoff=False)
        mbar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Load Topology", command=self.loadGraph)
        fileMenu.add_command(label="Save Topology", command=self.saveGraph)
        fileMenu.add_separator()
        fileMenu.add_command(label="Topology Editor", command=self.customize_topology)

        editMenu = Menu(mbar, tearoff=False)
        mbar.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Preferences", command=lambda: self.prefDetails(self.simulation_is_running))

        self.runMenu = Menu(mbar, tearoff=False)
        mbar.add_cascade(label="Simulation", menu=self.runMenu)
        self.runMenu.add_command(label="Run", command=self.run_simulation)
        self.runMenu.add_command(label="Pause", command=self.pause_simulation)
        self.runMenu.add_command(label="Resume", command=self.resume_simulation)
        self.runMenu.add_command(label="Results", command=self.window_results)
        self.runMenu.entryconfig("Results", state="disable")

        appMenu = Menu(mbar, tearoff=False)
        mbar.add_cascade(label="Help", menu=appMenu)
        appMenu.add_command(label='About SDN_Simulator', command=self.about)

    # Funcion convertJsonUnicode, encargada de convertir de un formato de json a unicode, ya que hay ciertas partes
    # del programa que es necesario realizar esta conversion.
    def convertJsonUnicode(self, text):
        if isinstance(text, dict):
            return {self.convertJsonUnicode(key): self.convertJsonUnicode(value) for key, value in text.iteritems()}
        elif isinstance(text, list):
            return [self.convertJsonUnicode(element) for element in text]
        else:
            return text

    # Funcion saveGraph, encargada de guardar el estado de la topologia o de la simulacion (en el caso de que se haya
    # ejecutado alguna simulacion sobre esta) en el formato json. Se almacena la topologia en si, la informacion de
    # cada uno de los Switches, controladores, hosts, la carga y la informacion de los enlaces, los paquetes generados
    # por cada host, los eventos que se han producido en la simulacion de eventos discretos, etc.
    def saveGraph(self):
        try:
            path = filedialog.asksaveasfile(title='Save Topology', initialdir='./Graphs',
                                            filetypes=(('Files .json', '*.json'), (('All Files', '*.*'))))
            inf = json.dumps(json_graph.cytoscape_data(graph.get_graph()), indent=4, cls=MyEncoder)
            f = open(path.name, 'w')
            f.write(inf)
            f.close()
        except Exception as er:
            return

    # Funcion loadGraph, encargada de cargar la topologia guardada en un fichero en formato json.
    def loadGraph(self):

        path = filedialog.askopenfile(title='Load Graph', initialdir='./Graphs',
                                      filetypes=(('Files .txt', '*.json'), (('All Files', '*.*'))))
        if path is None:
            return
        # Leemos el fichero json
        try:
            edit_topo = json.load(open(path.name))
        except:
            return

        g = nx.Graph()
        if 'hosts' in edit_topo:
            for i in edit_topo['hosts']:
                if 'hostname' in i['opts']:
                    g.add_node(i['opts']['hostname'])
                if 'mac' in i['opts']:
                    g.nodes[i['opts']['hostname']]['mac'] = i['opts']['mac']
                if 'ip' in i['opts']:
                    g.nodes[i['opts']['hostname']]['ip'] = i['opts']['ip']
                if 'port' in i['opts']:
                    g.nodes[i['opts']['hostname']]['port'] = i['opts']['port']
                if 'x' in i:
                    g.nodes[i['opts']['hostname']]['x'] = i['x']
                if 'y' in i:
                    g.nodes[i['opts']['hostname']]['y'] = i['y']

        if 'controllers' in edit_topo:
            for i in edit_topo['controllers']:
                if 'hostname' in i['opts']:
                    g.add_node(i['opts']['hostname'])
                if 'mac' in i['opts']:
                    g.nodes[i['opts']['hostname']]['mac'] = i['opts']['mac']
                if 'ip' in i['opts']:
                    g.nodes[i['opts']['hostname']]['ip'] = i['opts']['remoteIP']
                if 'port' in i['opts']:
                    g.nodes[i['opts']['hostname']]['port'] = str(i['opts']['remotePort'])
                if 'x' in i:
                    g.nodes[i['opts']['hostname']]['x'] = i['x']
                if 'y' in i:
                    g.nodes[i['opts']['hostname']]['y'] = i['y']

        if 'switches' in edit_topo:
            for i in edit_topo['switches']:
                if 'hostname' in i['opts']:
                    g.add_node(i['opts']['hostname'])
                if 'mac' in i['opts']:
                    g.nodes[i['opts']['hostname']]['mac'] = i['opts']['mac']
                if 'ip' in i['opts']:
                    g.nodes[i['opts']['hostname']]['ip'] = i['opts']['ip']
                if 'port' in i['opts']:
                    g.nodes[i['opts']['hostname']]['port'] = str(i['opts']['port'])
                g.nodes[i['opts']['hostname']]['flow_table'] = []
                if 'x' in i:
                    g.nodes[i['opts']['hostname']]['x'] = i['x']
                if 'y' in i:
                    g.nodes[i['opts']['hostname']]['y'] = i['y']
                if 'controllers' in i['opts']:
                    g.add_edges_from([(i['opts']['hostname'], i['opts']['controllers'][0], {'bw': sys.maxsize})])

        if 'links' in edit_topo:
            for i in edit_topo['links']:

                if 'bw' in i['opts'] and 'distance' in i['opts'] and 'propagation_speed' in i['opts']:
                    g.add_edge(i['src'], i['dest'], bw=1 / int(i['opts']['bw']), distance=int(i['opts']['distance']),
                               propagation_speed=int(i['opts']['propagation_speed']), load=[])

        graph.set_graph(g)
        self.TopoInfo()
        self.createNodes()

    # Funcion customize_topology. Esta contiene la llamada de la herramienta customizetopology, la cual abrira ficha
    # herramienta permitiendonos editar una topologia desde 0 o modificar una que hallamos creado anterioemente.
    def customize_topology(self):
        root = tkinter.Toplevel()
        root.iconbitmap('./Arch/red.ico')
        edit_topology = edit.customize_topology(root)

    # Funcion pause_simulation, encargada de detener cada uno de los hilos que estan realizando la ejecucion de cada
    # animacion de movimiento de los paquetes y del hilo que esta ejecutando el propio simulador de eventos discretos.
    # Esta funcion almacena el instante de tiempo en el que la simulacion se detiene para que al reanudar la ejecucion
    # siga por el instante de tiempo en el que se detuvo la ejecucion de esta.
    def pause_simulation(self):
        self.stop_simulation = True
        self.time_start_pause = self.current_milli_time()

        for thread in self.list_threads:
            len(self.list_threads)
            if not thread.is_alive():
                self.list_threads.pop(self.list_threads.index(thread))
            else:
                thread.pause()

    # Funcion resume_simulation, encargada de realizar la pausa de la ejecucion de cada uno de los hilos que estan
    # ejecutando la animacion de movimiento de un paquete y la propia ejecucion del simulador de eventos discretos.
    def resume_simulation(self):
        self.stop_simulation = False
        self.time_pause += self.current_milli_time() - self.time_start_pause
        for thread in self.list_threads:
            thread.resume()

    # Funcion about, encargada de mostrar al usuario la informacion relativa al creador del simulador, los turores que
    # han supervisdado este proyecto, la fecha de publicacion, etc.
    def about(self):
        about = self.aboutBox
        if about is None:
            bg = 'white'
            about = Toplevel(bg='white')
            about.title('About')
            desc = self.appName + ': a discrete event simulator.'
            version = self.appName + ' ' + SDN_Simulator_VERSION
            author = 'Author: Cristian Cruz Carrasco <ccruzcar@alumnos.unex.es>, \n <cristiancruzcarrasco999@gmail.com> \nSeptember 2021\n\n University of Extremadura'
            enhancements = 'Supervisors: Javier Carmona Murillo, Jesús Manuel Calle Cancho.'
            line1 = Label(about, text=desc, font='Helvetica 10 bold', bg=bg)
            line2 = Label(about, text=version, font='Helvetica 9', bg=bg)
            line3 = Label(about, text=author, font='Helvetica 9', bg=bg)
            line4 = Label(about, text=enhancements, font='Helvetica 9', bg=bg)
            line1.pack(padx=20, pady=10)
            line2.pack(pady=10)
            line3.pack(pady=10)
            line4.pack(pady=10)
            hide = (lambda about=about: about.withdraw())
            self.aboutBox = about
            Wm.wm_protocol(about, name='WM_DELETE_WINDOW', func=hide)
        about.deiconify()

    # Funcion link_details, encargada de mostrar las caracteristicas de un enlace seleccionado haciendo para ello la
    # llamada a la funcion InfoLinkWindow.
    def link_details(self):
        if self.selection is None:
            return
        link = self.selection
        linkDetail = self.links[link]
        src = linkDetail['src']
        dst = linkDetail['dest']
        srcName, dstName = src['text'], dst['text']
        root = tkinter.Toplevel()
        info_s = info_link.InfoLinkWindow(root, graph.get_graph().edges[srcName, dstName], srcName + ',' + dstName)
        info_s.initialize_user_interface()

    # Funcion prefDetails, encargada de mostrar las preferencias del simulador.
    def prefDetails(self, simulation_is_running):
        prefDefaults = self.appPrefs
        prefBox = PrefsDialog(self, title='Preferences', prefDefaults=prefDefaults,
                              simulation_running=simulation_is_running)
        if prefBox.result:
            self.appPrefs = prefBox.result

    # Funcion show_switch_info, encargada de mostrar la informacion relativa al switch seleccionado haciendo para ello
    # la llamada a la funcion InfoSwitchWindow.
    def show_switch_info(self, _ignore=None):
        if (self.selection is None or
                self.selection not in self.itemToWidget):
            return
        root = tkinter.Toplevel()
        name = self.itemToWidget[self.selection]['text']
        info_s = info_switch.InfoSwitchWindow(root, graph.get_graph().nodes[name], name)
        info_s.initialize_user_interface()

    # Funcion do_linkPopup, encargada de mostrar el menu emergente de un enlace.
    def do_linkPopup(self, event):
        try:
            self.linkPopup.post(event.x_root, event.y_root)
            self.linkPopup.focus_set()
        finally:
            self.linkPopup.grab_release()

    # Funcion do_controllerPopup, que en principio, no hace nada.
    def do_controllerPopup(self, event):
        return

    # Funcion do_legacyRouterPopup, encargada de mostrar el menu emergente de un legacyRouter (que en principio
    # no usaremos).
    def do_legacyRouterPopup(self, event):
        try:
            self.legacyRouterPopup.post(event.x_root, event.y_root)
            self.legacyRouterPopup.focus_set()
        finally:
            self.legacyRouterPopup.grab_release()

    # Funcion do_hostPopup, encargado de mostrar el menu emergente de un host.
    def do_hostPopup(self, event):
        try:
            self.hostPopup.post(event.x_root, event.y_root)
            self.hostPopup.focus_set()
        finally:
            self.hostPopup.grab_release()

    # Funcion do_legacySwitchPopup, encargada de mostrar el menu emergente de un legacySwitch (que en principio
    # no usaremos).
    def do_legacySwitchPopup(self, event):
        try:
            self.switchPopup.post(event.x_root, event.y_root)
            self.switchPopup.focus_set()

        finally:
            self.switchPopup.grab_release()

    # Funcion do_switchPopup, encargada de mostrar el menu emergente de un switch.
    def do_switchPopup(self, event):
        try:
            self.switchPopup.post(event.x_root, event.y_root)
            self.switchPopup.focus_set()
        finally:
            self.switchPopup.grab_release()

    # Funcion stop, encargada de reiniciar el terminal aunque no se haya salido del CLI correctamente y borrar las
    # colas de paquetes.
    def stop(self):
        for q in self.flowQueues:
            self.flowQueues[q].queue.clear()

    # Funcion quit, encargada de reiniciar el terminal aunque no se haya salido del CLI correctamente y borrar las
    # colas de paquetes mediante la llamada a la funcion stop y eliminando el frame.
    def quit(self):
        self.stop()
        Frame.quit(self)

    # Funcion traffic_insertion, encargada de mostrar la ventana de insercion de trafico de un host seleccionado
    # llamando para ello a la funcion PacketImportWindow.
    def traffic_insertion(self):
        root = tkinter.Toplevel()
        is_correct = True
        try:
            name = self.itemToWidget[self.selection]['text']
        except:
            is_correct = False
        if is_correct and name[0] == 'h':
            p_import_w.PacketImportWindow(root=root, master=self, host=name, graph=graph)

    # Funcion find_timeGeneration_timeArrive, encargada de devolver el tiempo en el que se genero y llego un paquete;
    # ademas de devolver el numero de saltos que ha realizado dicho paquete y el host que lo genero.
    def find_timeGeneration_timeArrive(self, id_packet):

        time_generation = 0
        time_arrive = 0
        number_jumps = 0
        host = 0

        for i in self.list_processed_events:
            if i != 0:
                if i['type'] == 'packet_generation' and i['packet_id'] == str(id_packet):
                    time_generation = i['time_spawn']
                    host = i['src']
                elif i['type'] == 'packet_processing_host' and i['packet_id'] == str(id_packet):
                    time_arrive = i['time_spawn']
                elif (i['type'] == 'packet_processing_switch' or i['type'] == 'packet_processing_controller' or i[
                    'type'] == 'packet_processing_host') and i['packet_id'] == str(id_packet):
                    if 'openflow_id' in i:
                        openflow_message = self.packets_openflow[i['openflow_id']]
                        if openflow_message['type'] == 'packet_out' or openflow_message['type'] == 'packet_in':
                            number_jumps += 1
                    else:
                        number_jumps += 1

        return time_generation, time_arrive, number_jumps, host

    # Funcion current_milli_time, encargada de devolver el tiempo actual en segundos.
    def current_milli_time(self):
        return round(time.time() * 1000)

    # Funcion processing_event, encargada de realizar el tratamiento de los eventos que van saliendo de la lista de
    # eventos discretos realizando la llamada a si mismo para procesar el siguiente evento (mediante otro hilo cada
    # 1 ms) y a las diferentes funciones destinadas al tratamiento de cada uno de los diferentes tipos de eventos.
    # Cada vez que se ejecuta este metodo, se comprueba si el evento se tiene que ejecutar en el tiempo de ejecucion de
    # la simulacion en el que le corresponde segun su tiempo de generacion. Ademas, realiza la actualizacion del
    # cronometro que aparece en la simulacion haciendo la llamada al metodo update_chronometer.
    def processing_event(self):
        time = (self.current_milli_time() - self.start)
        if not self.stop_simulation:
            self.update_chronometer(time - self.time_pause)
        if self.event != 0:
            threading.Timer(1.0 / 1000.0, self.processing_event).start()

        if self.event != 0 and float(self.event['time_spawn']) * 1000.0 <= (
                time - self.time_pause) and self.stop_simulation == False:

            if self.event['type'] == 'packet_generation':
                new_event = graph.processing_event_packet_generation(self.event, self.packets_data)
                if new_event != 0: self.discrete_events.inser_event(new_event)
            if self.event['type'] == 'packet_propagation':
                new_event = graph.processing_event_packet_propagation2(self.event, self.packets_data,
                                                                       self.packets_openflow, app)
                self.discrete_events.inser_event(new_event)

            if self.event['type'] == 'packet_processing_switch':
                new_event = graph.processing_event_packet_match_and_action_switch(self.event, self.packets_data,
                                                                                  self.packets_openflow)
                if new_event != 0:
                    self.discrete_events.inser_event(new_event)

            if self.event['type'] == 'packet_processing_controller':
                new_event = graph.processing_event_packet_controller_action(self.event, self.packets_data,
                                                                            self.packets_openflow,
                                                                            self.appPrefs['reactive_proactive'])
                if len(new_event) > 0:
                    for i in new_event:
                        self.discrete_events.inser_event(i)
            if self.event['type'] == 'packet_processing_host':
                if 'load' in graph.get_graph().edges[self.event['src'], self.event['dst']] and len(
                        graph.get_graph().edges[self.event['src'], self.event['dst']]['load']) > 0:
                    last_load = graph.get_graph().edges[self.event['src'], self.event['dst']]['load'][-1][1]
                else:
                    last_load = 0
                packet = self.packets_data[self.event['packet_id']]
                load_packet = len(packet)
                new_load = last_load - load_packet

                if 'load' in graph.get_graph().edges[self.event['src'], self.event['dst']]:
                    graph.get_graph().edges[self.event['src'], self.event['dst']]['load'].append(
                        (self.event['time_spawn'], new_load))  # TODO ooo
            self.event = self.discrete_events.unqueue_list_events()
            self.list_processed_events.append(self.event)

        elif self.event == 0:
            self.final_time = self.current_milli_time() - self.start - self.time_pause
            self.processing_results()
            self.simulation_is_running = False
            information = []

            for event in self.list_processed_events:

                if event != 0:
                    information.append(str(list(event.items())))

            graph.get_graph().graph['event_list'] = information
            information = []

            for i, j in self.packets_data.items():
                information.append(
                    'Packet Id: ' + str(i) + ' Packet Information: ' + str(list(j)) + ' Packet Lenght: ' + str(len(j)))
            graph.get_graph().graph['packey_list'] = information
            information = []

            for i, j in self.packets_openflow.items():
                information.append('Openflow Message Id: ' + str(i) + ' Information: ' + str(list(j.items())))

            graph.get_graph().graph['openflow_list'] = information

    # Funcion update_chronometer, encargada de actualizar el cronometro de nuestra simulacion, mostrando los minutos,
    # segundos y milisegundos de la ejecucion de dicha simulacion.
    def update_chronometer(self, milliseconds):
        milli = math.trunc(milliseconds % 1000)
        seconds = math.trunc((milliseconds / 1000) % 60)
        minutes = math.trunc((milliseconds / (1000 * 60)) % 60)
        Label(self.cframe, text='\n Simulation Time \n\n' + str(minutes) + ':' + str(seconds) + ':' + str(milli),
              padx=3, pady=3, relief="ridge").grid(row=0, column=1, sticky='NE', padx=3, pady=3)

    # Funcion run_simulation, encargada de iniciar la ejecucion del simulador de eventos discretos inicializando del
    # tiempo de inicio de la simulacion, inicializando la lista de paquetes de datos, de mensajes openflow y eventos.
    # Para iniciar el tratamiento de los eventos en la cola de eventos discretos, se emplea la funcion processing_event
    # ya mencionada anteriormente.
    def run_simulation(self):

        self.simulation_is_running = True
        self.packets_data = {}
        self.packets_openflow = {}
        self.event_queue = []
        self.discrete_events = DiscreteEvents(initial_event_list=self.event_queue,
                                              initial_packets_list=self.packets_data,
                                              initial_openflow_list=self.packets_openflow)
        i = 0
        if len(self.info_window_import) > 0:
            for host in self.info_window_import:
                if len(self.info_window_import[host]) > 0:
                    cola_eventos = self.info_window_import[host]
                    for paquet in cola_eventos:
                        self.packets_data[str(i)] = paquet[0]
                        self.discrete_events.inser_event(
                            {'type': 'packet_generation', 'src': host, 'dst': None, 'time_spawn': paquet[1],
                             'packet_id': str(i)})
                        i += 1

        self.event = self.discrete_events.unqueue_list_events()
        self.list_processed_events.append(self.event)
        self.start = self.current_milli_time()
        self.stop_simulation = False
        self.update_chronometer(self.start)
        threading.Timer(1.0 / 1000.0, self.processing_event).start()

    # Funcion find_packet_equal, encargada de encontrar paquetes iguales (pertenecientes al mismo flujo).
    def find_packet_equal(self, list_packet, packet):
        for i in list_packet:
            if 'TCP' in packet:
                protocol = 'TCP'
            else:
                protocol = 'UDP'

            if 'TCP' in i[1]:
                protocol_2 = 'TCP'
            else:
                protocol_2 = 'UDP'

            if i[1][Ether].src == packet[Ether].src and i[1][Ether].dst == packet[Ether].dst and \
                    i[1][IP].src == packet[IP].src and i[1][IP].dst == packet[IP].dst and protocol_2 == protocol \
                    and i[1][protocol].sport == packet[protocol].sport and \
                    i[1][protocol].dport == packet[protocol].dport:
                return i[0]
            # if i[1] == packet:
            #     return i[0]
        return None

    # Funcion processing_results, encargada de procesar la informacion tras haberse realizado la simulacion calculando
    # el delay por paquete.
    def processing_results(self):
        self.list_flow = {}
        list_packet = []

        for id_packet, packet in self.packets_data.items():
            time_generation, time_arrive, number_jumps, host = self.find_timeGeneration_timeArrive(id_packet)

            if self.appPrefs['flowTime'] == 30:
                animation_propagation_time = 3.5
            else:
                animation_propagation_time = 1.0

            delay = (time_arrive - time_generation - (animation_propagation_time * (number_jumps + 1))) * 1000
            id = self.find_packet_equal(list_packet, packet)

            if host not in self.list_flow:
                self.list_flow[host] = {}
            if id == None:

                self.list_flow[host][id_packet] = fl_inf.flow_information(packet)
                self.list_flow[host][id_packet].add_delay(delay, time_generation)
                list_packet.append((id_packet, packet, time_generation))
            else:
                self.list_flow[host][id].add_delay(delay, time_generation)

        self.runMenu.entryconfig("Results", state="normal")

    # Funcion window_results, encargada de mostrar los resultados de la simulacion (graficas) mediante la funcion
    # ResultInformation.
    def window_results(self):
        root = tkinter.Toplevel()
        resultInfor.ResultInformation(root=root, master=self, graph=graph,
                                      list_flow=self.list_flow, final_time=self.final_time)


# Funcion miniImages, encargada de crear y devolver imagenes que seran usadas por nuestro simulador (imagenes de los
# hosts, switches, controladores...).
def miniImages():
    return {
        'Select': BitmapImage(
            file='Arch\left_ptr'),

        # Convertir a base 64: https://onlinepngtools.com/convert-png-to-base64

        'Switch': PhotoImage(data=r"""
iVBORw0KGgoAAAANSUhEUgAAAG4AAAA1CAYAAACgEt7PAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAStdEVYdG14ZmlsZQAlM0NteGZpbGUlMjBob3N0JTNEJTIyRWxlY3Ryb24lMjIlMjBtb2RpZmllZCUzRCUyMjIwMjEtMDMtMDlUMjAlM0E1MSUzQTE0LjgzNFolMjIlMjBhZ2VudCUzRCUyMjUuMCUyMChXaW5kb3dzJTIwTlQlMjAxMC4wJTNCJTIwV2luNjQlM0IlMjB4NjQpJTIwQXBwbGVXZWJLaXQlMkY1MzcuMzYlMjAoS0hUTUwlMkMlMjBsaWtlJTIwR2Vja28pJTIwZHJhdy5pbyUyRjE0LjEuOCUyMENocm9tZSUyRjg3LjAuNDI4MC44OCUyMEVsZWN0cm9uJTJGMTEuMS4xJTIwU2FmYXJpJTJGNTM3LjM2JTIyJTIwZXRhZyUzRCUyMlJsMGxZekhIU2dsdUhLYVIycWloJTIyJTIwdmVyc2lvbiUzRCUyMjE0LjEuOCUyMiUyMHR5cGUlM0QlMjJkZXZpY2UlMjIlM0UlM0NkaWFncmFtJTIwaWQlM0QlMjJZTVYwbmpDMEw0VzRkdDFodDh1eSUyMiUyMG5hbWUlM0QlMjJQJUMzJUExZ2luYS0xJTIyJTNFeFZUQmpwc3dFUDBhamtXQVE1TWNHN0xwcW1wWGxkS3F4NVVERG96V1pxanRKS1JmM3pFWUVvUlcyejJWZzdIZnpOZ3o4NTRkc0V5MW56VnZxbTlZQ0Jra1VkRUdiQnNreVhLeHB0RUIxeDVJVjZ3SFNnMUZEOFUzWUE5JTJGaEFjamo1NmdFR2JpYUJHbGhXWUs1bGpYSXJjVGpHdU5sNm5iRWVYMDFJYVhZZ2JzY3k3bjZDOG9iTldqcTJSNXd4OEZsTlZ3Y3Z6UkY2ejQ0T3dyTVJVdjhISUhzWWVBWlJyUjlqUFZaa0s2M2cxOTZlTjJyMWpIeExTbzdiOEVzTU1YRXgwdnpZJTJGajB5TmVuJTJCS2Y3ZTczQjclMkZMbWN1VEw5Z25hNjlEQnhxRTJuWmRURGRCdWczWWhwdW1iJTJGVVJXa0c3YnlxckpDMWpaNU5RMWpUUEtTdWhDUmpMam1oUmNGTzVp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
            """),

        'LegacySwitch': PhotoImage(data=r"""
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
4BE2eIRYeHAEIBwBP0Y4Qn41YWRSCQgAOw==
            """),

        'LegacyRouter': PhotoImage(data=r"""
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
gGPLHwLwcMIo12Qxu0ABAQA7
            """),

        'Controller': PhotoImage(data=r"""
iVBORw0KGgoAAAANSUhEUgAAAG8AAABbCAYAAAB9LtvbAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAStdEVYdG14ZmlsZQAlM0NteGZpbGUlMjBob3N0JTNEJTIyRWxlY3Ryb24lMjIlMjBtb2RpZmllZCUzRCUyMjIwMjEtMDMtMDlUMjAlM0E1MSUzQTE0LjgzNFolMjIlMjBhZ2VudCUzRCUyMjUuMCUyMChXaW5kb3dzJTIwTlQlMjAxMC4wJTNCJTIwV2luNjQlM0IlMjB4NjQpJTIwQXBwbGVXZWJLaXQlMkY1MzcuMzYlMjAoS0hUTUwlMkMlMjBsaWtlJTIwR2Vja28pJTIwZHJhdy5pbyUyRjE0LjEuOCUyMENocm9tZSUyRjg3LjAuNDI4MC44OCUyMEVsZWN0cm9uJTJGMTEuMS4xJTIwU2FmYXJpJTJGNTM3LjM2JTIyJTIwZXRhZyUzRCUyMlJsMGxZekhIU2dsdUhLYVIycWloJTIyJTIwdmVyc2lvbiUzRCUyMjE0LjEuOCUyMiUyMHR5cGUlM0QlMjJkZXZpY2UlMjIlM0UlM0NkaWFncmFtJTIwaWQlM0QlMjJZTVYwbmpDMEw0VzRkdDFodDh1eSUyMiUyMG5hbWUlM0QlMjJQJUMzJUExZ2luYS0xJTIyJTNFeFZUQmpwc3dFUDBhamtXQVE1TWNHN0xwcW1wWGxkS3F4NVVERG96V1pxanRKS1JmM3pFWUVvUlcyejJWZzdIZnpOZ3o4NTRkc0V5MW56VnZxbTlZQ0Jra1VkRUdiQnNreVhLeHB0RUIxeDVJVjZ3SFNnMUZEOFUzWUE5JTJGaEFjamo1NmdFR2JpYUJHbGhXWUs1bGpYSXJjVGpHdU5sNm5iRWVYMDFJYVhZZ2JzY3k3bjZDOG9iTldqcTJSNXd4OEZsTlZ3Y3Z6UkY2ejQ0T3dyTVJVdjhISUhzWWVBWlJyUjlqUFZaa0s2M2cxOTZlTjJyMWpIeExTbzdiOEVzTU1YRXgwdnpZJTJGajB5TmVuJTJCS2Y3ZTczQjclMkZMbWN1VEw5Z25hNjlEQnhxRTJuWmRURGRCdWczWWhwdW1iJTJGVVJXa0c3YnlxckpDMWpaNU5RMWpUUEtTdWhDUmpMam1oUmNGTzVp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
            """),

        'Host': PhotoImage(data=r"""
            iVBORw0KGgoAAAANSUhEUgAAAC8AAAAkCAYAAAAZ4GNvAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANZSURBVFhH7ZjPSxtBFMffRq3EmDQoRDEqRKlKQKp4CV5URGlBr6X3FtpLvLT2kJhoVnPrSWkp7aF/QAs9e4gteJFgvQhKVRT8EUVEYzQN5ofpm+GxbUxisilkV8gHBve9ncl8Z3zzZmfgLiPQX3C73aOCIMTIzEl1dfWv8fHxHTIVgYt3Op2jdXV1n/GxjNl5Eg4Gg49x0KtkFx0uXhTFTy0tLc87Ojq4Mx/8fv/vo6OjN9j2HbmKDhc/PT09297ebscBcGcm5ufn4fr6miyAZDLJShxDLUGuooF9fnS5XGOyxA8NDbGG5FGG7e1t2NjYmJPEezyeDwaD4YVer+cVMnF4eAgjIyPQ1dVFnuLDhC8vL0viNeQHnU4HtbW1WYvSM54JLl6j0USNRiM0NTVlLaoVf1cpiVeKknilkMSzHfOuwcXjtn8vFArxjShbUePgpJm/uLiAQCCQtahWPNukzGYzDAwM8O+Xnp6etIJ1eAM1kaKosbERLBYLWeonRfz+/j7s7Ch6OJJFini2aE9PT8lSP+oLZBmUxCuFdAxsa2uzt7a2cmcm2DFweHgYysryv2D498x7G3LS8ObmZuoxMF/x8XicLOlzgqm7bffKOVKcjGQikchvlAS2eS9L/E1WVlYuMbWOiaLI7nsyMjU1lWTn3mzs7u7C+vr6F6fT+YRcsigtWKXgYeP1ekU8gLsaGhq4MxdsIR4fH7Mbs1domioqKl4yN3+Zihnf0WNmcB1FcP2k7Yzl5eUn0Wj0mdvt/kmuNLh4u91uaG5ufo2VrdybB1qt9sfZ2dmlTqeb7e7u1m9tbdGbwrBarbC2tkYWQFVVFRwcHARisdhDj8dzQu4UuPhCmJyc7McU5+vt7dVgB//9WVFTUwOYdeD8/JzbODkQiUSSuKj9DofDxp03kHMrLDExMWHBcPiOM641mUywt7fHv4uurq4KLuzeqL6+nt+KMTscDkNnZ6eAv3vfZrNZFxYWvlH3ErJnHmdcU1lZuYpp1Zortfp8PnpKB2Ma+vr6yPoLE720tEQWwODgICwuLgbxP/IWU6+X3BzZ4mdmZnzYcT/GZIhcWcEwuDWb4WaTtshvtmF1BEEwYlgmMFE8xfj/Sq8KmvlH9FhUcH09wL7nyEQA/gCxR5oVwYOagwAAAABJRU5ErkJggg==
        """),

        'OldSwitch': PhotoImage(data=r"""
            R0lGODlhIAAYAPcAMf//////zP//mf//Zv//M///AP/M///MzP/M
            mf/MZv/MM//MAP+Z//+ZzP+Zmf+ZZv+ZM/+ZAP9m//9mzP9mmf9m
            Zv9mM/9mAP8z//8zzP8zmf8zZv8zM/8zAP8A//8AzP8Amf8AZv8A
            M/8AAMz//8z/zMz/mcz/Zsz/M8z/AMzM/8zMzMzMmczMZszMM8zM
            AMyZ/8yZzMyZmcyZZsyZM8yZAMxm/8xmzMxmmcxmZsxmM8xmAMwz
            /8wzzMwzmcwzZswzM8wzAMwA/8wAzMwAmcwAZswAM8wAAJn//5n/
            zJn/mZn/Zpn/M5n/AJnM/5nMzJnMmZnMZpnMM5nMAJmZ/5mZzJmZ
            mZmZZpmZM5mZAJlm/5lmzJlmmZlmZplmM5lmAJkz/5kzzJkzmZkz
            ZpkzM5kzAJkA/5kAzJkAmZkAZpkAM5kAAGb//2b/zGb/mWb/Zmb/
            M2b/AGbM/2bMzGbMmWbMZmbMM2bMAGaZ/2aZzGaZmWaZZmaZM2aZ
            AGZm/2ZmzGZmmWZmZmZmM2ZmAGYz/2YzzGYzmWYzZmYzM2YzAGYA
            /2YAzGYAmWYAZmYAM2YAADP//zP/zDP/mTP/ZjP/MzP/ADPM/zPM
            zDPMmTPMZjPMMzPMADOZ/zOZzDOZmTOZZjOZMzOZADNm/zNmzDNm
            mTNmZjNmMzNmADMz/zMzzDMzmTMzZjMzMzMzADMA/zMAzDMAmTMA
            ZjMAMzMAAAD//wD/zAD/mQD/ZgD/MwD/AADM/wDMzADMmQDMZgDM
            MwDMAACZ/wCZzACZmQCZZgCZMwCZAABm/wBmzABmmQBmZgBmMwBm
            AAAz/wAzzAAzmQAzZgAzMwAzAAAA/wAAzAAAmQAAZgAAM+4AAN0A
            ALsAAKoAAIgAAHcAAFUAAEQAACIAABEAAADuAADdAAC7AACqAACI
            AAB3AABVAABEAAAiAAARAAAA7gAA3QAAuwAAqgAAiAAAdwAAVQAA
            RAAAIgAAEe7u7t3d3bu7u6qqqoiIiHd3d1VVVURERCIiIhEREQAA
            ACH5BAEAAAAALAAAAAAgABgAAAhwAAEIHEiwoMGDCBMqXMiwocOH
            ECNKnEixosWB3zJq3Mixo0eNAL7xG0mypMmTKPl9Cznyn8uWL/m5
            /AeTpsyYI1eKlBnO5r+eLYHy9Ck0J8ubPmPOrMmUpM6UUKMa/Ui1
            6saLWLNq3cq1q9evYB0GBAA7
        """),

        'NetLink': PhotoImage(data=r"""
            R0lGODlhFgAWAPcAMf//////zP//mf//Zv//M///AP/M///MzP/M
            mf/MZv/MM//MAP+Z//+ZzP+Zmf+ZZv+ZM/+ZAP9m//9mzP9mmf9m
            Zv9mM/9mAP8z//8zzP8zmf8zZv8zM/8zAP8A//8AzP8Amf8AZv8A
            M/8AAMz//8z/zMz/mcz/Zsz/M8z/AMzM/8zMzMzMmczMZszMM8zM
            AMyZ/8yZzMyZmcyZZsyZM8yZAMxm/8xmzMxmmcxmZsxmM8xmAMwz
            /8wzzMwzmcwzZswzM8wzAMwA/8wAzMwAmcwAZswAM8wAAJn//5n/
            zJn/mZn/Zpn/M5n/AJnM/5nMzJnMmZnMZpnMM5nMAJmZ/5mZzJmZ
            mZmZZpmZM5mZAJlm/5lmzJlmmZlmZplmM5lmAJkz/5kzzJkzmZkz
            ZpkzM5kzAJkA/5kAzJkAmZkAZpkAM5kAAGb//2b/zGb/mWb/Zmb/
            M2b/AGbM/2bMzGbMmWbMZmbMM2bMAGaZ/2aZzGaZmWaZZmaZM2aZ
            AGZm/2ZmzGZmmWZmZmZmM2ZmAGYz/2YzzGYzmWYzZmYzM2YzAGYA
            /2YAzGYAmWYAZmYAM2YAADP//zP/zDP/mTP/ZjP/MzP/ADPM/zPM
            zDPMmTPMZjPMMzPMADOZ/zOZzDOZmTOZZjOZMzOZADNm/zNmzDNm
            mTNmZjNmMzNmADMz/zMzzDMzmTMzZjMzMzMzADMA/zMAzDMAmTMA
            ZjMAMzMAAAD//wD/zAD/mQD/ZgD/MwD/AADM/wDMzADMmQDMZgDM
            MwDMAACZ/wCZzACZmQCZZgCZMwCZAABm/wBmzABmmQBmZgBmMwBm
            AAAz/wAzzAAzmQAzZgAzMwAzAAAA/wAAzAAAmQAAZgAAM+4AAN0A
            ALsAAKoAAIgAAHcAAFUAAEQAACIAABEAAADuAADdAAC7AACqAACI
            AAB3AABVAABEAAAiAAARAAAA7gAA3QAAuwAAqgAAiAAAdwAAVQAA
            RAAAIgAAEe7u7t3d3bu7u6qqqoiIiHd3d1VVVURERCIiIhEREQAA
            ACH5BAEAAAAALAAAAAAWABYAAAhIAAEIHEiwoEGBrhIeXEgwoUKG
            Cx0+hGhQoiuKBy1irChxY0GNHgeCDAlgZEiTHlFuVImRJUWXEGEy
            lBmxI8mSNknm1Dnx5sCAADs=
        """),

        'Logo': PhotoImage(
            data="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")

    }


if __name__ == "__main__":
    try:
        graph = p.NetworkTopology()
        style = Style(theme='TFG', themes_file='./Arch/Themes.json')
        window = style.master
        window.iconbitmap('./Arch/red.ico')
        app = SDN_Simulator()
        app.mainloop()
    except KeyboardInterrupt:
        app.stop()

    except Exception:
        type_, val_, trace_ = sys.exc_info()
        line = sys.exc_info()[-1].tb_lineno
        errorMsg = ("-" * 80 + "\n" +
                    "Caught exception on line %d." % (line) +
                    " Cleaning up...\n\n" + "%s: %s\n" % (type_.__name__, val_) +
                    "-" * 80 + "\n")
        error(errorMsg)
        import traceback

        stackTrace = traceback.format_exc()
        app.stop()
