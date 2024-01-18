import json
import os
from subprocess import call
from tkinter import (Frame, Label, LabelFrame, Entry, Menu, Toplevel, Button, BitmapImage,
                     PhotoImage, Canvas, Scrollbar, Wm, TclError,
                     StringVar, W, NW, Y, VERTICAL, SOLID,
                     RIGHT, LEFT, BOTH, TRUE, FALSE, N)
from tkinter import filedialog as tkFileDialog
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import simpledialog as tkSimpleDialog

import networkx as nx

import Utilities

message_help = '  o   Valid Port value: [1, 65535] \n\n' \
               '  o   IP address format:\n\n' \
               '              <num_1>.<num_2>.<num_3>.<num_4>\n\n' \
               '      (from 0 to 255, both included)\n\n' \
               '  o   MAC address format:\n\n' \
               '            <val1>:<val2>:<val3>:<val4>:<val5>:<val6>\n\n' \
               '      (from 00 to FF [HEX], both included)\n'

message_help_2 = '  o   Bandwidth, Distance, and Velocity of Propagation\n' \
                 '      values must be a positive integer greater than 0.'


# Clase CustomDialog, encargada de crear una ventana de dialogo personalizada.
class CustomDialog(object):

    # Constructor parametrizado de la clase CustomDialog.
    def __init__(self, master, _title):
        self.top = Toplevel(master)
        self.top.title(_title)
        self.bodyFrame = Frame(self.top)
        self.bodyFrame.grid(row=0, column=0, sticky='N')
        self.body(self.bodyFrame)

        buttonFrame = Frame(self.top, bd=3)
        buttonFrame.grid(row=1, column=0, sticky=N)
        okButton = Button(buttonFrame, width=8, text='OK', command=self.okAction)
        okButton.grid(row=0, column=0, sticky=N, padx=5, pady=5)
        canlceButton = Button(buttonFrame, width=8, text='Cancel', command=self.cancelAction)
        canlceButton.grid(row=0, column=1, sticky=N, padx=5, pady=5)

    # Funcion body, encargada de establecer el frame root.
    def body(self, master):
        self.rootFrame = master

    # Funcion apply, encargada de drestruir la ventana de dialogo mostrada.
    def apply(self):
        self.top.destroy()

    # Funcion cancelAction, encargada de
    def cancelAction(self):
        self.top.destroy()

    # Funcion okAction, encargado de aplicar los cambios y destruir la ventana.
    def okAction(self):
        self.apply()
        self.top.destroy()


# Clase HostDialog, encargada de crear una ventana de dialogo personalizada para mostrar la informacion relativa a un
# host.
class HostDialog(CustomDialog):

    # Constructor parametrizado de la clase HostDialog.
    def __init__(self, master, title, prefDefaults):

        self.port = StringVar()
        self.ip = StringVar()
        self.mac = StringVar()
        self.hostname = StringVar()
        self.prefValues = prefDefaults
        self.result = None
        CustomDialog.__init__(self, master, title)

    # Funcion body, encargado de crear el cuerpo de la ventana de dialogo.
    def body(self, master):

        Label(master, text="Hostname:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        Entry(master, textvariable=self.hostname, state='disabled').grid(row=0, column=1, padx=5, pady=5)
        if 'hostname' in self.prefValues:
            self.hostname.set(self.prefValues['hostname'])

        Label(master, text="MAC Address:").grid(row=1, sticky=W, padx=5, pady=5)
        Entry(master, textvariable=self.mac).grid(row=1, column=1, padx=5, pady=5)
        if 'mac' in self.prefValues:
            self.mac.set(self.prefValues['mac'])

        Label(master, text="IP Address:").grid(row=2, sticky=W, padx=5, pady=5)
        Entry(master, textvariable=self.ip).grid(row=2, column=1, padx=5, pady=5)
        if 'ip' in self.prefValues:
            self.ip.set(self.prefValues['ip'])

        Label(master, text="Port:").grid(row=3, sticky=W, padx=5, pady=5)
        Entry(master, textvariable=self.port).grid(row=3, column=1, padx=5, pady=5)
        if 'port' in self.prefValues:
            self.port.set(self.prefValues['port'])

    # Funcion apply, encargada de establecer los valores introducidos de los diferentes campos de la ventana de
    # dialogo.
    def apply(self):
        results = {
            'hostname': self.hostname.get(),
            'mac': self.mac.get(),
            'ip': self.ip.get(),
            'port': self.port.get(),
        }
        self.result = results


# Clase SwitchDialog, encargada de crear una ventana de dialogo personalizada para mostrar la informacion relativa a un
# host.
class SwitchDialog(CustomDialog):

    # Constructor parametrizado de la clase SwitchDialog.
    def __init__(self, master, title, prefDefaults):
        self.prefValues = prefDefaults
        self.result = None
        self.ip = StringVar()
        self.mac = StringVar()
        self.port = StringVar()
        self.hostame = StringVar()
        CustomDialog.__init__(self, master, title)

    # Funcion body, encargado de crear el cuerpo de la ventana de dialogo.
    def body(self, master):

        Label(master, text="Hostname:").grid(row=0, column=0, sticky=W, padx=10, pady=5)
        Entry(master, textvariable=self.hostame, state='disabled').grid(row=0, column=1, padx=10, pady=5)
        if 'hostname' in self.prefValues:
            self.hostame.set(self.prefValues['hostname'])

        Label(master, text="MAC Address:").grid(row=1, sticky=W, padx=10, pady=5)
        Entry(master, textvariable=self.mac).grid(row=1, column=1, padx=10, pady=5)
        if 'mac' in self.prefValues:
            self.mac.set(self.prefValues['mac'])

        Label(master, text="IP Address:").grid(row=2, sticky=W, padx=10, pady=5)
        Entry(master, textvariable=self.ip).grid(row=2, column=1, padx=10, pady=5)
        if 'ip' in self.prefValues:
            self.ip.set(self.prefValues['ip'])

    # Funcion apply, encargada de establecer los valores introducidos de los diferentes campos de la ventana de
    # dialogo.
    def apply(self):

        results = {
            'hostname': self.hostame.get(),
            'mac': self.mac.get(),
            'ip': self.ip.get(),
        }
        self.result = results


# Clase VerticalScrolledTable, marco desplazable de tkinter. Emplea el atributo 'interior' para colocar los widgets
# dentro del marco desplazable (este marco solo permite el desplazamiento vertical).
class VerticalScrolledTable(LabelFrame):

    # Constructor parametrizado de la clase VerticalScrolledTable.
    def __init__(self, parent, rows=2, columns=2, title=None, **kw):
        LabelFrame.__init__(self, parent, text=title, padx=5, pady=5, **kw)

        # Creamos un objeto canvas y una barra de desplazamiento vertical para desplazarlo:
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reiniciamos la vista:
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Creamos un marco dentro del lienzo que se desplazara con el:
        self.interior = interior = TableFrame(canvas, rows=rows, columns=columns)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)

        # Funcion _configure_interior, en el que rastreamos los cambios en el lienzo y el ancho del marco y
        # sincronizarlos, actualizando tambien la barra de desplazamiento.
        def _configure_interior(_event):
            # Actualizamos las barras de desplazamiento para que coincidan con el tamaño del marco interior:
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Actualizamos la anchura del lienzo para que se ajuste al marco interior:
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        # Funcion _configure_canvas, encargado de configurar el canvas que estamos empleando.
        def _configure_canvas(_event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)


# Clase TableFrame, encargada de crear una tabla en un frame. Recoge las funciones necesarias para manejar dicha tabla.
class TableFrame(Frame):

    # Constructor parametrizado de la clase TableFrame.
    def __init__(self, parent, rows=2, columns=2):

        Frame.__init__(self, parent, background="black")
        self._widgets = []
        self.rows = rows
        self.columns = columns
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = Entry(self, borderwidth=0)
                label.grid(row=row, column=column, sticky="wens", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

    # Setter del atributo widget.
    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.insert(0, value)

    # Getter del atributo widget.
    def get(self, row, column):
        widget = self._widgets[row][column]
        return widget.get()

    # Funcion addRow, encargada de aniadir filas en la tabla.
    def addRow(self, value=None, readonly=False):
        current_row = []
        for column in range(self.columns):
            label = Entry(self, borderwidth=0)
            label.grid(row=self.rows, column=column, sticky="wens", padx=1, pady=1)
            if value is not None:
                label.insert(0, value[column])
            if readonly:
                label.configure(state='readonly')
            current_row.append(label)
        self._widgets.append(current_row)
        self.update_idletasks()
        self.rows += 1


# Clase LinkDialog, encargada de crear y mostrar las propiedades de un enlace demiante una ventana de dialogo.
class LinkDialog(tkSimpleDialog.Dialog):

    # Constructor parametrizado de la clase LinkDialog
    def __init__(self, parent, title, linkDefaults):

        self.propagation_speed = StringVar()
        self.distance = StringVar()
        self.bandwidth = StringVar()
        self.linkValues = linkDefaults
        tkSimpleDialog.Dialog.__init__(self, parent, title)

    # Funcion body, encargado de crear el cuerpo de la ventana de dialogo.
    def body(self, master):

        Label(master, text="Bandwidth:").grid(row=0, sticky=W)
        Entry(master, textvariable=self.bandwidth, width=11).grid(row=0, column=1)
        Label(master, text="Mbps").grid(row=0, column=2, sticky=W)
        if 'bw' in self.linkValues:
            self.bandwidth.set(self.linkValues['bw'])
        else:
            self.bandwidth.set(1000)

        Label(master, text="Distance:").grid(row=1, sticky=W)
        Entry(master, textvariable=self.distance, width=11).grid(row=1, column=1)
        Label(master, text="m").grid(row=1, column=2, sticky=W)
        if 'distance' in self.linkValues:
            self.distance.set(self.linkValues['distance'])
        else:
            self.distance.set(1)

        Label(master, text="Propagation Speed:").grid(row=2, sticky=W)
        Entry(master, textvariable=self.propagation_speed, width=11).grid(row=2, column=1)
        Label(master, text="m/s").grid(row=2, column=2, sticky=W)
        if 'propagation_speed' in self.linkValues:
            self.propagation_speed.set(self.linkValues['propagation_speed'])
        else:
            self.propagation_speed.set(240000000)

    # Funcion apply, encargada de establecer los valores introducidos de los diferentes campos de la ventana de
    # dialogo.
    def apply(self):
        self.result = {}
        if len(self.bandwidth.get()) > 0:
            self.result['bw'] = self.bandwidth.get()
        if len(self.distance.get()) > 0:
            self.result['distance'] = self.distance.get()
        if len(self.propagation_speed.get()) > 0:
            self.result['propagation_speed'] = self.propagation_speed.get()


# Clase ControllerDialog, encargada de crear una ventana de dialogo personalizada para mostrar la informacion relativa
# a un controlador.
class ControllerDialog(tkSimpleDialog.Dialog):

    # Constructor parametrizado de la clase ControllerDialog.
    def __init__(self, parent, title, ctrlrDefaults=None):
        self.ip = StringVar()
        self.mac = StringVar()
        self.port = StringVar()
        self.hostame = StringVar()
        self.protcolvar = StringVar()
        self.var = StringVar()
        if ctrlrDefaults:
            self.ctrlrValues = ctrlrDefaults

        tkSimpleDialog.Dialog.__init__(self, parent, title)

    # Funcion body, encargado de crear el cuerpo de la ventana de dialogo.
    def body(self, master):
        rowCount = 0

        self.hostame.set(self.ctrlrValues['hostname'])
        Label(master, text="Hostname:").grid(row=rowCount, sticky=W, padx=5, pady=5)
        Entry(master, state='disabled', textvariable=self.hostame).grid(row=rowCount, column=1, padx=5, pady=5)
        rowCount += 1

        self.port.set(self.ctrlrValues['remotePort'])
        Label(master, text="OpenFlow TCP Port:").grid(row=rowCount, sticky=W, padx=5, pady=5)
        Entry(master, state='disabled', textvariable=self.port).grid(row=rowCount, column=1, padx=5, pady=5)
        rowCount += 1

        self.mac.set(self.ctrlrValues['mac'])
        Label(master, text="Mac:").grid(row=rowCount, sticky=W, padx=5, pady=5)
        Entry(master, textvariable=self.mac).grid(row=rowCount, column=1, padx=5, pady=5)
        rowCount += 1

        self.ip.set(self.ctrlrValues['remoteIP'])
        Label(master, text="IP Address:").grid(row=rowCount, sticky=W, padx=5, pady=5)
        Entry(master, state='disabled', textvariable=self.ip).grid(row=rowCount, column=1, padx=5, pady=5)

    # Funcion apply, encargada de establecer los valores introducidos de los diferentes campos de la ventana de
    # dialogo.
    def apply(self):
        self.result = {'hostname': self.hostame.get(),
                       'remoteIP': self.ip.get(),
                       'remotePort': self.port.get(),
                       'mac': self.mac.get()}


# Clase ToolTip, encargada de mostrar texto en la ventana de información sobre herramientas.
class ToolTip(object):

    # Constructor parametrizado de la clase ToolTip.
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    # Funcion showtip, encargada de mostrar texto en la ventana de información sobre herramientas.
    def showtip(self, text):

        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:

            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")

        except TclError:
            pass
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    # Funcion hidetip, encargada de destruir la ventana.
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# Clase customize_topology, clase principal en la que podremos customizar una topologia completa de SDN, con Switches,
# hosts, controladores y los enlaces que unen dichos elementos de la red.
class customize_topology(Frame):

    # Constructor parametrizado de la clase customize_topology
    def __init__(self, parent=None, cheight=600, cwidth=1000):

        self.graph = nx.Graph()

        self.defaultIpBase = '10.0.0.0/8'

        self.nflowDefaults = {'nflowTarget': '',
                              'nflowTimeout': '600',
                              'nflowAddId': '0'}
        self.sflowDefaults = {'sflowTarget': '',
                              'sflowSampling': '400',
                              'sflowHeader': '128',
                              'sflowPolling': '30'}

        self.appPrefs = {
            "ipBase": self.defaultIpBase,
            "startCLI": "0",
            "terminalType": 'xterm',
            "switchType": 'ovs',
            "dpctl": '',
            'sflow': self.sflowDefaults,
            'netflow': self.nflowDefaults,
            'openFlowVersions': {'ovsOf10': '1',
                                 'ovsOf11': '0',
                                 'ovsOf12': '0',
                                 'ovsOf13': '0'}

        }

        Frame.__init__(self, parent)
        self.action = None
        self.appName = 'Topology Editor'
        self.fixedFont = tkFont.Font(family="DejaVu Sans Mono", size="14")

        # Establecemos el estilo:
        self.font = ('Geneva', 9)
        self.smallFont = ('Geneva', 7)
        self.bg = 'white'

        # Titulo de la ventana
        self.top = self.winfo_toplevel()
        self.top.title(self.appName)

        # Menu bar de la ventana
        self.createMenubar()

        self.cheight, self.cwidth = cheight, cwidth
        self.cframe, self.canvas = self.createCanvas()

        self.controllers = {}

        self.images = miniEditImages()
        self.buttons = {}
        self.active = None

        self.tools = ('Select', 'NetLink', 'Host', 'Switch', 'Controller')
        self.customColors = {'Switch': 'darkGreen', 'Host': 'blue'}
        self.toolbar = self.createToolbar()

        self.toolbar.grid(column=0, row=0, sticky='nsew')
        self.cframe.grid(column=1, row=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.pack(expand=True, fill='both')

        self.aboutBox = None

        self.nodeBindings = self.createNodeBindings()
        self.nodePrefixes = {'LegacyRouter': 'r', 'LegacySwitch': 's', 'Switch': 's', 'Host': 'h', 'Controller': 'c'}
        self.widgetToItem = {}
        self.itemToWidget = {}

        self.link = self.linkWidget = None

        self.selection = None

        self.bind('<Control-q>', lambda event: self.quit())
        self.bind('<KeyPress-Delete>', self.deleteSelection)
        self.bind('<KeyPress-BackSpace>', self.deleteSelection)
        self.focus()
        self.hostPopup = Menu(self.top, tearoff=0)
        self.hostPopup.add_command(label='Properties', font=self.font, command=self.hostDetails)
        self.switchPopup = Menu(self.top, tearoff=0)
        self.switchPopup.add_command(label='Properties', font=self.font, command=self.switchDetails)
        self.switchRunPopup = Menu(self.top, tearoff=0)
        self.switchRunPopup.add_command(label='Switch Options', font=self.font)
        self.switchRunPopup.add_separator()
        self.switchRunPopup.add_command(label='List bridge details', font=self.font, command=self.listBridge)
        self.linkPopup = Menu(self.top, tearoff=0)
        self.linkPopup.add_command(label='Properties', font=self.font, command=self.linkDetails)
        self.linkRunPopup = Menu(self.top, tearoff=0)
        self.controllerPopup = Menu(self.top, tearoff=0)
        self.controllerPopup.add_command(label='Properties', font=self.font, command=self.controllerDetails)

        self.linkx = self.linky = self.linkItem = None
        self.lastSelection = None

        self.links = {}
        self.hostOpts = {}
        self.switchOpts = {}
        self.hostCount = 0
        self.switchCount = 0
        self.controllerCount = 0
        self.net = None

        Wm.wm_protocol(self.top, name='WM_DELETE_WINDOW', func=self.master.destroy)

    # Funcion quit, encargada de destruit la ventana de esta herramienta y parar su ejecucion.
    def quit(self):

        self.stop()
        Frame.quit(self)

    # Funcion createMenubar, encargada de crear un menu bar en la parte superior de nuestra herramienta.
    def createMenubar(self):

        font = self.font
        mbar = Menu(self.top, font=font)
        self.top.configure(menu=mbar)

        fileMenu = Menu(mbar, tearoff=False)
        mbar.add_cascade(label="File", font=font, menu=fileMenu)
        fileMenu.add_command(label="New", font=font, command=self.newTopology)
        fileMenu.add_command(label="Open", font=font, command=self.loadTopology)
        fileMenu.add_command(label="Save", font=font, command=self.saveTopology)

    # Funcion createCanvas, que crear y devuelve nuestro marco de lienzo desplazable
    def createCanvas(self):

        f = Frame(self)
        canvas = Canvas(f, width=self.cwidth, height=self.cheight,
                        bg=self.bg)

        xbar = Scrollbar(f, orient='horizontal', command=canvas.xview)
        ybar = Scrollbar(f, orient='vertical', command=canvas.yview)
        canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)

        resize = Label(f, bg='white')

        canvas.grid(row=0, column=1, sticky='nsew')
        ybar.grid(row=0, column=2, sticky='ns')
        xbar.grid(row=1, column=1, sticky='ew')
        resize.grid(row=1, column=2, sticky='nsew')

        f.rowconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)
        f.grid(row=0, column=0, sticky='nsew')
        f.bind('<Configure>', lambda event: self.updateScrollRegion())

        canvas.bind('<ButtonPress-1>', self.clickCanvas)
        canvas.bind('<B1-Motion>', self.dragCanvas)
        canvas.bind('<ButtonRelease-1>', self.releaseCanvas)

        return f, canvas

    # Funcion updateScrollRegion, actualiza la región de desplazamiento del lienzo.
    def updateScrollRegion(self):

        bbox = self.canvas.bbox('all')
        if bbox is not None:
            self.canvas.configure(scrollregion=(0, 0, bbox[2],
                                                bbox[3]))

    # Funcion canvasx, que convierte la coordenada x de la raiz a la coordenada del lienzo.
    def canvasx(self, x_root):
        c = self.canvas
        return c.canvasx(x_root) - c.winfo_rootx()

    # Funcion canvasy. Convierte la coordenada y de la raíz a la coordenada del lienzo.
    def canvasy(self, y_root):
        c = self.canvas
        return c.canvasy(y_root) - c.winfo_rooty()

    # Funcion activate. Activa una herramienta y pulsa su boton.
    def activate(self, toolName):
        # Ajusta la apariencia del boton:
        if self.active:
            self.buttons[self.active].configure(relief='raised')
        self.buttons[toolName].configure(relief='sunken')
        # Activa los enlaces dinamicos:
        self.active = toolName

    @staticmethod
    def createToolTip(widget, text):
        toolTip = ToolTip(widget)

        def enter(_event):
            toolTip.showtip(text)

        def leave(_event):
            toolTip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def createToolbar(self):
        "Create and return our toolbar frame."

        toolbar = Frame(self)

        # Tools
        for tool in self.tools:
            cmd = (lambda t=tool: self.activate(t))
            b = Button(toolbar, text=tool, font=self.smallFont, command=cmd)
            if tool in self.images:
                b.config(height=90, image=self.images[tool])
                self.createToolTip(b, str(tool))
            b.pack(fill='x')
            self.buttons[tool] = b
        self.activate(self.tools[0])

        # Spacer
        Label(toolbar, text='').pack()

        return toolbar

    # Funcion addNode. Aniade un nuevo nodo a nuestro lienzo (canvas).
    def addNode(self, node, nodeNum, x, y, name=None):

        if node == 'Switch':
            self.switchCount += 1
        if node == 'Host':
            self.hostCount += 1
        if node == 'Controller':
            self.controllerCount += 1
        if name is None:
            name = self.nodePrefixes[node] + nodeNum

        self.addNamedNode(node, name, x, y)

    # Funcion addNamedNode. Aniade un nuevo nodo a nuestro lienzo.
    def addNamedNode(self, node, name, x, y):
        icon = self.nodeIcon(node, name)
        item = self.canvas.create_window(x, y, anchor='c', window=icon,
                                         tags=node)
        self.widgetToItem[icon] = item
        self.itemToWidget[item] = icon
        icon.links = {}

        self.graph.add_node(name)

    # Funcion loadTopology, encargada de cargar una topologia guardada previamente en un formato json
    def loadTopology(self):
        c = self.canvas
        f = tkFileDialog.askopenfile(title='Open Topology', initialdir='./Graphs', mode='rb',
                                     filetypes=(('Files .json', '*.json'), ('All Files', '*.*')))
        if f is None:
            return
        self.newTopology()
        loadedTopology = self.convertJsonUnicode(json.load(f))

        if 'controllers' in loadedTopology:

            controllers = loadedTopology['controllers']
            for controller in controllers:
                hostname = controller['opts']['hostname']
                x = controller['x']
                y = controller['y']
                self.addNode('Controller', 0, float(x), float(y), name=hostname)
                self.controllers[hostname] = controller['opts']
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_controllerPopup)

        hosts = loadedTopology['hosts']
        for host in hosts:
            nodeNum = host['number']
            hostname = 'h' + nodeNum
            if 'hostname' in host['opts']:
                hostname = host['opts']['hostname']
            else:
                host['opts']['hostname'] = hostname
            if 'nodeNum' not in host['opts']:
                host['opts']['nodeNum'] = int(nodeNum)
            x = host['x']
            y = host['y']
            self.addNode('Host', nodeNum, float(x), float(y), name=hostname)

            if 'privateDirectory' in host['opts']:
                newDirList = []
                for privateDir in host['opts']['privateDirectory']:
                    if isinstance(privateDir, list):
                        newDirList.append((privateDir[0], privateDir[1]))
                    else:
                        newDirList.append(privateDir)
                host['opts']['privateDirectory'] = newDirList
            self.hostOpts[hostname] = host['opts']
            icon = self.findWidgetByName(hostname)
            icon.bind('<Button-3>', self.do_hostPopup)

        switches = loadedTopology['switches']
        for switch in switches:
            nodeNum = switch['number']
            hostname = 's' + nodeNum
            if 'controllers' not in switch['opts']:
                switch['opts']['controllers'] = []
            if 'switchType' not in switch['opts']:
                switch['opts']['switchType'] = 'default'
            if 'hostname' in switch['opts']:
                hostname = switch['opts']['hostname']
            else:
                switch['opts']['hostname'] = hostname
            if 'nodeNum' not in switch['opts']:
                switch['opts']['nodeNum'] = int(nodeNum)
            x = switch['x']
            y = switch['y']
            if switch['opts']['switchType'] == "legacyRouter":
                self.addNode('LegacyRouter', nodeNum, float(x), float(y), name=hostname)
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_legacyRouterPopup)
            elif switch['opts']['switchType'] == "legacySwitch":
                self.addNode('LegacySwitch', nodeNum, float(x), float(y), name=hostname)
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_legacySwitchPopup)
            else:
                self.addNode('Switch', nodeNum, float(x), float(y), name=hostname)
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_switchPopup)
            self.switchOpts[hostname] = switch['opts']

            if True:
                controllers = self.switchOpts[hostname]['controllers']
                for controller in controllers:
                    dest = self.findWidgetByName(controller)
                    dx, dy = self.canvas.coords(self.widgetToItem[dest])
                    self.link = self.canvas.create_line(float(x),
                                                        float(y),
                                                        dx,
                                                        dy,
                                                        width=4,
                                                        fill='#95A5A6',
                                                        dash=(6, 4, 2, 4),
                                                        tag='link')
                    c.itemconfig(self.link, tags=c.gettags(self.link) + ('control',))
                    self.addLink(icon, dest, linktype='control')
                    self.createControlLinkBindings()
                    self.link = self.linkWidget = None

        links = loadedTopology['links']
        for link in links:
            srcNode = link['src']
            src = self.findWidgetByName(srcNode)
            sx, sy = self.canvas.coords(self.widgetToItem[src])

            destNode = link['dest']
            dest = self.findWidgetByName(destNode)
            dx, dy = self.canvas.coords(self.widgetToItem[dest])

            self.link = self.canvas.create_line(sx, sy, dx, dy, width=4,
                                                fill='purple', tag='link')
            c.itemconfig(self.link, tags=c.gettags(self.link) + ('data',))

            self.addLink(src, dest, linkopts=link['opts'])
            self.createDataLinkBindings()
            self.link = self.linkWidget = None

        f.close()

    # Funcion convertJsonUnicode, encargado de convertir un fichero en formato json a unicode.
    def convertJsonUnicode(self, text):
        if isinstance(text, dict):
            return {self.convertJsonUnicode(key): self.convertJsonUnicode(value) for key, value in text.items()}
        if isinstance(text, list):
            return [self.convertJsonUnicode(element) for element in text]
        return text

    # Funcion findWidgetByName, encargada de encontrar un widget por su nombre.
    def findWidgetByName(self, name):
        for widget in self.widgetToItem:
            if name == widget['text']:
                return widget
        return None

    # Funcion newTopology, encargada de eliminar todos los elementos de nuestra topologia.
    def newTopology(self):
        keys = list(self.widgetToItem.keys())
        for key in keys:
            self.deleteItem(self.widgetToItem[key])
        self.hostCount = 0
        self.switchCount = 0
        self.controllerCount = 0
        self.links = {}
        self.hostOpts = {}
        self.switchOpts = {}
        self.controllers = {}
        self.appPrefs["ipBase"] = self.defaultIpBase

    # Funcion is_correct_graph. Comprueba si el grafo cumple con los requisitos para considerarse una topografia
    # correcta.
    def is_correct_graph(self):
        if not nx.is_empty(self.graph):
            if nx.is_connected(self.graph) and self.graph.number_of_nodes() >= 4:

                # Vemos el numero de controladores en el grafo (no puede ser mas de uno)
                list_controllers = [controller for controller in list(self.graph.nodes()) if (controller[0] == 'c')]
                list_switchs = [switch for switch in list(self.graph.nodes()) if (switch[0] == 's')]
                list_hosts = [host for host in list(self.graph.nodes()) if (host[0] == 'h')]
                if len(list_controllers) == 1 and len(list_switchs) >= 1 and len(list_hosts) >= 2:
                    for switch in list_switchs:
                        if switch not in self.graph.neighbors(list_controllers[0]):
                            return False

                    for host in list_hosts:
                        if not ('mac' in self.hostOpts[host] and 'ip' in self.hostOpts[host] and 'port' in
                                self.hostOpts[host]):
                            return False
                        for host_2 in list_hosts:
                            if (host_2 != host) and (
                                    self.hostOpts[host]['ip'] == self.hostOpts[host_2]['ip'] or self.hostOpts[host][
                                'mac'] == self.hostOpts[host_2]['mac']):
                                return False
                    list_nodes_without_controller = list_hosts + list_switchs

                    if nx.is_connected(self.graph.subgraph(list_nodes_without_controller)) and nx.is_connected(
                            self.graph.subgraph(list_switchs)):
                        return True

        return False

    # Funcion saveTopology, encargada de guardar la topologia, haciendo llamada a otras funciones como is_correct_graph
    # para verificar que el grafo a guardar forma una topologia que cumple con unos requisitos minimos.
    def saveTopology(self):

        if self.is_correct_graph():
            savingDictionary = {}
            fileName = tkFileDialog.asksaveasfilename(title='Save the topology as...', initialdir='./Graphs',
                                                      filetypes=(('Files .json', '*.json'), ('All Files', '*.*')))

            if len(fileName) > 0:
                # Save Switches and Hosts
                hostsToSave = []
                switchesToSave = []
                controllersToSave = []
                for widget in self.widgetToItem:
                    name = widget['text']
                    tags = self.canvas.gettags(self.widgetToItem[widget])
                    x1, y1 = self.canvas.coords(self.widgetToItem[widget])

                    if 'Switch' in tags:
                        nodeNum = self.switchOpts[name]['nodeNum']
                        nodeToSave = {'number': str(nodeNum),
                                      'x': str(x1),
                                      'y': str(y1),
                                      'opts': self.switchOpts[name]}
                        switchesToSave.append(nodeToSave)
                    elif 'Host' in tags:
                        nodeNum = self.hostOpts[name]['nodeNum']
                        nodeToSave = {'number': str(nodeNum),
                                      'x': str(x1),
                                      'y': str(y1),
                                      'opts': self.hostOpts[name]}
                        hostsToSave.append(nodeToSave)
                    elif 'Controller' in tags:
                        nodeToSave = {'x': str(x1),
                                      'y': str(y1),
                                      'opts': self.controllers[name]}
                        controllersToSave.append(nodeToSave)
                    else:
                        raise Exception("Cannot create mystery node: " + name)

                savingDictionary['hosts'] = hostsToSave
                savingDictionary['switches'] = switchesToSave
                savingDictionary['controllers'] = controllersToSave

                # Save Links
                linksToSave = []
                for link in self.links.values():
                    src = link['src']
                    dst = link['dest']
                    linkopts = link['opts']

                    srcName, dstName = src['text'], dst['text']
                    linkToSave = {'src': srcName,
                                  'dest': dstName,
                                  'opts': linkopts}

                    if link['type'] == 'data':
                        linksToSave.append(linkToSave)
                savingDictionary['links'] = linksToSave

                try:

                    f = open(fileName, 'w')
                    f.write(json.dumps(savingDictionary, sort_keys=True, indent=4, separators=(',', ': ')))

                except Exception as er:
                    print(er)

                finally:
                    f.close()

                f.close()
        else:
            message = 'One or more of the requirements to save the created topology is not met.'
            help_message = 'Minimum requirements: \n\n' \
                           '  o   Controllers = 1 \n' \
                           '  o   Switches >= 1 \n' \
                           '  o   Hosts >= 2 \n' \
                           '  o   The controller must be connected to all switches.\n' \
                           '  o   Switches and hosts must form a connected graph.\n' \
                           '  o   Switches must form a connected graph.\n' \
                           '  o   All hosts must have assigned IP address, MAC and port'
            messagebox.showerror("Error", message + '\n\n' + help_message)

    # Funcion canvasHandle, Manejador de eventos genéricos del lienzo (canvas).
    def canvasHandle(self, eventName, event):
        if self.active is None:
            return
        toolName = self.active
        handler = getattr(self, eventName + toolName, None)
        if handler is not None:
            handler(event)

    # Funcion clickCanvas, Controlador de clics en el lienzo.
    def clickCanvas(self, event):
        self.canvasHandle('click', event)

    # Funcion dragCanvas. Manejador de arrastre del lienzo.
    def dragCanvas(self, event):
        self.canvasHandle('drag', event)

    # Funcion releaseCanvas. Manejador de ratón de lienzo hacia arriba.
    def releaseCanvas(self, event):
        self.canvasHandle('release', event)

    # Funcion findItem, para encontrar items en un lugar de nuestro lienzo.
    def findItem(self, x, y):
        items = self.canvas.find_overlapping(x, y, x, y)
        if len(items) == 0:
            return None
        else:
            return items[0]

    # Funcion clickSelect, encargada de seleccionar un item.
    def clickSelect(self, event):
        self.selectItem(self.findItem(event.x, event.y))

    # Funcion deleteItem, encargada de eliminar un item.
    def deleteItem(self, item):
        if self.buttons['Select']['state'] == 'disabledd':
            return

        if item in self.links:
            self.deleteLink(item)
        if item in self.itemToWidget:
            self.deleteNode(item)

        self.canvas.delete(item)

    # Funcion deleteSelection. Elimina el elemento seleccionado.
    def deleteSelection(self, _event):
        if self.selection is not None:
            self.deleteItem(self.selection)
        self.selectItem(None)

    # Funcion nodeIcon, que crea un nuevo icono de nodo.
    def nodeIcon(self, node, name):
        icon = Button(self.canvas, image=self.images[node],
                      text=name, compound='top')
        bindtags = [str(self.nodeBindings)]
        bindtags += list(icon.bindtags())
        icon.bindtags(tuple(bindtags))
        return icon

    # Funcion newNode, encargada de aniadir un nuevo nodo a nuestro lienzo (canvas)
    def newNode(self, node, event):
        c = self.canvas
        x, y = c.canvasx(event.x), c.canvasy(event.y)
        name = self.nodePrefixes[node]
        if node == 'Switch':
            self.switchCount += 1
            name = self.nodePrefixes[node] + str(self.switchCount)
            self.switchOpts[name] = {}
            self.switchOpts[name]['nodeNum'] = self.switchCount
            self.switchOpts[name]['hostname'] = name
            self.switchOpts[name]['switchType'] = 'default'
            self.switchOpts[name]['controllers'] = []

        if node == 'Host':
            self.hostCount += 1
            name = self.nodePrefixes[node] + str(self.hostCount)
            self.hostOpts[name] = {'sched': 'host'}
            self.hostOpts[name]['nodeNum'] = self.hostCount
            self.hostOpts[name]['hostname'] = name
        if node == 'Controller':
            name = self.nodePrefixes[node] + str(self.controllerCount)
            ctrlr = {'controllerType': 'ref',
                     'hostname': name,
                     'controllerProtocol': 'tcp',
                     'remoteIP': '127.0.0.1',
                     'remotePort': 6633,
                     'mac': ''}
            self.controllers[name] = ctrlr
            self.controllerCount += 1

        self.graph.add_node(name)

        icon = self.nodeIcon(node, name)
        item = self.canvas.create_window(x, y, anchor='c', window=icon,
                                         tags=node)
        self.widgetToItem[icon] = item
        self.itemToWidget[item] = icon
        self.selectItem(item)
        icon.links = {}
        if node == 'Switch':
            icon.bind('<Button-3>', self.do_switchPopup)

        if node == 'Host':
            icon.bind('<Button-3>', self.do_hostPopup)
        if node == 'Controller':
            icon.bind('<Button-3>', self.do_controllerPopup)

    # Funcion clickController, encargada de aniadir un nuevo Controlador a nuestro lienzo.
    def clickController(self, event):
        self.newNode('Controller', event)

    # Funcion clickHost, aniade un nuevo host a nuestro lienzo.
    def clickHost(self, event):
        self.newNode('Host', event)

    # Funcion clickSwitch, aniade un nuevo Switch a nuestro lienzo
    def clickSwitch(self, event):
        self.newNode('Switch', event)

    # Funcion dragNetLink, encargado de arrastrar el punto final de un enlace a otro nodo.
    def dragNetLink(self, event):
        if self.link is None:
            return
        # Como el arrastre comienza en el widget, utilizamos las coordenadas de la raiz
        x = self.canvasx(event.x_root)
        y = self.canvasy(event.y_root)
        c = self.canvas
        c.coords(self.link, self.linkx, self.linky, x, y)

    # Funcion releaseNetLink, encargada de abandonar el enlace actual.
    def releaseNetLink(self, _event):
        if self.link is not None:
            self.canvas.delete(self.link)
        self.linkWidget = self.linkItem = self.link = None

    # Funcion createNodeBindings, encargada de crear un conjunto de enlaces para los nodos.
    def createNodeBindings(self):
        bindings = {
            '<ButtonPress-1>': self.clickNode,
            '<B1-Motion>': self.dragNode,
            '<ButtonRelease-1>': self.releaseNode,
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

    # Funcion leaveNode, encargada de restaurar la antigua seleccion al salir.
    def leaveNode(self, _event):
        self.selectItem(self.lastSelection)

    # Funcion clickNode, encargado de manejar los clics de los nodos.
    def clickNode(self, event):
        if self.active == 'NetLink':
            self.startLink(event)
        else:
            self.selectNode(event)
        return 'break'

    # Funcion dragNode, encargada de manejar el arrastre de los nodos por el lienzo.
    def dragNode(self, event):
        if self.active == 'NetLink':
            self.dragNetLink(event)
        else:
            self.dragNodeAround(event)

    # Funcion releaseNode, encargado de manejar las liberacion de nodos.
    def releaseNode(self, event):
        if self.active == 'NetLink':
            self.finishLink(event)

    # Funcion selectNode, encargado de seleccionar el nodo sobre el que se ha hecho clic.
    def selectNode(self, event):
        "Select the node that was clicked on."
        item = self.widgetToItem.get(event.widget, None)
        self.selectItem(item)

    # Funcion dragNodeAround, encargada de arrastrar un nodo en el lienzo.
    def dragNodeAround(self, event):
        c = self.canvas
        # Convierte las coordenadas globales en locales; necesario ya que x, y son relativas al widget.
        x = self.canvasx(event.x_root)
        y = self.canvasy(event.y_root)
        w = event.widget
        # Ajustamos la posicion del nodo
        item = self.widgetToItem[w]
        c.coords(item, x, y)
        # Ajustamos las posiciones de los enlaces
        for dest in w.links:
            link = w.links[dest]
            item = self.widgetToItem[dest]
            x1, y1 = c.coords(item)
            c.coords(link, x, y, x1, y1)
        self.updateScrollRegion()

    # Funcion , encargada de crear un conjunto de enlaces para los nodos.
    def createControlLinkBindings(self):

        def select(_event, link=self.link):
            "Seleccionar el elemento en la entrada del raton"
            self.selectItem(link)

        def highlight(_event, link=self.link):
            "Resaltar el elemento en la entrada del raton."
            self.selectItem(link)
            self.canvas.itemconfig(link, fill='#29D3A7')

        def unhighlight(_event, link=self.link):
            "Destacar el elemento al salir del raton."
            self.canvas.itemconfig(link, fill='#95A5A6')

        self.canvas.tag_bind(self.link, '<Enter>', highlight)
        self.canvas.tag_bind(self.link, '<Leave>', unhighlight)
        self.canvas.tag_bind(self.link, '<ButtonPress-1>', select)

    # Funcion createDataLinkBindings, encargado de crear un conjunto de enlaces para los nodos.
    def createDataLinkBindings(self):

        def select(_event, link=self.link):
            self.selectItem(link)
            self.canvas.itemconfig(link, fill='purple')

        def highlight(_event, link=self.link):
            self.selectItem(link)
            self.canvas.itemconfig(link, fill='#29D3A7')

        def unhighlight(_event, link=self.link):
            self.canvas.itemconfig(link, fill='purple')

        self.canvas.tag_bind(self.link, '<Enter>', highlight)
        self.canvas.tag_bind(self.link, '<Leave>', unhighlight)
        self.canvas.tag_bind(self.link, '<ButtonPress-1>', select)
        self.canvas.tag_bind(self.link, '<Button-3>', self.do_linkPopup)

    # Funcion startLink, encargada de iniciar un nuevo enlace.
    def startLink(self, event):
        if event.widget not in self.widgetToItem:
            # No ha hecho clic en un nodo:
            return

        w = event.widget
        item = self.widgetToItem[w]
        x, y = self.canvas.coords(item)
        self.link = self.canvas.create_line(x, y, x, y, width=4,
                                            fill='purple', tag='link')
        self.linkx, self.linky = x, y
        self.linkWidget = w
        self.linkItem = item

    # Funcion finishLink, encargada de terminar de crear un enlace
    def finishLink(self, event):

        if self.link is None:
            return
        source = self.linkWidget

        c = self.canvas
        # Como hemos arrastrado desde el widget, utiliza las coordenadas raiz
        x, y = self.canvasx(event.x_root), self.canvasy(event.y_root)
        target = self.findItem(x, y)
        dest = self.itemToWidget.get(target, None)

        if (source is None or dest is None or source == dest
                or dest in source.links or source in dest.links):
            self.releaseNetLink(event)
            return
        # Por ahora, no permita que los hosts se vinculen directamente
        stags = self.canvas.gettags(self.widgetToItem[source])
        dtags = self.canvas.gettags(target)

        if (('Host' in stags and 'Host' in dtags) or
                ('Controller' in dtags and 'LegacyRouter' in stags) or
                ('Controller' in stags and 'LegacyRouter' in dtags) or
                ('Controller' in dtags and 'LegacySwitch' in stags) or
                ('Controller' in stags and 'LegacySwitch' in dtags) or
                ('Controller' in dtags and 'Host' in stags) or
                ('Controller' in stags and 'Host' in dtags) or
                ('Controller' in stags and 'Controller' in dtags)):
            self.releaseNetLink(event)
            return

        # Establecemos el tipo de enlace
        linkType = 'data'
        if 'Controller' in stags or 'Controller' in dtags:
            linkType = 'control'
            c.itemconfig(self.link, dash=(6, 4, 2, 4), fill='#95A5A6')
            self.createControlLinkBindings()
        else:
            linkType = 'data'
            self.createDataLinkBindings()
        c.itemconfig(self.link, tags=c.gettags(self.link) + (linkType,))

        x, y = c.coords(target)
        c.coords(self.link, self.linkx, self.linky, x, y)
        self.addLink(source, dest, linktype=linkType)
        if linkType == 'control':
            controllerName = ''
            switchName = ''
            if 'Controller' in stags:
                controllerName = source['text']
                switchName = dest['text']
            else:
                controllerName = dest['text']
                switchName = source['text']

            self.switchOpts[switchName]['controllers'].append(controllerName)

        self.link = self.linkWidget = None

    # Funcion hostDetails, encagada de almacenar los parametros introducidos en la ventana de dialogo de un host,
    # realizando las comprobaciones correspondientes a cada uno de los campos.
    def hostDetails(self, _ignore=None):

        if (self.selection is None or
                self.net is not None or
                self.selection not in self.itemToWidget):
            return
        widget = self.itemToWidget[self.selection]
        name = widget['text']
        tags = self.canvas.gettags(self.selection)
        if 'Host' not in tags:
            return

        prefDefaults = self.hostOpts[name]
        hostBox = HostDialog(self, title='Host Details', prefDefaults=prefDefaults)
        self.master.wait_window(hostBox.top)
        correct = True
        utilities = Utilities.Utilities()
        parameter = ''

        if hostBox.result:
            newHostOpts = {'nodeNum': self.hostOpts[name]['nodeNum']}

            if len(hostBox.result['hostname']) > 0:
                newHostOpts['hostname'] = hostBox.result['hostname']
                name = hostBox.result['hostname']
                widget['text'] = name
            if len(hostBox.result['mac']) > 0 and utilities.mac_address_check(hostBox.result['mac']):
                newHostOpts['mac'] = hostBox.result['mac']
            else:
                correct = False
                parameter = '( MAC address )'
            if len(hostBox.result['ip']) > 0 and utilities.ip_address_check(hostBox.result['ip']):
                newHostOpts['ip'] = hostBox.result['ip']
            else:
                correct = False
                parameter += '( IP address )'
            if len(hostBox.result['port']) > 0 and utilities.port_check(hostBox.result['port']):
                newHostOpts['port'] = hostBox.result['port']
            else:
                parameter += '( Port )'
                correct = False

            if not correct:
                if len(parameter.split(' ')) > 0:
                    message = 'Error, invalid parameters [ ' + parameter + ' ]. Values will not be saved.'
                else:
                    message = 'Error, invalid parameter [ ' + parameter + ' ]. The value will not be saved'
                messagebox.showerror("Error", message + '\n\n' + 'Help:\n\n' + message_help)
            else:
                self.hostOpts[name] = newHostOpts

    # Funcion switchDetails, encagada de almacenar los parametros introducidos en la ventana de dialogo de un Switch,
    # realizando las comprobaciones correspondientes a cada uno de los campos.
    def switchDetails(self, _ignore=None):
        if (self.selection is None or
                self.selection not in self.itemToWidget):
            return
        widget = self.itemToWidget[self.selection]
        name = widget['text']
        tags = self.canvas.gettags(self.selection)
        if 'Switch' not in tags:
            return

        prefDefaults = self.switchOpts[name]
        switchBox = SwitchDialog(self, title='Switch Details', prefDefaults=prefDefaults)
        self.master.wait_window(switchBox.top)
        if switchBox.result:
            newSwitchOpts = {'nodeNum': self.switchOpts[name]['nodeNum'],
                             'controllers': self.switchOpts[name]['controllers']}
            utilities = Utilities.Utilities()
            parameter = ''
            correct = True

            if len(switchBox.result['hostname']) > 0:
                newSwitchOpts['hostname'] = switchBox.result['hostname']
                name = switchBox.result['hostname']
                widget['text'] = name

            if len(switchBox.result['mac']) > 0 and utilities.mac_address_check(switchBox.result['mac']):
                newSwitchOpts['mac'] = switchBox.result['mac']
            else:
                correct = False
                parameter = '( MAC address )'

            if len(switchBox.result['ip']) > 0 and utilities.ip_address_check(switchBox.result['ip']):
                newSwitchOpts['ip'] = switchBox.result['ip']
            else:
                correct = False
                parameter += '( IP address )'

            if not correct:
                if len(parameter.split(' ')) > 0:
                    message = 'Error, invalid parameters [ ' + parameter + ' ]. Values will not be saved.'
                else:
                    message = 'Error, invalid parameter [ ' + parameter + ' ]. The value will not be saved'
                messagebox.showerror("Error", message + '\n\n' + 'Help:\n\n' + message_help)
            else:
                self.switchOpts[name] = newSwitchOpts

    # Funcion linkDetails, encagada de almacenar los parametros introducidos en la ventana de dialogo de un enlace,
    # realizando las comprobaciones correspondientes a cada uno de los campos.
    def linkDetails(self, _ignore=None):
        parameter = ''
        correct = True
        if (self.selection is None or
                self.net is not None):
            return
        link = self.selection

        linkDetail = self.links[link]

        linkopts = linkDetail['opts']
        linkBox = LinkDialog(self, title='Link Details', linkDefaults=linkopts)
        if linkBox.result is not None:
            utilities = Utilities.Utilities()
            if len(linkBox.result['bw']) > 0 and utilities.is_number_positive(linkBox.result['bw']):
                linkDetail['opts']['bw'] = linkBox.result['bw']
            else:
                correct = False
                parameter = '( Bandwidth )'
            if len(linkBox.result['distance']) > 0 and utilities.is_number_positive(linkBox.result['distance']):
                linkDetail['opts']['distance'] = linkBox.result['distance']
            else:
                correct = False
                parameter += '( Distance )'
            if len(linkBox.result['propagation_speed']) > 0 and utilities.is_number_positive(
                    linkBox.result['propagation_speed']):
                linkDetail['opts']['propagation_speed'] = linkBox.result['propagation_speed']
            else:
                correct = False
                parameter += '( Propagation Speed )'

            if not correct:
                if len(parameter.split(' ')) > 1:
                    message = 'Error, invalid parameters [ ' + parameter + ' ]. Values will not be saved.'
                else:
                    message = 'Error, invalid parameter [' + parameter + ']. The value will not be saved.'
                messagebox.showerror("Error", message + '\n\n' + 'Help:\n\n' + message_help_2)

    # Funcion controllerDetails, encagada de almacenar los parametros introducidos en la ventana de dialogo de un
    # controlador, realizando las comprobaciones correspondientes a cada uno de los campos.
    def controllerDetails(self, _ignore=None):
        if (self.selection is None or
                self.net is not None or
                self.selection not in self.itemToWidget):
            return
        widget = self.itemToWidget[self.selection]
        name = widget['text']
        tags = self.canvas.gettags(self.selection)
        oldName = name
        if 'Controller' not in tags:
            return

        ctrlrBox = ControllerDialog(self, title='Controller Details', ctrlrDefaults=self.controllers[name])
        if ctrlrBox.result:
            utilities = Utilities.Utilities()
            parameter = ''
            correct = True

            if len(ctrlrBox.result['hostname']) > 0:
                self.controllers['hostname'] = ctrlrBox.result['hostname']
                name = ctrlrBox.result['hostname']
                widget['text'] = name
            if len(ctrlrBox.result['mac']) > 0 and utilities.mac_address_check(ctrlrBox.result['mac']):
                self.controllers['mac'] = ctrlrBox.result['mac']
            else:
                correct = False
                parameter = '( MAC address )'
            if len(ctrlrBox.result['remoteIP']) > 0 and utilities.ip_address_check(ctrlrBox.result['remoteIP']):
                self.controllers['remoteIP'] = ctrlrBox.result['remoteIP']
            else:
                correct = False
                parameter += '( IP address )'
            if len(ctrlrBox.result['remotePort']) > 0 and utilities.port_check(ctrlrBox.result['remotePort']):
                self.controllers['remotePort'] = ctrlrBox.result['remotePort']
            else:
                parameter += '{Port}'
                correct = False

            if not correct:
                if len(parameter.split(' ')) > 1:
                    message = 'Error, invalid parameters (' + parameter + '). Values will not be saved.'
                else:
                    message = 'Error, invalid parameter (' + parameter + '). The value will not be saved.'
                messagebox.showerror("Error", message + '\n\n' + 'Help:\n\n' + message_help)
            else:
                self.controllers[name] = ctrlrBox.result

                # Buscamos referencias al controlador y cambiamos el nombre
                if oldName != name:
                    for widget in self.widgetToItem:
                        switchName = widget['text']
                        tags = self.canvas.gettags(self.widgetToItem[widget])
                        if 'Switch' in tags:
                            switch = self.switchOpts[switchName]
                            if oldName in switch['controllers']:
                                switch['controllers'].remove(oldName)
                                switch['controllers'].append(name)

    def listBridge(self, _ignore=None):
        if (self.selection is None or
                self.net is None or
                self.selection not in self.itemToWidget):
            return
        name = self.itemToWidget[self.selection]['text']
        tags = self.canvas.gettags(self.selection)

        if name not in self.net.nameToNode:
            return

    # Funcion addLink, encargada de aniadir un enlace al modelo.
    def addLink(self, source, dest, linktype='data', linkopts=None):
        if linkopts is None:
            linkopts = {'bw': 1000,
                        'distance': 1,
                        'propagation_speed': 240000000}
        source.links[dest] = self.link
        dest.links[source] = self.link
        self.links[self.link] = {'type': linktype,
                                 'src': source,
                                 'dest': dest,
                                 'opts': linkopts}

        self.graph.add_edge(source['text'], dest['text'])

    # Funcion deleteLink, encargado de eliminar el enlace del modelo.
    def deleteLink(self, link):
        pair = self.links.get(link, None)
        if pair is not None:
            source = pair['src']
            dest = pair['dest']
            del source.links[dest]
            del dest.links[source]

            if self.graph.has_edge(source['text'], dest['text']):
                self.graph.remove_edge(source['text'], dest['text'])

            stags = self.canvas.gettags(self.widgetToItem[source])
            ltags = self.canvas.gettags(link)

            if 'control' in ltags:
                controllerName = ''
                switchName = ''
                if 'Controller' in stags:
                    controllerName = source['text']
                    switchName = dest['text']
                else:
                    controllerName = dest['text']
                    switchName = source['text']

                if controllerName in self.switchOpts[switchName]['controllers']:
                    self.switchOpts[switchName]['controllers'].remove(controllerName)

        if link is not None:
            del self.links[link]

    # Fucnion deleteNode, encargada de eliminar el nodo (y sus enlaces) del modelo.
    def deleteNode(self, item):

        widget = self.itemToWidget[item]
        tags = self.canvas.gettags(item)
        if 'Controller' in tags:
            # Eliminamos de las listas de controladores de los switch
            for searchwidget in self.widgetToItem:
                name = searchwidget['text']
                tags = self.canvas.gettags(self.widgetToItem[searchwidget])
                if 'Switch' in tags:
                    if widget['text'] in self.switchOpts[name]['controllers']:
                        self.switchOpts[name]['controllers'].remove(widget['text'])

        self.graph.remove_node(widget['text'])

        for link in tuple(widget.links.values()):
            # Borramos de la vista y del modelo
            self.deleteItem(link)

        del self.itemToWidget[item]
        del self.widgetToItem[widget]

    # Funcion buildNodes, encargada de crear los nodos.
    def buildNodes(self, net):

        for widget in self.widgetToItem:
            name = widget['text']
            tags = self.canvas.gettags(self.widgetToItem[widget])

            if 'Switch' in tags:
                opts = self.switchOpts[name]

    @staticmethod
    def pathCheck(*args, **kwargs):
        moduleName = kwargs.get('moduleName', 'it')

    # Funcion buildLinks, encargada de crear los enlaces.
    def buildLinks(self, net):
        # Make links
        for key, link in self.links.items():
            tags = self.canvas.gettags(key)
            if 'data' in tags:
                src = link['src']
                dst = link['dest']
                linkopts = link['opts']
                srcName, dstName = src['text'], dst['text']
                srcNode, dstNode = net.nameToNode[srcName], net.nameToNode[dstName]

    def postStartSetup(self):

        # Configuramos los detalles del host
        for widget in self.widgetToItem:
            name = widget['text']
            tags = self.canvas.gettags(self.widgetToItem[widget])
            if 'Host' in tags:
                newHost = self.net.get(name)
                opts = self.hostOpts[name]
                if 'vlanInterfaces' in opts:
                    for vlanInterface in opts['vlanInterfaces']:
                        newHost.cmdPrint('ifconfig ' + name + '-eth0.' + vlanInterface[1] + ' ' + vlanInterface[0])
                if 'startCommand' in opts:
                    newHost.cmdPrint(opts['startCommand'])
            if 'Switch' in tags:
                newNode = self.net.get(name)
                opts = self.switchOpts[name]
                if 'startCommand' in opts:
                    newNode.cmdPrint(opts['startCommand'])

        # Configuramos NetFlow
        nflowValues = self.appPrefs['netflow']
        if len(nflowValues['nflowTarget']) > 0:
            nflowEnabled = False
            nflowSwitches = ''
            for widget in self.widgetToItem:
                name = widget['text']
                tags = self.canvas.gettags(self.widgetToItem[widget])

                if 'Switch' in tags:
                    opts = self.switchOpts[name]
                    if 'netflow' in opts:
                        if opts['netflow'] == '1':
                            nflowSwitches = nflowSwitches + ' -- set Bridge ' + name + ' netflow=@MiniEditNF'
                            nflowEnabled = True
            if nflowEnabled:
                nflowCmd = 'ovs-vsctl -- --id=@MiniEditNF create NetFlow ' + 'target=\\\"' + nflowValues[
                    'nflowTarget'] + '\\\" ' + 'active-timeout=' + nflowValues['nflowTimeout']
                if nflowValues['nflowAddId'] == '1':
                    nflowCmd = nflowCmd + ' add_id_to_interface=true'
                else:
                    nflowCmd = nflowCmd + ' add_id_to_interface=false'
                call(nflowCmd + nflowSwitches, shell=True)

        sflowValues = self.appPrefs['sflow']
        if len(sflowValues['sflowTarget']) > 0:
            sflowEnabled = False
            sflowSwitches = ''
            for widget in self.widgetToItem:
                name = widget['text']
                tags = self.canvas.gettags(self.widgetToItem[widget])

                if 'Switch' in tags:
                    opts = self.switchOpts[name]
                    if 'sflow' in opts:
                        if opts['sflow'] == '1':
                            sflowSwitches = sflowSwitches + ' -- set Bridge ' + name + ' sflow=@MiniEditSF'
                            sflowEnabled = True
            if sflowEnabled:
                sflowCmd = 'ovs-vsctl -- --id=@MiniEditSF create sFlow ' + 'target=\\\"' + sflowValues[
                    'sflowTarget'] + '\\\" ' + 'header=' + sflowValues['sflowHeader'] + ' ' + 'sampling=' + sflowValues[
                               'sflowSampling'] + ' ' + 'polling=' + sflowValues['sflowPolling']
                call(sflowCmd + sflowSwitches, shell=True)

    # Funcion do_linkPopup, encargada de mostrar el menu emergente de un enlace.
    def do_linkPopup(self, event):
        if self.net is None:
            try:
                self.linkPopup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.linkPopup.grab_release()
        else:
            try:
                self.linkRunPopup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.linkRunPopup.grab_release()

    # Funcion do_controllerPopup, encargada de mostrar el menu emergente de un controlador.
    def do_controllerPopup(self, event):
        if self.net is None:
            try:
                self.controllerPopup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.controllerPopup.grab_release()

    # Funcion do_hostPopup, encargada de mostrar el menu emergente de un host.
    def do_hostPopup(self, event):
        if self.net is None:
            try:
                self.hostPopup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.hostPopup.grab_release()
        else:
            try:
                self.hostRunPopup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.hostRunPopup.grab_release()

    # Funcion do_switchPopup, encargada de mostrar el menu emergente de un switch.
    def do_switchPopup(self, event):
        if self.net is None:
            try:
                self.switchPopup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.switchPopup.grab_release()
        else:
            try:
                self.switchRunPopup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.switchRunPopup.grab_release()

    # Funcion setCustom, encargada de establecer parametros personalizados para la ejecucion.
    def setCustom(self, name, value):
        if name in ('topos', 'switches', 'hosts', 'controllers'):
            param = name.upper()
            globals()[param].update(value)
        elif name == 'validate':
            self.validate = value
        else:
            globals()[name] = value

    # Funcion parseCustomFile, para analizar el archivo personalizado y añade los parametros antes de analizar las
    # opciones de la linea de comandos.
    def parseCustomFile(self, fileName):
        customs = {}
        if os.path.isfile(fileName):
            with open(fileName, 'r') as f:
                exec(f.read())
            for name, val in customs.items():
                self.setCustom(name, val)
        else:
            raise Exception('could not find custom file: %s' % fileName)


# Funcion miniEditImages, encargada de crear y devolver imagenes de los diferentes dispositivos de la topologia
# (switches, hosts y controladores).
def miniEditImages():
    return {
        'Select': BitmapImage(
            file='Arch\left_ptr'),
        'Switch': PhotoImage(
            data=r"""iVBORw0KGgoAAAANSUhEUgAAAG4AAAA1CAYAAACgEt7PAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAStdEVYdG14ZmlsZQAlM0NteGZpbGUlMjBob3N0JTNEJTIyRWxlY3Ryb24lMjIlMjBtb2RpZmllZCUzRCUyMjIwMjEtMDMtMDlUMjAlM0E1MSUzQTE0LjgzNFolMjIlMjBhZ2VudCUzRCUyMjUuMCUyMChXaW5kb3dzJTIwTlQlMjAxMC4wJTNCJTIwV2luNjQlM0IlMjB4NjQpJTIwQXBwbGVXZWJLaXQlMkY1MzcuMzYlMjAoS0hUTUwlMkMlMjBsaWtlJTIwR2Vja28pJTIwZHJhdy5pbyUyRjE0LjEuOCUyMENocm9tZSUyRjg3LjAuNDI4MC44OCUyMEVsZWN0cm9uJTJGMTEuMS4xJTIwU2FmYXJpJTJGNTM3LjM2JTIyJTIwZXRhZyUzRCUyMlJsMGxZekhIU2dsdUhLYVIycWloJTIyJTIwdmVyc2lvbiUzRCUyMjE0LjEuOCUyMiUyMHR5cGUlM0QlMjJkZXZpY2UlMjIlM0UlM0NkaWFncmFtJTIwaWQlM0QlMjJZTVYwbmpDMEw0VzRkdDFodDh1eSUyMiUyMG5hbWUlM0QlMjJQJUMzJUExZ2luYS0xJTIyJTNFeFZUQmpwc3dFUDBhamtXQVE1TWNHN0xwcW1wWGxkS3F4NVVERG96V1pxanRKS1JmM3pFWUVvUlcyejJWZzdIZnpOZ3o4NTRkc0V5MW56VnZxbTlZQ0Jra1VkRUdiQnNreVhLeHB0RUIxeDVJVjZ3SFNnMUZEOFUzWUE5JTJGaEFjamo1NmdFR2JpYUJHbGhXWUs1bGpYSXJjVGpHdU5sNm5iRWVYMDFJYVhZZ2JzY3k3bjZDOG9iTldqcTJSNXd4OEZsTlZ3Y3Z6UkY2ejQ0T3dyTVJVdjhISUhzWWVBWlJyUjlqUFZaa0s2M2cxOTZlTjJyMWpIeExTbzdiOEVzTU1YRXgwdnpZJTJGajB5TmVuJTJCS2Y3ZTczQjclMkZMbWN1VEw5Z25hNjlEQnhxRTJuWmRURGRCdWczWWhwdW1iJTJGVVJXa0c3YnlxckpDMWpaNU5RMWpUUEtTdWhDUmpMam1oUmNGTzVp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"""),
        'Controller': PhotoImage(
            data=r"""iVBORw0KGgoAAAANSUhEUgAAAG8AAABbCAYAAAB9LtvbAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAStdEVYdG14ZmlsZQAlM0NteGZpbGUlMjBob3N0JTNEJTIyRWxlY3Ryb24lMjIlMjBtb2RpZmllZCUzRCUyMjIwMjEtMDMtMDlUMjAlM0E1MSUzQTE0LjgzNFolMjIlMjBhZ2VudCUzRCUyMjUuMCUyMChXaW5kb3dzJTIwTlQlMjAxMC4wJTNCJTIwV2luNjQlM0IlMjB4NjQpJTIwQXBwbGVXZWJLaXQlMkY1MzcuMzYlMjAoS0hUTUwlMkMlMjBsaWtlJTIwR2Vja28pJTIwZHJhdy5pbyUyRjE0LjEuOCUyMENocm9tZSUyRjg3LjAuNDI4MC44OCUyMEVsZWN0cm9uJTJGMTEuMS4xJTIwU2FmYXJpJTJGNTM3LjM2JTIyJTIwZXRhZyUzRCUyMlJsMGxZekhIU2dsdUhLYVIycWloJTIyJTIwdmVyc2lvbiUzRCUyMjE0LjEuOCUyMiUyMHR5cGUlM0QlMjJkZXZpY2UlMjIlM0UlM0NkaWFncmFtJTIwaWQlM0QlMjJZTVYwbmpDMEw0VzRkdDFodDh1eSUyMiUyMG5hbWUlM0QlMjJQJUMzJUExZ2luYS0xJTIyJTNFeFZUQmpwc3dFUDBhamtXQVE1TWNHN0xwcW1wWGxkS3F4NVVERG96V1pxanRKS1JmM3pFWUVvUlcyejJWZzdIZnpOZ3o4NTRkc0V5MW56VnZxbTlZQ0Jra1VkRUdiQnNreVhLeHB0RUIxeDVJVjZ3SFNnMUZEOFUzWUE5JTJGaEFjamo1NmdFR2JpYUJHbGhXWUs1bGpYSXJjVGpHdU5sNm5iRWVYMDFJYVhZZ2JzY3k3bjZDOG9iTldqcTJSNXd4OEZsTlZ3Y3Z6UkY2ejQ0T3dyTVJVdjhISUhzWWVBWlJyUjlqUFZaa0s2M2cxOTZlTjJyMWpIeExTbzdiOEVzTU1YRXgwdnpZJTJGajB5TmVuJTJCS2Y3ZTczQjclMkZMbWN1VEw5Z25hNjlEQnhxRTJuWmRURGRCdWczWWhwdW1iJTJGVVJXa0c3YnlxckpDMWpaNU5RMWpUUEtTdWhDUmpMam1oUmNGTzVp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"""),
        'Host': PhotoImage(
            data=r"""iVBORw0KGgoAAAANSUhEUgAAAC8AAAAkCAYAAAAZ4GNvAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANZSURBVFhH7ZjPSxtBFMffRq3EmDQoRDEqRKlKQKp4CV5URGlBr6X3FtpLvLT2kJhoVnPrSWkp7aF/QAs9e4gteJFgvQhKVRT8EUVEYzQN5ofpm+GxbUxisilkV8gHBve9ncl8Z3zzZmfgLiPQX3C73aOCIMTIzEl1dfWv8fHxHTIVgYt3Op2jdXV1n/GxjNl5Eg4Gg49x0KtkFx0uXhTFTy0tLc87Ojq4Mx/8fv/vo6OjN9j2HbmKDhc/PT09297ebscBcGcm5ufn4fr6miyAZDLJShxDLUGuooF9fnS5XGOyxA8NDbGG5FGG7e1t2NjYmJPEezyeDwaD4YVer+cVMnF4eAgjIyPQ1dVFnuLDhC8vL0viNeQHnU4HtbW1WYvSM54JLl6j0USNRiM0NTVlLaoVf1cpiVeKknilkMSzHfOuwcXjtn8vFArxjShbUePgpJm/uLiAQCCQtahWPNukzGYzDAwM8O+Xnp6etIJ1eAM1kaKosbERLBYLWeonRfz+/j7s7Ch6OJJFini2aE9PT8lSP+oLZBmUxCuFdAxsa2uzt7a2cmcm2DFweHgYysryv2D498x7G3LS8ObmZuoxMF/x8XicLOlzgqm7bffKOVKcjGQikchvlAS2eS9L/E1WVlYuMbWOiaLI7nsyMjU1lWTn3mzs7u7C+vr6F6fT+YRcsigtWKXgYeP1ekU8gLsaGhq4MxdsIR4fH7Mbs1domioqKl4yN3+Zihnf0WNmcB1FcP2k7Yzl5eUn0Wj0mdvt/kmuNLh4u91uaG5ufo2VrdybB1qt9sfZ2dmlTqeb7e7u1m9tbdGbwrBarbC2tkYWQFVVFRwcHARisdhDj8dzQu4UuPhCmJyc7McU5+vt7dVgB//9WVFTUwOYdeD8/JzbODkQiUSSuKj9DofDxp03kHMrLDExMWHBcPiOM641mUywt7fHv4uurq4KLuzeqL6+nt+KMTscDkNnZ6eAv3vfZrNZFxYWvlH3ErJnHmdcU1lZuYpp1Zortfp8PnpKB2Ma+vr6yPoLE720tEQWwODgICwuLgbxP/IWU6+X3BzZ4mdmZnzYcT/GZIhcWcEwuDWb4WaTtshvtmF1BEEwYlgmMFE8xfj/Sq8KmvlH9FhUcH09wL7nyEQA/gCxR5oVwYOagwAAAABJRU5ErkJggg=="""),
        'NetLink': PhotoImage(
            data=r"""R0lGODlhFgAWAPcAMf//////zP//mf//Zv//M///AP/M///MzP/Mmf/MZv/MM//MAP+Z//+ZzP+Zmf+ZZv+ZM/+ZAP9m//9mzP9mmf9mZv9mM/9mAP8z//8zzP8zmf8zZv8zM/8zAP8A//8AzP8Amf8AZv8AM/8AAMz//8z/zMz/mcz/Zsz/M8z/AMzM/8zMzMzMmczMZszMM8zMAMyZ/8yZzMyZmcyZZsyZM8yZAMxm/8xmzMxmmcxmZsxmM8xmAMwz/8wzzMwzmcwzZswzM8wzAMwA/8wAzMwAmcwAZswAM8wAAJn//5n/zJn/mZn/Zpn/M5n/AJnM/5nMzJnMmZnMZpnMM5nMAJmZ/5mZzJmZmZmZZpmZM5mZAJlm/5lmzJlmmZlmZplmM5lmAJkz/5kzzJkzmZkzZpkzM5kzAJkA/5kAzJkAmZkAZpkAM5kAAGb//2b/zGb/mWb/Zmb/M2b/AGbM/2bMzGbMmWbMZmbMM2bMAGaZ/2aZzGaZmWaZZmaZM2aZAGZm/2ZmzGZmmWZmZmZmM2ZmAGYz/2YzzGYzmWYzZmYzM2YzAGYA/2YAzGYAmWYAZmYAM2YAADP//zP/zDP/mTP/ZjP/MzP/ADPM/zPMzDPMmTPMZjPMMzPMADOZ/zOZzDOZmTOZZjOZMzOZADNm/zNmzDNmmTNmZjNmMzNmADMz/zMzzDMzmTMzZjMzMzMzADMA/zMAzDMAmTMAZjMAMzMAAAD//wD/zAD/mQD/ZgD/MwD/AADM/wDMzADMmQDMZgDMMwDMAACZ/wCZzACZmQCZZgCZMwCZAABm/wBmzABmmQBmZgBmMwBmAAAz/wAzzAAzmQAzZgAzMwAzAAAA/wAAzAAAmQAAZgAAM+4AAN0AALsAAKoAAIgAAHcAAFUAAEQAACIAABEAAADuAADdAAC7AACqAACIAAB3AABVAABEAAAiAAARAAAA7gAA3QAAuwAAqgAAiAAAdwAAVQAARAAAIgAAEe7u7t3d3bu7u6qqqoiIiHd3d1VVVURERCIiIhEREQAAACH5BAEAAAAALAAAAAAWABYAAAhIAAEIHEiwoEGBrhIeXEgwoUKGCx0+hGhQoiuKBy1irChxY0GNHgeCDAlgZEiTHlFuVImRJUWXEGEylBmxI8mSNknm1Dnx5sCAADs="""),
        'Logo': PhotoImage(
            data="iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AABpJklEQVR42u2dB3wT5/nHSy1jIVSR0bRNR9L0n678k3/bNE3SNm3IJCTsGabBtpaNCStskI0tyWww2GyzCXsPY4MNls6YDWET9gp7Ezb6+xV35ozt00mWdO/d/d7P5z4prvS19Ep+vs/dve/z/OhHGBgYGBgYGBj+jo8/rlml+Pgx76gCHnjggQceeODJi+fvL494+gAPPPDAAw888OTF8zfr0BQfkbxDE2j2AR544IEHHnjghZ8XyC8nv7Aq74is5JsBDzzwwAMPPPDCyAvkl0cVH1reEVXJNwMeeOCBBx544IWRF8gvJ7+wGu/QVvLNgAceeOCBBx54YeRxTLEPJKsLdcVHdd5B/v3jAH8xeOCBBx544IEXfl4VdtHgj8X+cvIL9byjeiXfDHjggQceeOCBF14et4DQdwLA++UG3qGv5JvRgwceeOCBBx54YeVV4e0aEE4A2AfreC+gBvvfyrwZjlMDPPDAAw888MALC49bQFiVlwBUEXqwlnfpwYDJBg888MADDzxZ8rhdAyUJgK9ModpT9x4w2eCBBx544IEnL56Ot2uAJAAaX/cItLwEoDomGzzwwAMPPPBkx+McziUAkUKX/jVshsAlADpMNnjggQceeODJjsffNVBNsGgQuyggkpcAaDHZ4IEHHnjggSdLnoGXAGh9LfrjJwCVKVeIDw888MADDzzwpOVxCYBO0OfskyJ4ewQhf/DAAw888MCTL88gag0fLwHQQP7ggQceeOCBJ3ueuN17vAQA8gcPPPDAAw88tfAq2VEIkw0eeOCBBx54MudhcsADDzzwwAMP8sfkgAceeOCBBx7kj8kGDzzwwAMPPMgfkw0eeOCBBx54kD944IEHHnjggQf5gwceeOCBBx54NMpf9O4/TDZ44IEHHnjgKYLHlf4XXSRIj8kGDzzwwAMPPNnLXyMqAeD1EzZgssEDDzzwwANP1vLn+v0IJwDsg3Xs2b8Bkw0eeOCBBx54spV/FNvtN1Kw9D/7YC179q/n9RbGZIMHHnjggQeevHha9ihJAHxlCtV4CYAekw0eeOCBBx54suPpWJ9zCYDG1z0CLS8BqI7JBg888MADDzzZ8TiHcwlApNClfw2bIXAJgA6TDR544IEHHniy43FX77kEIEpI/hFsdlCVd78Akw0eeOCBBx548uMZeAmA1teiP34CECW6ShAmGzzwwAMPPPBo43EJgE7Q5+yTInh7BCF/8MADDzzwwJMvzyBqDR8vAdBA/uCBBx544IEne5643Xu8BADyBw888MADDzy18AIVPyYbPPDAAw888JTBw+SABx544IEHHuSPyQEPPPDAAw88yB+TDR544IEHHniQPyYbPPDAAw888CB/8MADDzzwwAMP8gcPPPDAAw888GiUv+jdf5hs8MADDzzwwFMEjyv9L7pIkB6TDR544IEHHniyl79GVALA6ydswGSDBx544IEHnqzlz/X7EU4A2Afr2LN/AyYbPPDAAw888GQr/yi222+kYOl/9sFa9uxfz+stjMkGDzzwwAMPPHnxtOxRkgD4yhSq8RIAPSYbPPDAAw888GTH07E+5xIAja97BFpeAlAdkw0eeOCBBx54suNxDucSgEihS/8aNkPgEgAdJhs88MADDzzwZMfjrt5zCUCUkPwj2OygKu9+ASYbPPDAAw888OTHM/ASAK2vRX/8BCBKdJUgTDZ44IEHHnjg0cbjEgCdoM/ZJ0Xw9ghC/uCBBx544IEnX55B1Bo+XgKggfzBAw888MADT/Y8cbv3eAkA5A8eeOCBBx54auEFKn5MNnjggQceeOApg4fJAQ888MADDzzIH5MDHnjggQceeJA/Jhs88MADDzzwIH9MNnjggQceeOBB/uCBBx544IEHHuQPHnjggQceeODRKH/Ru/8w2eCBBx544IGnCB5X+l90kSA9Jhs88MADDzzwZC9/jagEgNdP2IDJBg888MADDzxZy5/r9yOcALAP1rFn/wZMNnjggQceeODJVv5RbLffSMHS/+yDtezZv57XWxiTDR54FPNsNs+Pjbblz0d3nfLX9j1mfBTTZ0GzuH5LLUbbit4Wu8thdTCZVod7ktnBTLc63XMtdmaxxeleZbW71hb/b5fZ6dpktTM7rE7XruKfb7U6mUKzw7U+bkDuWlPy6mxjcs5SY3L2PFNyzkxzasF4i5MZWvy43ua0QnPxfxsXP79mMed1Y+r6F5vadlfF5wseeFTwtOxRkgD4yhSq8RIAPSYbPPAk5nk8VYrF/GxCauGbxcJuVCzfrsUyH10s6OVmO7Pb7GTOW1PdD8wpeR5zylrekecpfpynWOb+H8XPqxTPzlwvfp1Hiv93gcXhnmq2uwYY+y+ztus1+4s2iWNeb9CgxfP4fMEDL6Q8HetzLgHQ+LpHoOUlANUx2eCBFz5ea9u0KHIWbXEWtiw+S08jZ+nkrLz47PpaSGUtAc+Ykne/ODE44r0C4WTGF7/fRHIVIXZo4XP4voAHXqV5nMO5BCBS6NK/hs0QuARAh8kGD7zQ8Go2qFOjdceRf2rfZ36jONvyfnHJObOLz+Z3FsvwHo2yDj/PdcrqYFaSJMjscLdKcBa+wd1WwPcPPPB88rir91wCECUk/wg2O6jKu1+AyQYPvCDxEkeujLKmMf8yOwq6G5Nyl5uTc84rR9Zh4pHkyF6w0Zi0enRM34VtWnVM/wO+f+CBVy7PwEsAtL4W/fETgCjRVYIw2eCBV77w7QUvxDvd9S1OZmDxWazbbGfuqErW4bqNkLz2qNVRMN27ENHOvE4WQuL7Bx54JQmATtDn7JMieHsEIX/wwPOTZ7Jt0VnSXLUtDibd6mD2Q9YS8eyuq8X/XVL8c0t8CvMyvs/gqZRnELWGj5cAaCB/8MATyfN4qlgGuv9YLJuvrA5XdvF/b0PWNPJc+4qTsmHmNNcn5DYMvs/gqYQnbvceLwGA/MEDT4AXbcvXFsukjsXpzmC3t0HWsuK5bpnt61fE2VZ0bdkp43X8fYCnel6g4sdkg6cGXu2mCc+bU9fX8xbPsTPXIVfl8EzJuZvi+q/qGZ+S9xL+PsBTOw+TAx54xZw6X7b/aWzvBY2NSTkzzA73FchV+TxSCZHUISBVDPH3AR7kj8kBT0W8L75o/kxsz3n1jLbsqeYBuZchV5Xy7K5HVjuTb3G6rQmOjc/j7wM8yB+TDZ5CeXG2Nb+JS1qVYkrOOQ4ZgvfUmoG7VofrG4uT+ZDbXoi/N/Agf0w2eDLm2Wz5muLgXtdidy0zpqx5CBmC55vFHDI7Xb1ad8p8FX9v4EH+mGzwZMYzOzf8tjj4p5jtzGnIELxAeMaUtfdNttXL2ved16RWs0bP4u8NPMgfPPBo5Xk8VeLtzEfFQXyF9/4uZAhesHip7uNWB9PNlLalBv7ewJOT/EXv/sNkgydHnmnclkjSRMbsZLZDXuCFlPe47fFQU5rrJfz9gkc5jyv9L7pIkB6TDZ5ceORsjJyVWeyuk5AXeGHl2ZkHFqd7VkJq4Zv4+wWPUvlrRCUAvH7CBkw2eLTzyNkXOQursFgP5AVeGHlmJ5NX/N8vsHsAPIrkz/X7EU4A2Afr2LN/AyYbPFp5pOFLsfgnkrMvyAs82ngWu+tbS8r6hjUb1KmBv1/wJJR/FNvtN1Kw9D/7YC179q/n9RbGZINHDc+cWvgrq4PJ9PaIh2zAo5xnGpC7vX3v+U1r1v/iGfz9ghdmnpY9ShIAX5lCNV4CoMdkg0cLL9a+4edWp3u42c7cgWzAkxvPNGDNRou94FOyOwXxALww8HSsz7kEQOPrHoGWlwBUx2SDRwOPlGW1OJmBpKMbZAOe3Hlmp3udxe7+D+IBeCHkcQ7nEoBIoUv/GjZD4BIAHSYbPKl5nYcWVisWf1+/OvFBNuDJhedwZcenuf4X8QC8IPO4q/dcAhAlJP8INjuoyrtfgMkGTzLeX2x9I8xprmZmp+sYZAOeonlkAavDPbq85kOIB+AFyDPwEgCtr0V//AQgSnSVIEw2eCHgWZPXvVUcGAsgB/BUtXXQzly2OJiOpIgV4gF4leRxCYBO0OfskyJ4ewQhf/Ak4ZFGKxZ7QVZJyV7IATwV8sx2116zY31txBfwKsEziFrDx0sANJA/eFLwGrSK/Zmx/8p+1lT3dcgBPPAe8+KSs7Oju0z4O+ILeAHwxO3e4yUAkD94Yee17zX7U2Ny7n7IATzwyuPl3o2zrUpt8NUCLeILeEHnBSp+TDZ4leE1j7b92mhbNd6cvOYR5AAeeMI8s53ZbUlzvYv4Al6oeJgc8MLCi+m9sLkpOec05AAeeP50HSRrY1wj4235esQX8CB/8GTFa5E45FVT0qr5CObggVeproPHLWmu2ogv4EH+4FHPI41QYvsutpoH5F5GMAcPvCDxHO6ZifaCFxCvwIP8waOS92XHQa8YbTkrEMzBAy8EPLvrHHc1APEKPMgfPGp4sX0WNDAm555FMAcPvNDyzHbXqKbtuv4M8Qo8yB88SXktuszQmZKzMxDMwQMvnC2Hc/a2/3ravxCvwBPBrILJAS/oPNOA/P8zJefuRjAHDzyJ6gb0X9WzXbsJGsQr8MoTP1v3R3SRID0mGzyfw+OpYrYXfGVMzruDYA4eeBLXDXAyq42p619EvALvKflrRCUAvH7CBkw2eELD6nQ9a3UULEfwBQ88muoGMBfMaa5PEK/AY+XP9fsRTgDYB+vYs38DJhu8CuVv3/B/5lT3YQRf8MCjj2d2uh5a0pie5Aod4pWq5R/FdvuNFCz9zz5Yy57963m9hTHZ4JUaZoe7lTm14AcEX/DAo5xndy9MtBUZEP9UydOyR0kC4CtTqMZLAPSYbPBKLfQbtyWSlCRF8AUPPBnxHMx+s73gNcQ/VfF0rM+5BEDj6x6BlpcAVMdkg8cfZGGRxc64EHzBA09+PLOTuRFvZ5og/qmCxzmcSwAihS79a9gMgUsAdJhs8Epd8rcX/rs4iJxB8AUPPHnzjEnZIxo0aPE84p9iedzVey4BiBKSfwSbHVTl3S/AZIPHW+nvbm21u+4h+IIHnjJ4puSc1U3adP8V4p8ieQZeAqD1teiPnwBEia4ShMlWPs/jqWJxMP0QfMEDT4G85JydltScXyP+KY7HJQA6QZ+zT4rg7RGE/MErWexndrqyECzBA0+5PIvddTLBWfgG4p+ieAZRa/h4CYAG8gePG1/Z8p+xOF1rECzBA08VRYOuF//7U8Q/xfDE7d7jJQCQP3jeEZ/CvGy2M7sRLMEDT0U8O/PAanfFIp6qiBeo+DHZyuRZna6/m+3u7xEswQNPpTwHYy+vciDiKVoEY7KVfObvZP5L9gkjWIIHnsp5dmZC07lzIxBPIX9Mtgp4ljSmltnu+gHBEjzwwGM5M8lCYMRTyB+TrWCe2VnY0LvHH8ESPPDA4x2WVNeShm1MP0U8hfwx2Uo883cWtvQu/kGwBA888MrhxQ3IWduw5dcvIp5C/phsRcnfHVd85v8IwRI88MAT4pkG5BZ+2T7lV4inkD8mWxGr/ZmvENzAAw88sTyzo2BT7NDC5xBP5S9/0bv/MNkKlL+D6YbgBh544PnNszM7/EkCEJ+p43Gl/0UXCdJjshUl/3gEN/DAAy9gnsO1MdFWZEA8laX8NaISAF4/YQMmWyH3/B2uaAQ38MADr7I8i9213mTbokN8lpX8uX4/wgkA+2Ade/ZvwGQr4Z5/YVOz0/UQwQ088MALTsVAV3biyJVRiM+ykH8U2+03UrD0P/tgLXv2r+f1FsZky/bMn6ljdjL3EdzAAw+8YPLMTvciUiwI8ZlqnpY9ShIAX5lCNV4CoMdky5cXb2c+MtuZOwhu4IEHXqgqBpKywYjPVPJ0rM+5BEDj6x6BlpcAVMdky5dnthf+2+p03UJwAw888EJcMXBizQZ1aiA+U8XjHM4lAJFCl/41bIbAJQA6TLaM7/mnbfiz2clcQXADDzzwwsEzJq0YiPhMDY+7es8lAFFC8o9gs4OqvPsFmGyZ8mLtG35utbuOIriBBx544eTF9Vsaj/hMBc/ASwC0vhb98ROAKNFVgjDZ1PHI1hyyTxfBCDzwwAs3z5iSd9+asv4TxGfJeVwCoBP0OfukCN4eQchfpjyyEMdqdy9EMAIPPPCk4pmdrmsWO/M64rOkPIOoNXy8BEAD+cubZ3EwwxCMwAMPPMl5dua4MXX9i4jPkvH0/pT7jYD85c0zO1wdEIzAAw88inhbug5eXR3xmWJeoOLHZNPDszpddb1V/hCMwAMPPIp4FgezlNyaRLxHi2DwQiH/x9v9biAYgQceeDTyLE7GgXgP+YMXZF7MQPdPis/+9yEYgQceeFTz7EwDxHvIH7xg8TyeKsV/VPMRjMADDzzqeXbmumWg+4+I95A/eEHgWe3u7ghG4IEHnox4e5pG934R8R7yB68SPG+DH0fBQwQj8MADT048U3L2opr1v3gG8R7yBy8AninN9ZI11X0BwQg88MCTZblg24o+iPfSyl/07j9MNj28aFu+1mp3b0YwAg888GTLS857YElZ9xHivSQ8rvS/6CJBekw2HTyLwzUawQg88MCTPc/uOmcZzPwM8T7s8teISgB4/YQNmGzpeabUdXUQPMADDzyl8MwO13KymwnxPmzy5/r9CCcA7IN17Nm/AZMtLa+dLfdFc3LueQQP8MADT1E8BxOPeB8W+Uex3X4jBUv/sw/Wsmf/el5vYUy2BLy/2PpGmAbkrkbwAA888BTIu222F7yGeB9SnpY9ShIAX5lCNV4CoMdkS8eLs63oiuABHnjgKZZnZ3YkjlwZhXgfEp6O9TmXAGh83SPQ8hKA6phs6Xhtu039R/Ef0W0ED/DAA0/RPId7CPwRdB7ncC4BiBS69K9hMwQuAdBhsqXjNWxj+qkpKXcXggd44IGnDl7hx/BH0Hjc1XsuAYgSkn8Emx1U5d0vwGRLyItLWpmO4AEeeOCpiHemnT37p/BHUHgGXgKg9bXoj58ARImuEoTJDgkvuuc3HxpTch8ieIAHHnhq4sUlZ0+HP4LC4xIAnaDP2SdF8PYIQv4S8mo3sbxgTMrZg+ABHnjgqZEX03t+ffij0jyDqDV8vARAA/lLzzP2X5GC4AEeeOCplWdMXnO0UeteP4c/KsXT+1PuNwLyl57Xusvkf5hTcu8ieIAHHnhq5lnsrsHwRxh4gYofkx1c3uefN33WNCC3EMEDPPDAUzvP7HQ9tDpdf4c/wsfD5EjIi7Et74TgAR544IHH9gpwMttN47ZEwh+Qv6J5LTuM/rMxZc11BA/wwAMPvCeHxcH0gD8gf0XzjANyl+CPHTzwwAOvbK8Aq9P1O/gD8lckL6bPgjr4YwcPPPDAK/+wOJkF8Afkrzhew4atn7WkFnyLP3bwwAMPvIoPs9NVE/6A/BXFs9jXW/HHDh544IHH+OwY2HTu3Aj4IzjyF737D5MdGl58z8XPFX+pL+CPveKjx8gNnjPnr3qOnDjrOXz8TMlB/k1+/v2Fa34fNPKW5u2DHETwRszYIsvP1x9eWtYmxIOKDxP8UWkeV/pfdJEgPSY7+DyLgxkG+QsfSWM2eG7duuW5efNmyUH+/fDhQ08ggzyPRt6Fyzc8bXougPx98Nxbj8ry8/WHlzZ2lceUko94UN5tAIf7fKvYlN/AH5WSv0ZUAsDrJ2zAZAdZ/gPdfzQ7mfuQvzDPPt6lePlzo2PSLE/rbrMh/wp4HQYynlu37ypa/mSkT1nraRQ/wROXlIt4UA4vLmnVaPgoYPlz/X6EEwD2wTr27N+AyQ4uz+xwLYf8ffOGTWZUIX/yvEmz8z314oZ7WnadBfmXcwyftkXx8idj4hyXp75ptKeBOdMTl7wG8eApXlzK2vvRXSb8HT7yW/5RbLffSMHS/+yDtezZv57XWxiTHQSe1Vn4MeQvjpc5q1AV8ifP3/rtIW8CQA5yJQDyL33kFR1WvPzJmLmkyJsAkKOhZYzHOGAt4sFTPNOA3BXwkV88LXuUJAC+MoVqvARAj8kOEs/jqWJ1uDZC/uJ4WfM3qkL+hHPjxg1Py46Z3gSgvmmUp3WPBZA/eySkMZ5rN24rXv5kLFq9rSQBIEfj+Ame2KQcxIOnewWkFb4NH4ni6VifcwmAxtc9Ai0vAagO+QePZ3EwdSB/8bzZK7apQv7ckZa5zCt/Lvj7lQQo+PsycPJmVcifjNUFu0slAI+PDI8xeS3kz+c5XNnwkag1fNV5CUCk0KV/DZshcAmADvIPIo+c/dtd2yB/8bxVBQdUI3/y7/wN+8sE/zY9F6n++5LtPqgK+ZNRsOlgOQnAKE9DS6Ynpt8KyJ+/K8Be+G/4SHD3np6XAEQJyT+CzQ6q8u4XQP5B5BXLvxHk7x+vYPMR1cif/PzGzdvFgT6jjABad5+v2u9LfBrjuXTlpirkT8aWXcfKyJ9bG9LQPNoT03c55P+kW2AefFQhz8BLALS+Fv3xE4Ao0VWCMNmieKSCldnO7Ib8/eNt2X1SNfLnRs+BC8o5A6zgSoAKvi/2CRtVI38y9n53plz5c0d9Y7rHNCAPC0RLKgS6P4CPyuVxCYBO0OfskyJ4ewQh/yDz4h1MC8jff97eQ2dVJX8y5q3cUm4C4E0CeixU3fdlWf5+1cifjKMnL1Yof26BaOOEib7rBKgmvrjd5PYqfFSGZxC1ho+XAGgg/+DzbLZ8jcXJHID8/ecdP31ZVfIvLYDyD+/tAJV8X+KLj+/PX1ON/Mk4d/G6oPz5CwMrrBOgsvhiSWNqwUdleHp/yv1GQP6h4VmdhW0h/8B4F3n3ftUgf27E9pgikASM8rT+eo4qvi9JY4tUJX8yrt+4JUL+j49G1vFl6wSoML6YnQWbuKsA8JGfvEDFj8kWwSMr/53MHsg/MN7tO/dUJ38yMmfkVyh/Tgituim/YuCCnD2qkj953vUbNzz1jb7lz68TUOHtADXFF7v7A/gILYKp4lnSXLUh/8B4pPiLGuVPxqadRwXlr5aKgQcOnVaV/DleE+soUfLnDlI2uEwDIbU1CrKvXwEfQf5U8ax211rIPzBe12GFqpQ/GXfu3vc0TRgjKH9ODqLqBMjw+9JzxDpVyp8cbTqPFS3/kisBZGEgtyZApfGlTdesd+AjyJ8KnsXJ/A3yD5zXZ/QGVcqfG8kjl/qUv5IrBk5fvFmV8ieHuddkv+T/pHfAWO/tALXGF2Ny9jT4CPKnglf85ZwB+QfOSx2/UbXyJ2N53rciV4Mrs2Lgt/uOqVL+5N9dUmf7Lf+SioHm0Z7Y/itVGl9y7rbulPkqfAT5Syv/lPW/MTuZ+5B/4LwhUzerVv5kfH/+apnFYMKXhTNK1wmQ8fel25B81cqf/Lzv0EUByZ/7jjS2jlFtxUCzw2WHjyB/SXkWp3sw5F85XsbsbaqVP8ez9pksejV4ucWCZPp9maSiLpDl8RwZKwKWP79iIGkgpLr44ii41HXw6urwUZB2/0H+/vESbUUGs9N1DfKvHC9r0Q5Vy59wxs9a65f8S64E8G8HyPD7snXXUdXKn4zhWbmVkn9JxUCyRVBssSAFxReLk0mAjyoWP1v3R3SRID3kL55ndboTIf/K82av3K1q+ZNj847v/F4NXup2gAy/L50H53sePHigWvmTMW7W+krLv6RYkD9JgFLii8N9sLzywJC/V/4aUQkAr5+wAfIXObyFf1y7IP/K8xav3adq+ZPjxo2bnpadxge8IEyOFQMnLdyuavmTMX3RhqDI/8nugDEeU8o6dcUXe+H7kH8Z+XP9foQTAPbBOvbs3wD5ixuWNNe7kH9weCvydqla/hxv0PjsSiwIG1GcBMyW1fdl+97TqpY/GfNXbQ2a/LmjScKkiq8EKDO+zID8S/k8iu32GylY+p99sJY9+9fzegtD/r4u/zvckyD/4PDWFu5VvfzJyNuwv9ILwuRSMbDz0ELPgwcPVS1/Mlbm7wqq/PlXAsr0DlBofDGlMndihxY+B/l7eVr2KEkAfGUK1XgJgB7yF7f4z+oouAX5B4e3Yet3qpc/Gdeu/+BpYM6o5D3h0bKoGDhu7nbVy5+MdUUHgi5//pqAkiRA6V0CHUxHyN97Jb8aLwHQ+LpHoOUlANUhf3HD5HRZIP/g8XbuPaZ6+XPja+e8INwTzvAvCZDg+7Lp2xOql78/vSACWyDK3g5QRcXAgl0q7xLIOZxLACKFLv1r2AyBSwB0kL94njllzXbIP3i8Q0e/h/zZMWf55iDdE86gtmLgV4MKPXfv3Ve9/MnYfeB0yOTP8RqY0j1xtmzFxxeyLkul8ueu3nMJQJSQ/CPY7KAq734B5C+S167nN+9B/sHlXb56E/Jnx6Hj54N4T9hHEiDR92X0rK2QPzsOnzgfUvmXqhjYb4Wi44vF4Zqk0jo2Bl4CoPW16I+fAESJrhIE+Xt5xqTsiZB/cHn37j+A/Hmj3ddZQbwsXEESIOH3xb31KOTPLwMdYvlzR0NLpvd2gFLjiylp7a3m0bZfq3ArO5cA6AR9zj4pgrdHEPL3g1fny/Y/NQ/IvQz5B4+XOIiB/J8ao6bmBfmyMD0VAzsMZDy3bt+F/HkLP8Mhf47XyDreY0rJV2x8ie27xKzCrewGUWv4eAmABvL3n9e+77wmkH9wed1HFEL+T40N2w6H4LIwmwRI/H0ZPm0L5M8bd+7eC5v8SxYGJmYptmJgXHJ2tgq3suv9KfcbAfkHxjMmrZ4J+QeX1z+zCPJ/aty+c8/TJH5MCM4MR0teMTC/6DDk/xSvsSU9bPJ/UidgrMc4IE958SU5957Rtvx5+K2CNQA/CnCoXf4NWsX+zJy85hrkH1yeY9ImyL+c0X/Y4hCdGY7wtO4+R5LvS0Ia47l24zY+36d4rb/KDKv8+VsEyxQLUkSXQKY9/BbEgS6BNWvE9l3YHPIPPm/E9C2Qfzm8+SuLQnhZeISnTfe5Yf++DJy8GZ9vOby4HhPDLn/utlC5ZYPlHl8crmz4DfIPKs9sd82A/IPPGzt3G+RfDu/Q0dMhviwc/oqB2e6D+HzL4XVMmiaB/HkVA63jnjQQUkJ8SWUeJDg2Pg+/Qf5B4bXoMkNntTPXIf/g86Yt+Rbyr4Bn7p0V0jPDBuZMT9tei8PyfYlPYzyXrtzE51sOr/egBZLJnzuaJk5WVMXAeLvbCL9B/kHhmZ2FDSHr0PDmrd4D+VfAGztzTRjODMNTMdA+YSM+3wp4KaOXSyp/jtfQnOGJ7b9SEfHF4nStgd8g/6DwrA7XN5B1aHjL1x2A/Cvg7dh7Iixnhj6vBATh+7Isfz8+3wp4QyfmSC5/jtHImskmAfKOLyZnwUPLYOZn8BvkXymezZavsdpdVyHr0PCe3hZGQzDff/isdyue1HIg7XK/7DguLHJ4nAQsCcn3Jb74+P7CNUk/31z3HmqTiTEz1lEhf26BaJOE8YqoGGhxuKIhfz92/0H+ZXnxaa73IOvQ8TbuPEHdmdyU+Yy3SQsNckgbszKMcsgofSUgSN+XpLFFkn6+pNxuy04TqL2SMGVBISXyf7JAtNTCQLnGF4frG5X7jSv9L7pIkB7yL82zOhg7ZB063q4DZ6i7jDt21jrPsrU7qZBDrntvWOVArgRE914a1O/Lwty9kn6+ZA59JQBSvr65KzZTJP8nLaVJxcAK6wTIIb44Ci41nTs3QsXy14hKAHj9hA2Qf+lhtbu2Qdah4x0+cZG6e7gjJ6/xjJq6lgo5XL52q1jKGWGVA/l9pE5AsL4vx05dkvTzHZ6VK5gASP39W563kzL5+6gTIKP4YnK4/6lS+XP9foQTAPbBOvbs3wD5Pxnxgzb+ArIOLY9cnqVtAVfa2FWeLqlzqLky0cU+J+xyqG8c6WldkgQE/vn2GVUo+fzF9ZxaYQJAw+e7tnAfhfJ/kgQ0ip9Q8e0AyuOL2e4aoEL5R7HdfiMFS/+zD9ayZ/96Xm9h1cufDLKIBLIOLe/8xcvUrd5OTl/mrcV/7/59KpKTWUs3SiKH+sZ0T9se8yv1+c5YskXS+Tt74Zr3vZWXANBy5al08yea5P8kCWjacYosKwYaU1ZvVdltbS17lCQAvjKFarwEQA/58xIAJzMbsg4dz5Ka57lx4wZ1W7d6D17oDYr7Dp6kIjk5ePSspAvCKlMx8Nt9xySdP24NRYuvxlO7dXDnvpMUy593JcA6/kkDIbnEq6ScR62sA/9HJfLXsT7nEgCNr3sEWl4CUB3yfzLI9j+znbkMWYeOl5iWR+W+7S6ps73BcWXeNipe36NHHk90tyzJ5FCyMNDPz7fbkHzJ52/YpNzHCUDH8dTWDTh49Bzl8uetCeiQ5TEmr5VVvIrtt9ikAvlzDucSgEihS/8aNkPgEgAd5F96kMUjkHVoed2H5lNZtMXaZ4o3QI6ZnkvN6xs5ZY2kcqiwToDA5ztp/kbJ5y+m+2Tv62+eOI7aokGnzl6Rgfz5XQTHe2L6rZBNvDIlr56rcL9xV++5BCBKSP4RbHZQlXe/APJ/evW/w9ULsg4tr9+odVRWbGvfbbw3SHZ3fkPN62O2HpJcDj6TgKc+3y3fHpF0/k6feyLWZh3GUlsx8PLVWzKR/5OW0g0tmR5jUrZM4tX6Uz/yeKoo2G8GXgKg9bXoj58ARImuEqSyokFmh2s5ZB1ann28i8pyra06Pu7P3rzDaG81Phpe381btz0NzSMll0MD85jybwc89fl2Hvz49o6Un2/2+t1Pmt0kZFJbLphUnZSP/HkVAztM8Bh9bRGkJF7FpzAvK9hvXAKgE/Q5+6QI3h5ByL/c+/+eH5e6/w9Zh4SXPmMLlbXam1jTS4IluTxLy+vrNXA2FXIo0zugnM933JwiyeU6aHx2yfttbEmnuldAA9MIGcn/yQLRxgkTxRcLkjBemR3uVgr2m0HUGj5eAqCB/AXO/u0Fr0HWoedNmL+dOvnfuHHTU9/4JFiu33iAmtc3d1khNXIouRJQwee7bc8pyeXapuukkvdLrp7Q3CioZWKmzOQ/qtTCQFNKPt3xysFkKthven/K/UZA/sKD9JKGrEPPm7HsW6rkT45Ll6+WCpaT5rqoeX0HDp+iSg7eKwE95pf5fDsPYQK6dRLM+Tt68kKp99vQNJLqLoEx3SfIUP5Pdgc06zjV95UACeOVyeneqXq/BSp+tdVSLv7CTIGsQ88jNeJpkj/599VrN0sFN1ITgKbXZ+o9lSo5lFcxcNy8bZLLdXHO9qeKGo2gukVwQr+pMpW/TCoGphY8MqVtqQG/Qf4iFgAWfAdZh56X7TpIlVzJz89ful4qsJF2vGQfPi2vb/w3BdTJ4emKgZu+PSG5XG3DFpR5v7TKnxxf27+RsfxLVwwsKRZEWbyypDG14DfIX3AY7at/AVmHh1ew+QhV8ifj5JnLZQLbiTOXqHl923Yfp1IO3BbBrwYVeu7euy+pXK/fuOFpljC6zPt95CuTk/DzTRq5VOby5yUBiZOf3A6gKl65B0D+kL8gL7bPkhaQdXh4W3afpEr+ZBw6dr5MUCPNWmh5fffuP/AWtaFRDmRh4PApbsnluvXbQ+W+Pn/XJYTz8x08frUC5P8kCSC7A8wp+XTFK7trLeQP+Qvy4pJWDYWsw8Pbe+gsVfInY8/B02UC2rhZ66l5fWTYM1ZQK4f1G6W/rTN13vpyX9/dew+olD8ZGdPzFCL/J0fTxIme2P4rqYlXJidzg2zxhvwh/wp5ccnZ2ZB1eHjHT1+mSv4VXWLv5phHzesjY3XBbirlQDoo3rp9V3K5fm2fVe7rIwV3aJQ/GVnz3AqS/5OKgY0smWwSQEe86pCy/hXIH/KvkGccsOYUZB0e3sUrN6mSPxlF28u2ZiViu3//ARWvjwwybw3M9MmBtFGWWq4XLl7x7vkv7/Xd+uEulfInY/ayTQqT//CSXSKkd4Dp6YWBEsUrc+q6+mqTv+jdf2qXf4v2tpcg6/Dxnj4jo0Gu64oOlBvYSEtemmrJd0qZTZ0cct17JJdrQdHeCl/f9Zu3qZQ/GUvX7FCc/J8sEBVZJyAM8SouaVWKivzGlf4XXSRIr1b5k6N9r3m1IOvw8BLSGOrk//jy+p5yg9uytTupqiU/Y3ERVXIgl3qv3bgtuVzHzMyv8D1dvf4DlfInI9e9V5Hy57eU9i4MTF0nabwyJWcvUpH8NaISAF4/YYNa5U/+bXYUdICsw8PrOqyQOvlXfCY2yjNo7HKqasnvP/w9VXLoM2QRFXK19J1e4Wu8VM4tJ1q+f4+7PSpT/vzKkc2+mlq2TkAY45VpwOoDKpE/1+9HOAFgH6xjz/4NapU/+bnZ7h4HWYeH12f0BurkT8a8lVvKDW7m3llU1ZInW9rbdJlIjRyW5+2UXK5nL1wTWBsx2lvkiUb5k7F9zwlFy5+fBDRJzKo4CQhxvIpLyXnYtF3Xnylc/lFst99IwdL/7IO17Nm/ntdbWHXy95YAdjAbIOvw8FLHb6SyP/vMJUXlBjfSIOjsuYtUlZMdPD6bCjkQ6Z67KL1cV63fJfg6SYJAo/wfX9E5q3j5P50ElCkbHKZ4ZU7N+4eC/aZlj5IEwFemUI2XAOjVKn9vC2AncwOyDg9v8JRNVPZnf7Idq2xwYzbvo6qc7Iq126iQQ2LSLCrOrJ1jVgq+ztO81s60JZ+k2qQa5F/6dsA0SSoGxjvd7RTqNx3rcy4B0Pi6R6DlJQDV1Sp/Msj+UMg6fLyR0wup7M8+Zua6CoPbjMUbqKolf/zUWe+VCamD+ZT50i/ofPjwkafFV+MFXydX0pnGK08XL99QjfxLXQlImOTdIhjOeGVxMkMV6DfO4VwCECl06V/DZghcAqBTs/y9l/+dhR9D1uHjjZuzgcr+7COycisMbrbhS6irJW/ulSV5MN914JTkZ9Z7D53x+TqPnrxIpfzJIAWU1CT/J0lAhrdiYJxtVdjilcXOLFaY37ir91wCECUk/wg2O6jKu1+gavmTYXG64yDr8PGmLdpMZX92R8bSCoMbOcP0p59MOGQzaupqSYM5mZMH7PuRUq4zy2yLLHt8d+wclfLnFnWStRRqkj+/pXTThAnhqxiYyuxQmN8MvARA62vRHz8BiBJdJUjhRYOsDsYOWYePN3fVdir7sycNXyAY3I6fvkRVOVnh7WOhD+ZpY1dRcVm9m2Ouz/e7c+9RKuXP8Zp3GK06+fMrBjaOH+dtIBTqeGVyFlz7kcdTRUF+4xIAnaDP2SdF8PYIQv4lCYB7JmQdPt6KvF1U9mfvPWiOYHAjdfhpKid789YdT0NLhmTBPMe1R3L5kwp/wnPw+P2SLoG0yp88v13XcaqUP79iYPNO033XCQhCvIodWvicgvxmELWGj5cAaCD/pxIAJ1MIWYeP5956lDr5k6Nr6izB4DZy8hrqysn6PvsNTTAnl6wvXLom+WX19RsPiHq/m3YcpFb+hGPtM1m18udXDGzSIUt8EhBgvEpILXxTQX7T+1PuNwLyLzcBOANZh4+3fe9p6uRPjkTbNMHgZu03g7pystMXbZAkmHdMmkXFPfXhWbmi3u+GrfuplT85uqTMVLX8S20R7Di1bJ2AIMYri9PdWHW9cAIVv9Inp/PQwmqQdXh5B4+ep07+5N9WgVKy3FlveTXvpbwMvnPfSUmC+YRv8qm4p9626yRR75e2Og5P8/oOnqd6+T/5OxsjfDugsvHKwXRTlfwrM5Q+OZaB7j9C1uHlnT57lTr5k5/H9JjiM5gV7ThCVUW5u/ceeJomjAl7MN+4/aDk8icr+8W+3w3bDlErf/JvX4WM1CJ/fhJAKgaWaSAUjHjlcI+G/CF/74h3FH4GWYeXd+XaD9TJn4xWnSb4VfiGln3l/YYtDmswb5Yw2nPt2nXJ76nPWb5Z9Pt1b/6OWvmTn6dPWQv5+7oSELx4tQLyh/wf3/+3u2Ih6/Dy7t1/QJ38yRA+k3589Bg4n7qKcmWbGIU2mJPtkjQsqOueNl/0+11XtJ9a+ZMxcY4L8q8gCSBrAozJa4MWr0xO907IH/J/fAvAwfSArMPHSxzEUCl/rhiLr4DUJH6M587de1QVlSnbTCa0wXxh9kbJ5X+j1PY/3+83172XWvmTMWvpRshfqGxwhwkeY1J2kOLV+lOQP+TvHWZHwRDIOny87iMKqQu+ZNy+c090cOPvKafhTNhbC7/j+LAF88PHvpd8Qd2T7X/i3i/pFkir/MlYnLMd8hesGJjuad5xclAqBsYl5d2pWf+LZyB/lcufPC8uOXs6ZB0+Xv/MIuqCLxlkdb/YYDRzkZu6ojIpo5aFJZjH9ZhExfsdOjHHr/e7bO1OauVPxuqCPZC/z4qB6Z7GCeM8pgGVrxjYvH3nX6pB/qJ3/6lR/uT5puSclZB1+HiOSZuoC75knL94XXQw6jd0PnVFZcgZZDiCeeb0fMnf76NHjzytOk/w6/0uWr2NWvmT4dp8EPL3yRvhvR1AFgaa/C0b/FS8apM45nWF+40r/S+6SJBebfInnLjk1UWQdfh4I6ZvoS74knHyzGXRwahFYmYxk66iMvsOnghLMC/afljy97vnu9N+y2buis3Uyp+MrbuOQf6ieBm+6wSIiFcx3Wf/R+Hy14hKAHj9hA1qkz85TMlrDkLW4eONnbuNuuBLxqFj5/0KRkdOnKdG/hyvVcfMkAbfRtZMb+taqd9v1px1fsuGLLKjVf5kVNzSGPIvy3ucBDTtOMVjTl0fULyypK77TMHy5/r9CCcA7IN17Nm/QW3yJ4cxJfcSZB0+3rQl31IXfMnYffC0X8Foed5OquRPjtT0RSENvj0HLqDi/Sb0m+q3bKYtLKRW/mQcO3UR8veL9zgJ+LLzzIAqBsY7mBYKlX8U2+03UrD0P/tgLXv2r+f1FlaN/Gs1a/Ss2VHwELIOH2/e6j3UBV8ytu0+7lcwGsi2wqVpa9nCVZtCGnxnL9sk+fs9fuqsp77Rf9lkzXVTK//y16BA/r55GSV1AsqsCfAZr9yJCvSblj1KEgBfmUI1XgKgV5P8yb/NttwXIOvw8pavO0Bd8CWjcNthv4JRdLcs6vaVl38WGbzgS+oNSP1+F6/eFJBsxs1aT638vXUNbt2B/APiZXgaWoqTgK+mPWkgJCJeWRxMssL8pmN9ziUAGl/3CLS8BKC62uRPfm5Kc70EWYeXl7fhEHXBl4z8Dfv9Dkanzl6hbmtZm3Kb41Q++LbsNMG7+l7q99t/6PyAZJMxPY9a+XO1HB4XooL8/ec9TgK8twPEVgx0uIcoyG+cw7kEIFLo0r+GzRC4BECnRvmzfQBehazDyyvYeIC64EtG9vrdfgcjsnebtq1l5NZEKIIvaVYjtfwvXb7qaWJND0g2I7JyqZU/N5p1GAP5B8wjSYD4ioEWB5OuEL9xV++5BCBKSP4RbHZQlXe/QJXy91YBtBe8BlmHl7dpxyEqg++inG1+ByNSjIa2rWUr83eFJPiuWrdL8mRnfdHegGUzeHw21fInz2vbeRzkXyneCE8D0+OKgXG2VYLxymx3j1OI3wy8BEDra9EfPwGIEl0lSKFFgyxO5m+QdXh5uw+coDL4zljk9jsYxXSfTN3WshNnLoUk+J45d1XyZCewjnmP3++A9MVUy58839w7C/KvNO9xEtCsY5b3dkBFMcniYCYrxG9cAqAT9Dn7pAjeHkFVy//xLYCCdyDr8PKOHP+eyuA7cXZeQMHoaTHScJlZeB2A/8HX2Guq5PJ/8OChd+FloHLgqjfSKn/C6ZQ8A/IPUsVAcjuALAysqE6AxemepRC/GUSt4eMlABrIn00AnMx/Ievw8s5fuExl8M2YmhNQMMp176FudXnF6wACC76jp+VJfqXjwJGzlZJD70FzqJY/OchrhPyDVzGQLAxs0WVW+XUC7Mx8hfhN70+53wjI/8mwOgs/hqzDx7Ok5hWfyT2gMvgOm7AyoGA0bFIudavLl+d9G9TgS+rUS32bY/qiDZWSw9f2WVTLnxzkNgXkH9yKgd4tgt46AeueilHuZarqhROo+JU8OWaH+3PIOny8ToMZaoOvM2NZQMGIrAOgbXV52XoAgQffBuYMb6dEqW9zdEz+plJy6DRgOtXyJ/8ePikH8g9BxcCGlrHeLYL8JMDsZFarRv6VGUqeHLOzsCFkHT5er/QN1AbfAd52uoEFo0PHzlC1wIxs12/VeWJQgm+nlNmSy//cxevsHvnA5ZBom0m1/MnPx3+zHvIPUcVALgngbgeYne51kL+K5e+9BeBwN4esw8dLHltEbfDtO3RRwMFoac5m6haY2TNWBCX4Tp7PSL7GYdnanZWWg6XvdKrlH4zbHJD/aJ9JAG9hYCHkr2L5excB2pkmkHX4eAMnb6I2+HZzzAs4GKVlLqWvrsHqbUEJvlt3H5d8jUO/YYsrLYeYHlOolj8ZC7K3QtYhrxg49vHCwOQ8N+SvYvk/XgToqgtZh483auZWaoNvYtKsgINRm85jqVtg9u2+Y5UOvo3jx3hu37knqfxJjXzShriycmjTZSLV8ieDFFuCrMNRMXCMp0niuCLIX8Xy9xYCSmNqQdbh402Yv53a4Ev2ulcmGJGFdzTdY75+/YanecLoSgXLXoMXSr7AcV3R/qDIoXniOKrl//i9HoCsw1QxsF7MsCLIX8Xy9yYAKes+gqzDx5ux7Ftqg6+4JjoVB6PleTupu8fcZ/DcSgXLb5ZulHx3Q5pgbwPxcmhkyaRa/mRs2nkUsg4Tr1bbFEYN8he9+09t8ifPi+k99xPIOny8hbl7qQ2+TRPGVCoYOTJWUHePecZCd6WC5bbdhyWV/737D7xn7sGSwwOB30XDVs7dB05D1mHi1foyab3C/caV/hddJEivJvmT57ftNbMmZB0+XrbrIJXB90kr1sCDkdh2ueF8vzv3nQw4WDZLGO25dv26pLsbKj4jDkwOZD0DrfIn4/CJ85B1mHifftl/jcLlrxGVAPD6CRvUJH/Caf/1tH9B1uHjFWw+QmXwvfXD3aAEo4NHz1J1mfnuvfsiFtCV/377U1A7f9TUvKDK4emCRrRVcPz+/FXIOky8D1skr1Cw/Ll+P8IJAPtgHXv2b1CT/MnR5utJb0HW4eNt2X2SyuB78crNoASjeSu3UHePuZtjbkDBcu7yQkllSK6mlF2XUTk5XLh8g1r5k0ESFMg6PLyPmvdbpFD5R7HdfiMFS/+zD9ayZ/96Xm9hVcifHO06jX8Dsg4fb++hs1QG31NnrwQlGJH96rTdY86a6w4oWO45cFxSGe4+eDrocjh97gq18ifj/v0HkHWYeB807j1PgX7TskdJAuArU6jGSwD0apI/+XeMbdWvIOvw8Y6fvkxl8P3u2LmgBCOykPDuvQdUXWYu3HbY72DZqmOm5DKcOMcVdDkcPXmRWvlzo0n8GMg6DLz3G/eeqTC/6VifcwmAxtc9Ai0vAaiuNvmTn0fb8rWQdfh45FI7jcF314FTQQtG2/eeoOoy89XrP/i9wDF11BLJZRjXc2rQ5UDWaNAs/8fbUSdC1mHg/bd+tzEK8hvncC4BiBS69K9hMwQuAdCpUf68aoC3IOvw8G79cIfK4PtktXnlg9EUCmrnPz3Mfab7FSxX5H0r6efx5IpMcOVAEj2a5U+eZ+yZBVmHgfdu7Q5pCvEbd/WeSwCihOQfwWYHVXn3C1Qrf28CYGeOQ9ah5yU43dQG34JNB4MWjLjueTSdaY7IyvUrWJ78/rKkn8e0hYUhkUPhlv1Uy588v6NtOmQdBt5bH7XrpRC/GXgJgNbXoj9+AhAlukqQgosGWe2ubZB16HmdBuVTG3yz1+8KWjBqYM7wXLl2k6pkZ9X6XaKDZfvukyX/PKz9podEDvmFu6mWP+H0SPsGsg4D7/V/NbUoxG9cAqAT9Dn7pAjeHkHVy9+bADiYHMg69Lyew/OpDb5zlhUGNRitXr+TqmSHLH4TGyyHTsyR9PMgPRVCJYec9Tuolj85koYvgKzDwPvDm7WaKcRvBlFr+HgJgAby5ycArm8g69DzkjLWUxt8p8xbH9RgNHjccqqSHbKnvkXH8aKCZa57j6Sfx7QFrpDJYfmaLVTLnxyDxi6DrMPAe/lP//qnQvym96fcbwTk/1QC4GRGQdah56VNcFEbfMdMzw1qMGrbeSx1yU7/YYtFBUtSjU7KzyOh75SQyWHhqk1Uy5/8O3NGPmQdal5c+qNfv/tuNVX1wglU/EqfnGJZJUHWoeeNnF5IbfAdNmFl0IPRvoMnqHq/T1/lKO/9xvaYIunn8d2RU576xtDJYcGqLVTLn/x86oJCyDrEvHqxw6+pSv6VGUqfHKvTnQhZh543aeF2aoOvY/TS4MsmeytV79e9aa/PYDk8K1fSz+ObJUxI5fDNsk1Uy58MUk4asg4tr067oSchf8jfO8xprmaQdeh5s1fupjb42oYvDnowEioLLMX7PXvuYsnZdUXBcg2zV9LPo2vqrJDKYUrx2TXN8idjed63kHWIeZ+1TdsF+UP+bAJQ+DZkHXrekrz91Abf7mnzgh6MSElX0o2Ppvdr7jVZMFieu3hdstd3+vvzxQnKiJDKYfw3BVTLn4y8Dfsh6xDzPm4xIAfyh/y9wzKY+RlkHXpeLvMdtcE3wTYzJMFo665jVL1fssWvovdk7DVV0te3LHdLyOVA2gvTLH8yirYfhqxDzHu/0dfTIH/I3zv+YusbYU5Z8wNkHVoes+0YtcE3pvvkkAQj0tCGpve7PG9nhe8rfcpaSV9f0silIZfDkAmrqZY/GTv3nYSsQ8x79zPTcMgf8i/hGZPW7IOsQ8vbvvc0tcH38R754AcjcmWBpvdLmuFU9N7IpWepXh/pEfG4C15o5eDIWEG1/Mko25kS8g8276/vNempFvmL3v2nVvkTTlxydjZkHVrewaPnqQ2+DS0ZIQlGpAvfhcs3qHm/pN9843JES17n+UvXJXt97s3fhUUOtuFLqJY/GafPXoGsQ8x79fV/t1GB37jS/6KLBOnVKH9yGJOyx0HWoeWdPnuVyuBLFuqFMhjluPZQ9X67OeaWeY2m3tMkfX1CaxOC+Xn0HLiAavmTcfnaLcg6hLw67YY//N///ev/qED+GlEJAK+fsEGN8vdeAUha2QeyDi3vyrUfqAy+167/ENJgNGhcNlXvd+ysdYL3/8P9+h4U/7dlpwlhkUPnlDlUy5+MO3fvQ9Yh5H0RPfCsCuTP9fsRTgDYB+vYs3+DGuVP/m1JWdcYsg4t7979B1QG37MXroU0GLUqlhupxU/L+11buK/MayQ/k+r1bd97ImxyiO83g2r5c6ORJROyDhHv09apOxUu/yi222+kYOl/9sFa9uxfz+strCr5k58npBa+CVmHjpc4iKH2zIt0nwt1MNp/+Cw17/f46Uvl7v+X6vWVd0UiVJ8Hv9QxrfIno5X3ighkHQreR1/2X6Vgv2nZoyQB8JUpVOMlAHo1yp/8//G2fL3V7noEWYeG131EIbVnXvsPfx/yYPTN0o3UvF9yNaJ54riS1xbXa6qkn0dMsZTDJYfWnSdSL38y4npNgaxDxHuvfpcxCvWbjvU5lwBofN0j0PISgOpqlX9JRUCn6zvIOjS8/plF1J55lb0EHfxg1M0+iyrZ9By04En9/0k5kn0eB4+eC6scmiaMpV7+5Hkd+k+FrEPEe/P91t0U6DfO4VwCECl06V/DZghcAqBTu/zJsNrdCyHr0PAckzZRe+a1YdvhkAejhqaRnvMXLlMjG1KgiHt9K9ZulezzmL5oQ1jl0MA8inr5k+d/bZ8FWYeI9+L//LW+wvzGXb3nEoAoIflHsNlBVd79AtXL35sAlNcWGPIPCm/E9C3Unnnll9ReD20wyivcTY1sHr/nx6/v0NHTkn0eiUmzwi6HS5evUi1/wuk/dD5kHQJendhh137k8VRRmN8MvARA62vRHz8BiBJdJUgFRYOsdlcjyDo0vDFztlJ75rVq3a6wBKORWdnUyIYsfCSvKbrrOMk+jzPnrnoLEIVbDqQrIs3yJ0da5lLIPwS8Wq2d2xXoNy4B0An6nH1SBG+PIOTPG/GOwlch69DwJs3bRO1l14XZW8MSjIy9plAjG8JoGj/KKxqpPo9Fq7dJIofjp85SLX9ykGQR8g8+78Mmfecr0G8GUWv4eAmABvIvO2w2z4+tTtctyD/4vJlLt1B72XXa/IKwBSNS5pUW2XRJmelZvHqTZJ8HqconhRy+O3qGavmTf2fNc0P+IeD98zPrIAX6Te9Pud8IyL/iYXW4NkL+wectWL2D2suu42auCVswIt34aJHNrn3HPOcuXJLk87h6/Ydy+i+ERw6Hjp+jWv7k53OWb4b8Q8B77e36ZtX6LVDxq0X+j9cBMBMg/+Dzstftpvay68isVWELRimjl1MnGyl4pD+CVHLYe+gM9fO3dM0OyD/YvLj0R8/9/JW31ew3yN/nFQAmHvIPPq9g4wFq5TVo7LKwBSNSgOfBg4eqlj8ZJBGSSg6k7gPt87eG2Qv5B5n3efthJyB/yF9wWJLz3oT8g8/7dv9pauU1YOSisAajXQdOqVr+t+/c8xbkkUoORTuOUD9/hVsPQf5B5n3SPGkF5A/5C/JqNWv0rDFl7U3IP7i8wycuUiuvfkMXhTUYTVtYqFr5l5abNHIo2HSQ+vkT1yAJ8veH985n8QMhf8jfJy8uaXU+5B9c3tkL16mV19fOeWENRnJoSRtK3rBJuZLKIde9h/r5O3DkLOQfZN4rr7/fGvKH/H3yjLaVaZB/cHk3bt6hVl7C1eiCH4wamDM8167/oEr5P3z4yNOq03hJ5eBrJwYN83fyzGXIP4i8Ou1HXOUqAEL+kL8gr33f+fUh/+Dx4tMYbwc6WuVFuuGFO7itKzqgOvmTsWPvCcnlsCB7K/Xzd/HKTcg/iLxarR1utcpf9O4/yP8xr61tSQ2z0/UQ8g8Or9OQQqrlRVrEhju4jcjKVZ38yfMypuVILodZSzdSP38/3L4H+QeRR1oAq9BvXOl/0UWC9GqXP8czO5ntkH9weD3TN1AtrybxY8Ie3Np1m6Q6+ZPnx3w9QXI5TJ7PyGL+yK0iyD84vNffaZigQvlrRCUAvH7CBsifqwfgHg35B4eXPLaIWnk9KP5ZxQ1pQhvc9h44rir579p/jAo5jJ21Thbz16LjeMg/CLw6MSPvvfTSK++oTP5cvx/hBIB9sI49+zdA/mw9gDTmS8g/OLyBkzdRK6+bt+5IFtxmL2VUI3/CmTx3HRVyGDlljSzmL6bHFMg/CLxarey7VSb/KLbbb6Rg6X/2wVr27F/P6y2savmTYRqS/1Or3fUI8q88L33mVmrldfHyDcmCW+9Bc1Qjf3Ik9JtKhRwGjc+Wxfx1sM2E/IPA+2+DztNVdGVbyx4lCYCvTKEaLwHQQ/78ssC8xkCQf8C8CfO3Uyuvk99fliy4Nbake27fuasK+R85fsZT30iHHEgZYjnMX9fUmZB/EHivv1O7o0rkr2N9ziUAGl/3CLS8BKA65P9UAuBkkiD/yvNmLPuWWnl9d+ycpMFt665jipc/Oeau2ECNHEjlRznMX5/BcyH/SvLqRA+68vrrb/5GBfLnHM4lAJFCl/41bIbAJQA6yL/siHcUvAP5V563MHcvtfIidfmlDG4T57gUL3/y796DFlAjB3JmLYf5s49aDPlXkvdR875rVSB/7uo9lwBECck/gs0OqvLuF0D+5Yymc+dGmJ2ui5B/5XjZroPUymvzzqOSBrcE20zFy//q9VueRpZMauTQof80WczfsAkrIf9K8t75NHaQCvxm4CUAWl+L/vgJQJToKkEqLRpkcbpnQf6V4xVsPkKtvEhjGCmDG9mCeOHyDcXKn/zcv9a2oZeDuVeWLOZvzIw1kH9leDHDHr3w6z/UVYHfuARAJ+hz9kkRvD2CkL+vBMDBtIH8K8fbvOsEtfLKce2RPLiR16BU+ZNhz1hBlRzadR0ni/mbuaQI8q8E77PoQXtV4jeDqDV8vARAA/mLG0b76l9A/pXjbdt9lFp5LcndLnlwGzQuW7Hyv3P3vqdpwliq5NCyY6Ys5m9xznbIvxK8/zboPlklftP7U+43AvL3j2dKzt0G+QfO2//dKWrlNXORW/Lg1qrzxHKbJSmhV8CGbYepk0OT+ExZzN/qgj2QfyV4f/5HPQv89tQagB8FONTcKCguaUUS5B8478Tpc9TKa+LsPCqCG+n/rjT5k0GaHtEmB7LuQmx3Sinnz7X5IOQfIO+LmBHnatR4+Rn4LQhD7V0C23Qe9xfIP3DexUtXqJVXxtTVVAS32cs2KU7+Dx8+EtlpMfyyuX3nHvXzt3X3ccg/QN4HjXvNht8g/6DxrHb3Zsjff541dS3V8hoyfgUVwa3HwPmKkn/5NRbokc3V6z9QP3/7Dn0P+QfIe+3t+mb4DfIPGs/qYLpB/v7zOg3Kp1pe9lFLqAhuZJ/8zZu3FdUimBQ5olU25y5ep37+jp++BPkHwKvTfsSZH3k8VeA3yD9ovPgU5mXI339en1GFVMsracQSaoJb/oY9ipE/GcZeU6mVzYkzl6ifv/OXrkP+AfDeb9x7JvwG+QedZ3UwGyB//3ip4zdSLa+eAZWoDU1wGzFplWLkf+TEBaplQ3pA0L71suJW1ZC/EO9Pb9aJg98g/6DzLI7CTpC/f7whUzdTLa9OKbOpCW6x3ScoQv5kfLN0I9Wy2X3wNPV1F8hOBbJjAfIXz6vdfvApocv/apS/6N1/kL8wLzGt6NeQv3+8jNnbqJaXpe90qoLboaNnZC//ihMremRDVtjLoe5C88RxkL8fvJoNe0+H356In637I7pIkB7y99kiuADyF8/LWrSDanm165ZFVXBbtnan7OV//uJ16s9cC7cdlkXdhXZfZ0H+fvB+/5dP2kH+JfLXiEoAeP2EDZC/8LA4XNGQv3je7JW7qZZX6TMs6YNbyujlspY/GUvX7KBeNuuK9sui7kJ8vxmQv0je520H74f8S+TP9fsRTgDYB+vYs38D5C88TLYtOqvddRXyF8dbkrefank1MGdQFdxIQvLgwUPZyp+MPkMWUS+b1QW7ZVF3oZt9DuQvkvevzxOGQP5en0ex3X4jBUv/sw/Wsmf/el5vYchf6CqA050B+Yvj5TLfUSsvUg2OxuBGCujIVf43bt721jSgXTbkKoUcii71HjQX8hfBqxs78naN51/6CGvavD7X8hMAX5lCNV4CoIf8fY/4VPdfIX9xPGbbMWrldeXaLSqD27SFhbKUPxlrC/fJQjZzV2yWRdGllPRFkL+I53/YzLYc8vdeya/GSwA0vu4RaHkJQHXIXzzPPGDNNsjfN2/73tPUyuv781epDG6dU+bIUv5kODJXykI2k+eul0XRJa5UNeQvfPA7/6lU/pzDuQQgUujSv4bNELgEQAf5+8eL67/sK8jf9/MPHj1PrbyOnrxAZXAj6xKuVVCrnmb53733wNM8cawsZDNuxhpZFF3KmJoD+fs4Pm835Ai391+lPuKu3nMJQJSQ/CPY7KAq734B5O8nr2Fsn1+bktfcgvyFj9Nnr1Irr72HzlAb3NYVHZCV/Mko2n5YNrJJz8qWRdElcqUC8hc+/l3nq3SV+8jASwC0vhb98ROAKNFVgiD/Mjxjcs5UyF/4uHLtB2rlta1Uu1W6gtuIrFxZyZ88b9iElbKRzeBxy2VRcXHBqi2Qv8BRJyb93rO/+kNtlfuISwB0gj5nnxTB2yMI+VeCZ3Tkvw35Cx/37j+gVl6FWw9RG9xIgSI5yZ8wWncaIxvZkC6Qcqi4uGr9Lshf4PikuS0bPvL+7+piC/5EsGsAIP8g8MxO9zrIv/wjcRBDtbzyNuynOriRNQpykD95/uad38lKNskjl8qi4uL6jQcgf8HKf5/GwEcid+/xEgDIP0g8q9NVF/Iv/+g+nKFaXivyvqU6uC3I3ioL+RPO2Bm5spINKVYkh4qLm3cehfwrOvtv49wEH/nBC1T8kH/FPJvN82Org9kP+Zfl9Umne6vV7KUM1cGSFIGRg/zJEddjoqxk080xTxbllknXQsi/fN5f32/aBz5Ci2DJefF2txHyL8sbMLaAanlNnruO6mDZxJruuXzlKvXy33fwhOxkk5g0Sxbllo+cuAD5l8P7PNp5pGb9L56BjyB/yXnRtnyt2cmch/xL8wZPcuOydSV5zKa91K9Wn7HQLTvZmHpPk0W55bMXrkH+5fDe/TR2CHwE+VPDszrd/SH/0rxRMxiq5TVi0krqg+WYGWuoX63eJWW27GTD32VBc8XFazduQ/5P8T5vO/jii7/57b/hI8ifni6BQ/J/WizB25D/E96keZuollda5jLqg2WCbQbV8j9/6ZqngVl+smnRcbwsyi3fv/8A8n+K936djlnwEeRPHc/qYDIh/ye8udm7qZZXyqhl1AdLItcLl29Qu2Bted5OWcqmkTVTNr0WmsSPgfxZRp32w27/6qU/NIKPIH/6ugSmMC9bUwvuQf6PecvXHaB6q1XfoYtkESxzXHuoXbDWb9hi2crmwYOHsii33KbrJMifPWrW7zIbPvKbWQWTEyaeMTl7AuT/mJdfdJjqrVbdHHNlESwHjcumcv5u3rrjPZOWq2xu/XBXFuWWLX2nQ/7FR932Q2798uU/NYKPxIufrfsjukiQHvKvHK9lh9F/NiavvYMugYxn484TVG+1SrDNlEWwbNV5oufRo0fUzd+6ov2yls3lq7dkUW65S+oc1cufHP9t0HkafOSX/DWiEgBeP2ED5F95XpxtVQa6BDKeXQfOUL3VKrbHFNkEywNHzlI3f2ljV8laNt+fvyqLXgt9Bi9Uvfzrth98/ac/fakWfCRa/ly/H+EEgH2wjj37N0D+lee1/GrE76yOgltqbxR0+MRFqrdateo0QTbBcvayTVTNH2ny1DxxnKxlc+zURVn0WhgwcpGq5U+O/9TrNB4+Ei3/KLbbb6Rg6X/2wVr27F/P6y0M+VeSZ3W609TeJfDshetUb7VqXGZ1Nb3BssfA+VTNn7ga9XTLZv/h72XRa2HQ2OWqln/d9sMu13j+5zXhI1E8LXuUJAC+MoVqvARAD/kHh5fg2Pi81c5cV3OjoBs371Ar/4r3V9MZLBtZMkstWpN6/kZNzZO9bDbt+E4WvRZGTclWrfzJz9+r23k0fCSKp2N9ziUAGl/3CLS8BKA65B9cntXpHqBW+cenMRUuXKPhsuuNm/KrsFa47TAV80c+1uhuWbKXjXvTXlk0Wpo4O0+18v+83YgL+mdffA8+ErWGrzovAYgUuvSvYTMELgHQQf7B5yXaigxWu+ucGhsFdR5WRHWRlfOXrssuWGZMz6di/vYeOqMI2axldlEvf3LMXOxWpfzJ///Pz6yD4CNRu/f0vAQgSkj+EWx2UJV3vwDyDxHP4nTHqbFLYJ+MLVQXWTlx5pLsguWXHcd6Og2Y4emUzDuK/901dY6nq32u/0fx8wLhxfWaqgjZrMrfTr38yb8Dq7Yof/nXbjP4YFSNGr+Fj3zyDLwEQOtr0R8/AYgSXSUIkx0Qr+ncuRFmJ7NdbY2C7JN2UF1k5eDRsyivqnLekpzN1Muf/Dx/w35Vfr6vv9ukA3wkisclADpBn7NPiuDtEYT8w8CLdzL/VVuXwGEzd1FdZGXnvpOQocp5i3K2US9/Mop2HFHd51vry5Q8+EM0zyBqDR8vAdBA/uHlWZyueWpqFNRz1GbPyGkbPGljVnrso5YUH4t5xxLvzweOXeX3ESxez0ELIEOV8xKTZkn2/fOH12vwQlV9vnWNo+6+9OrbTeEP0Ty9P+V+IyD/8PPMzg2/Nae676itUVCb7nMhG/DAA080r2aDHtPgjxDwAhU/Jjs4vLik7MFqbBTUttdCBDfwwAPPJ69u++EXajz/8w/gj9DyMDkS8Jq06f4rc8qa79XYKKhN93kBBg4ES/DAUwvv3VqmVPgD8lcsr32/he3U2iioba8lCJbggQdeubzP2qbt+MlPfvk8/AH5K5ZXs0GdGha7a5laGwW167McwRI88MArddSJSb/3ymv/aQV/QP6K5yWmFf3arz4BCts98PhKQAaCJXjggec9/lO/y3j4A/JXDc/qYOLV3CioXZ9lAkkAgiV44KmF93n7IYeqP/PMG/AH5K8ans3m+bHZ4WLUKP/SVwIQLMEDT628unGjHr72Vl0T/BE6+Yve/YfJDi/PbC94zep03VWj/Mu/HYBgCR54auJ92KTPHPgjZDyu9L/oIkF6THZ4eVanu79a5V9yO6DvCm8wQLAEDzz18Oq0H/Z9jed//iH8ETL5a0QlALx+wgZMdnh5TW27q5rtzG61yv9JxcB5xQFjBIIleOCphPfX91t2gz9CJn+u349wAsA+WMee/Rsw2eHnWZzM36x21z21yp/jtekxz1PfOBLBEjzwFM77uGn/xfBHyOQfxXb7jRQs/c8+WMue/et5vYUx2WHmWR1MNzXLnzva9lyAioHggadg3hdthxzTP/OL9+GPkPC07FGSAPjKFKrxEgA9JlsaXrt2EzSmpJz1apZ/6YqBGQiW4IGnNF7sqPt//NtnMfBHSHg61udcAqDxdY9Ay0sAqmOypeW17DD6z8bkNVfULH/+wsAG5kwEX/DAUxDv3/U6ZSLeh4THOZxLACKFLv1r2AyBSwB0mGw6eDF9F7ZRu/y5I7r3UhFJAIIveODJgfdZG8dWvf4XLyDeB53HXb3nEoAoIflHsNlBVd79Akw2RTyLwzVJ7fIXlwQg+IIHnhx49WKHX/vF7/7WCPE+JDwDLwHQ+lr0x08AokRXCcJkh40Xb8vXm52u79Quf+HbAQi+4IEnF97fP2jXF/E+ZDwuAdAJ+px9UgRvjyDkTynPNND9lmCVQJXVDSh9JQDBFzzw5ML7qFm/JYj3IeUZRK3h4yUAGsiffp7F6Y6D/JlSrYRJEoDgCx548uB9Fj14b7WfPPcu4n1IeXp/yv1GQP7y4VntzATI/wmvbY/5JcWCEHzBA49e3hexI6/86pW3GiPeU8ILVPyYbOl40bZ8rdXBbIb8UTEQPPDkwiNd/t74d7NOiPdoEQxeJXmmNNdLVjtzAfLnVQzstciPOgEI5uCBF07ef+p1zUS8h/zBCxIv3s58ZHa6HkL+T3iPFwaOQfAFDzyKeJ+0SM3/kcdTBfEe8gcviDyz3dUT8i/N8y8JQDAHD7xQ8r5oP+Rojede+hjxHvIHL8i8mg3q1DAmZy+G/MurEzAGwRw88CTk1YsdefOV199vjXgP+YMXIl7Dll+/aByQuxnyf3qL4DKBJADBHDzwQsmrY0x/8Ma/mnZGvIf8wQsxr+VXI35ncbiPQP5lrwQ0tIxBMAcPvDDz3q5ldiI+0yl/0bv/MNny4ZnszJ/MduYy5F9excAxCObggRcm3vsNe0xBfKaSx5X+F10kSI/Jlg8v3sn8F+WCy08CGlpQMRA88ELN+6hF8mqy4h/xmUr5a0QlALx+wgZMtrx4FmdhS8i/LC+612JPA1M6gjl44IWIV6u1c3u1as+/hfhMpfy5fj/CCQD7YB179m/AZMuPVyy8PpB/WV7bnqRscDqCOXjgBZn3efshx5/9xe9qIz5TKf8otttvpGDpf/bBWvbsX8/rLYzJlhPP46lSbs8AFA0qTgIWem8HIJiDB15weHXajbj02z+80xzxmUqelj1KEgBfmUI1XgKgx2TLk9d07twIi5OZDfmX5T3uIoiKgeCBV2n5xw679vs3PopGfKaSp2N9ziUAGl/3CLS8BKA6JlvePNO4LZEWB7MU8i/LI3UCym4RhBzAA0/sUTdu5M0/vVknDvGZSh7ncC4BiBS69K9hMwQuAdBhspXBa9Flhi4uKTcf8i/La993ZXESMBbBHDzw/OTVM468/drbjRMQn6nkcVfvuQQgSkj+EWx2UJV3vwCTrSBe8/adf2kakFME+ZdXMXC5wJUAyAE88Mpc9o9Jv/eXf33ZGfGZWp6BlwBofS364ycAUaKrBGGyZcVrYkz5jXnAmm2Qf/llg8teCYAcwAOvvBK/b37QuhfiM9U8LgHQCfqcfVIEb48g5K9gntmW+4LV6doF+TM+bgdADuCBV/ae/6iH//gkJhnxlHqeQdQaPl4CoIH81cGLtW/4uV9JgIoWED6+EoCKgeCBV0b+MaMfvlvLlIp4Kgue3p9yvxGQv7p4CY6Nz1sdzGbIv/yKgQ3No4uD5AjIATzwyBE76v7fP2jXF/FUYbxAxY/Jlj8v0VZksNgZF+RfTsXAXgtLygZDDuCp+szfOOrum++3+hrxFC2CMdkK43UdvLq61cHkQP4VVQwkuwMyIAfwVFrkZ9QP//fPph0RTyF/TLZCedG2fG2xBJdA/mV57fut9DSyjoMcwFMd74vYETf+/I96FsRTyB+TrYKKgVaH6xvIv7yKgctFFAuCbMBTkvxHXnn1b5/GIJ5C/phslfDq2fpFGpNzJkP+ZXnt+q7wNLKO93E7ALIBTwHybzfs7Cuvv98a8RTyx2SrjFez/hfPGPsvS4b8GT/LBkM24CmgpW/0oAMvvvx6A8RTyB+TrWJebP+l7a2OgruQf9mywY/XBGRANuApilerpYOp8fzPayL+KV/+onf/YbLVy7PY3f+xOlyXIP+nrgR4FwZytwMgG/Dkz/uwab8FUTVqvIL4p3geV/pfdJEgPSZbvbwER8EfrA7mEORf3pqAsaWKBUE24MmOF5f+6L06XUYh/qlG/hpRCQCvn7ABk61uXqK94IVi6RVC/qV5bXst8jQ0Z6BiIHiy5NWNSb9Dqvsh/qlG/ly/H+EEgH2wjj37N2Cywes8tLCad5sg5F+K16734pIkALIBTy68OrHDL772dn0z4p9q5B/FdvuNFCz9zz5Yy57963m9hTHZaud5PFWK5dfFamceQP68ioG9FnlvB6BiIHhy4NWOTtv5y9/+rR7in2p4WvYoSQB8ZQrVeAmAHpMNHn+Yna6aVrvrHOT/VMXA+Al+JgGQF3jh5X3QuN88wwsvvIr4pxqejvU5lwBofN0j0PISgOqYbPDKG/EpeS+ZBqzZBPm7S9UJKLtFEPICT3pePePI229/HDcA8U9VPM7hXAIQKXTpX8NmCFwCoMNkgyfEa9Aq9mfGpOyJkD8qBoJHL++L6GGnf/+XT9oh/qmKx1295xKAKCH5R7DZQVXe/QJMNniieMb+y6zmVPcdFA16fMT0zxa4HQB5gRc+3metUgufe+G3nyJeqY5n4CUAWl+L/vgJQJToKkGYbPBYXnyq+69Wp2sfigbxrwSgYiB40vDqGNMf/Kde53HPP//HnyBeqZLHJQA6QZ+zT4rg7RGE/MELiGeybdFZHUwmigY9SQIal1wJgLzACw/v85hhJ/705hdGxCtV8wyi1vDxEgAN5A9eMHhWp6uu1c5cQNEgxhPTb5X3SgAqBoIXDt5Hzfoteeanv3gf8Ur1PHG793gJAOQPXtB48YM2/sLqcGWjaBBbMdCSiYqB4IWMVyd22LW/f9i+D+IVeH7xAhU/Jhs8X8Nm8/zY4mA6mu3MHdVXDOyzxNOITQIgL/CCyavVyrH5xd/9pSHiFXhoEQwedbwEZ+EbZod7u9qLBkX3WuxHnQDIEDxhXl3jqLvv1e08+tlnf1cD8Qo8yB88anl1W8Y9F9d/ha1YhLdVXTGw70rvwsAG5kzIELyAebXbOLe+/Kf3vkR8AQ/yB082vNbdst40Ja0pUHPRIFInoLHossGQIXi8oj6x6dffrWVNI305EF/Ag/zBkx3vL7a+EVa7K9aa6rqq1roB3rLBPq8EQIbg8e71f5mSxzXxQXwBD/IHT9Y8Y+r6F612Zr5qKwb2W+VpnDCxgiQAMgSPXeEfM/T8mx+07oX4Ah7kD57y6gbYmQbWVOa4GusGeOsElLkdABmCN9pTN2b0w4+a9V/43HOvfIz4Al4w5S969x8mG7xw8DoPLaxmcTD9rM6CW2qrG+BdGFhyJQAyBO/x1r7fv/FRNOILeEHmcaX/RRcJ0mOywQsXLzGt6NdmBzNddRUDbas9TYqTgPrGkZChinm12w8+9WbNtr0rWuSH+AJeJeWvEZUA8PoJGzDZ4IWbZ7bn/cs8IGeLmuoGkDoBpGIgPwmAXNXBqxs38uZ/6nXN1NX46d8RD8ALkfy5fj/CCQD7YB179m/AZIMnBe/zz5s+G9t3iTkuac33aqkbEN17kaexdYw3CYBcVcCLS3/0YTPb8p/95o16iAfghVD+UWy330jB0v/sg7Xs2b+e11sYkw2eJLym0b1ftNjX9zalMpfVUDegXd9lnsYJ/hYLglzlxqvV2uF+9W+fxiAegBdinpY9ShIAX5lCNV4CoMdkg0cDz5S2pUaxNJNMzoJriq8Y2G+lwBZByFXOvFqt7Rtfe6uuCfEAvDDwdKzPuQRA4+segZaXAFTHZINHGy92aOFzFifjsKS6byq6YiBZGNghS2QSALnSzqvdasCO/327cQfEA/DCxOMcziUAkUKX/jVshsAlADpMNng08yyDmZ8VC3NIsSxvK7ZiYD8xvQMgV5p5n7VO2fvX95r0wN8veGHkcVfvuQQgSkj+EWx2UJV3vwCTDZ4seKSioMXJDLWmMteVuHWQJAGPrwSMgVxlxPu0derON2s271uzQZ0a+PsFL8w8Ay8B0Ppa9MdPAKJEVwnCZINHES/GlvOs0bayjzll9RmlbR2MLfd2AGRNG69uu+EPP2nWN//1f3yeiL9f8CTkcQmATtDn7JMieHsEIX/wZM2r3cTyQmy/xSZz0ppdiqoYWLIwcAxkTRmvTmz6Dx827r7wd39+tw3+fsGjgGcQtYaPlwBoIH/wlMQjXQfj7cxHFqd7lWIqBvZb5WmSOMlT35heLKwRkLXEvLrth194r37nsb966Q/18PcLHkU8cbv3eAkA5A+eYnkWO/N6sUBHmZ3MFblvHWzXZ2lJsSDIWhrep20Hbnv747gBz/3yt/+DvzfwZMsLVPyYbPDkyCNNh6xOd2uL3bVezlsH2/Ve7GkcP9Z7JSAwEUL+/vLqxgy7/H6DnjNf/tN7X+LvDTyl8TA54KmKZxno/qPF6R5sdjLn5bh7oH3fZd7bAY/XBGRA1qHgxaU/qtXSWfT3j2P7PPvL//kN/t7Ag/wx2eApiNfgqwXauD5L2hgHrM6NS1l7X067B7xrAhL8TQIgf1+8L6KHnf5vg+6Tf/2Htxvg7w08yB+TDZ4KeC0sg16JtS3rYE4tWGNyFjyURcXA/tmepomTPQ0tYpIAyL8iXp32w76v2aTXrD//vW5sRe148fcGHuSPyQZPBTy20qDFamfyrakFj2jePeCtE5CY5eNKAOT/NK9OzNDzHzbpM+e1t+ubK5I+/j7Ag/wx2eCpmEeqDZodrg4kGTA5mfs0LiD03g7okFXBlQDIn+PVaT/izIdN+s7/33caxttsnh/j7wM8yB+TAx54oniJtiKD2VnY0OJkxltSXSdpWkBIGgiVvR2gbvnXaTf03qctbVvfq/PV6Fder9nK15k+/j7AU7r8Re/+w2SDB17FgxQbatdj2ttx/Vf0NSWtXm9Oyrkn9QJCsiaA3ztAjfKvHe0oPsvvufStD77s99Lv/u8dfJ/BA69U6X/RRYL0mGzwwBPHaxrd+0WLfX3dYmE7i2VcUKZTYbgqBnoXBhYnASZ1VAys3X7wqU9aJGX/u7Zl5O9f/08Mvs/ggVeu/DWiEgBeP2EDJhs88ALjNbXtrmpJc71rcTJdrXb3Qm/NgTAtIPTWCUgYV6pssCLkHzvq/udtB+75oHGv2WR//i9e/uvn+P6BB55P+XP9foQTAPbBOvbs34DJBg+8IPE8nirmgRt+b3G4oq1O93CL07XGmuq+ENKKgQljvVcC5FgxsF7syHtfRA859FGL5NXv1e8y5v/+1STxuV+8+hq+f+CB55f8o9huv5GCpf/ZB2vZs389r7cwJhs88ELAI/3iW3VM/0O7PnMbxNlW9DEmr55lTSnYZnUW3A3GGgLSO6BZxymehpaxVFcM/CJmxLlPW9s3vN+o1wxSZ//3b3wU/fxv/vhLfF/AA69SPC17lCQAvjKFarwEQI/JBg+88PNM47ZExjsKXzWnuT6Jt7uNFifjsDjds6wOZkNxcnDWn9sIsezuACkrBtYzjrj9RbTz+KctkzZ91KTXsvfqJkx854PWqX9+s47x5z//Y018X8ADL+g8HetzLgHQ+LpHoOUlANUx2eCBRyfPZNuis6Zt+LMlzVXbbF/Xzmhb0TsuadXQONuqycbknKXGAbkuc6p7tynV/T2pXfBki+DYoFUMrBc78iYpm/tZ9KC9n7Z2bCCX6j9s0nfufxt8PfGfn3cY+taHsf3//I96ll++8pfa5EoHPl/wwAsbj3M4lwBECl3617AZApcA6DDZ4IGnEJ7HUyVmoPsnCY6NzycMdP/S7NzwW9IMKcFZ+IZpoPstaxrzL6vd/YEljallSl1XJ7bXgrrtesyuHd3zmw/bdZv+XnT3GW/FOtb8PjGt6NekQqIpbUsNcoUCnwd44FHJ467ecwlAlJD8I9jsoCrvfgEmGzzwwAMPPPDkxzPwEgCtr0V//AQgSnSVIEw2eOCBBx544NHG4xIAnaDP2SdF8PYIQv7ggQceeOCBJ1+eQdQaPl4CoIH8wQMPPPDAA0/2PHG793gJAOQPHnjggQceeGrhBSp+TDZ44IEHHnjgKYOHyQEPPPDAAw88yB+TAx544IEHHniQPyYbPPDAAw888CB/TDZ44IEHHnjgQf7ggQceeOCBBx7kDx544IEHHnjg0Sh/0bv/MNnggQceeOCBpwgeV/pfdJEgPSYbPPDAAw888GQvf42oBIDXT9iAyQYPPPDAAw88Wcuf6/cjnACwD9axZ/8GTDZ44IEHHnjgyVb+UWy330jB0v/sg7Xs2b+e11sYkw0eeOCBBx548uJp2aMkAfCVKVTjJQB6TDZ44IEHHnjgyY6nY33OJQAaX/cItLwEoDomGzzwwAMPPPBkx+McziUAkUKX/jVshsAlADpMNnjggQceeODJjsddvecSgCgh+Uew2UFV3v0CTDZ44IEHHnjgyY9n4CUAWl+L/vgJQJToKkGYbPDAAw888MCjjcclADpBn7NPiuDtEYT8wQMPPPDAA0++PIOoNXy8BEAD+YMHHnjggQee7Hnidu/xEgDIHzzwwAMPPPDUwgtU/Jhs8MADDzzwwFMGD5MDHnjggQceeJA/Jgc88MADDzzwIH9MNnjggQceeOBB/phs8MADDzzwwIP8wQMPPPDAAw88yB888MADDzzwwKNR/qJ3/2GywQMPPPDAA08RPK70v+giQXpMNnjggQceeODJXv4aUQkAr5+wAZMNHnjggQceeLKWP9fvRzgBYB+sY8/+DZhs8MADDzzwwJOt/KPYbr+RgqX/2Qdr2bN/Pa+3MCYbPPDAAw888OTF07JHSQLgK1OoxksA9Jhs8MADDzzwwJMdT8f6nEsANL7uEWh5CUB1TDZ44IEHHnjgyY7HOZxLACKFLv1r2AyBSwB0mGzwwAMPPPDAkx2Pu3rPJQBRQvKPYLODqrz7BZhs8MADDzzwwJMfz8BLALS+Fv3xE4Ao0VWCMNnggQceeOCBRxuPSwB0gj5nnxTB2yMI+YMHHnjggQeefHkGUWv4eAmABvIHDzzwwAMPPNnzxO3e4yUAkD944IEHHnjgqYUXqPgx2eCBBx544IGnDB4mBzzwwAMPPPAgf0wOeOCBBx544EH+pX85v0eAIQjlgsEDDzzwwAMPvDDyAvnl/B4B+iCUCwYPPPDAAw888MLIC+SX63j1hasHoVwweOCBBx544IEXRp6/v7wKr0dANV5zgSrggQceeOCBB548eBzTn18exesRoK1kuWDwwAMPPPDAA08aXoTYIkFVeD0CuCOykr8cPPDAAw888MALP08jKgHgPTiSd2iC8MvBAw888MADDzxpeKISgIinjx9VYoAHHnjggQceeFTwqvjKFn7MO6pU8peDBx544IEHHniU8P4ftdpkfJrXwgQAAAAASUVORK5CYII=")
    }
