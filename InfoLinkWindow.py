import tkinter as tk

# Clase InfoLinkWindow, encargada de mostrar la informacion relativa a un enlace mediante el uso de ventanas con la
# libreria tkinter.
class InfoLinkWindow(tk.Frame):

    # Constructor parametrizado de la clase InfoLinkWindow
    def __init__(self, root, link_data, src_dst):
        self.root = root
        self.link_data = link_data
        self.src_dst = src_dst

    # Funcion initialize_user_interface, encargada de inicializar la ventana en la que se mostrara la informacion
    # del enlace dado.
    def initialize_user_interface(self):

        self.root.title('[' + self.src_dst + '] link parameters')
        tk.Label(self.root, text="Bandwidth:").grid(row=1, column=0, sticky='w', padx=15, pady=5)
        tk.Label(self.root, text="Distance:").grid(row=2, column=0, sticky='w', padx=15, pady=5)
        tk.Label(self.root, text="Propagation Speed:").grid(row=3, column=0, sticky='w', padx=15, pady=5)
        tk.Label(self.root, text="Mbps").grid(row=1, column=2, sticky='w', padx=10, pady=5)
        tk.Label(self.root, text="m").grid(row=2, column=2, sticky='w', padx=10, pady=5)
        tk.Label(self.root, text="m/s").grid(row=3, column=2, sticky='w', padx=10, pady=5)

        if 'bw' in self.link_data:
            tk.Label(self.root, text=str(1 / float(self.link_data['bw']))).grid(row=1, column=1, sticky='w', padx=10,
                                                                                pady=5)
        if 'distance' in self.link_data:
            tk.Label(self.root, text=self.link_data['distance']).grid(row=2, column=1, sticky='w', padx=10, pady=5)
        if 'propagation_speed' in self.link_data:
            tk.Label(self.root, text=self.link_data['propagation_speed']).grid(row=3, column=1, sticky='w', padx=10,
                                                                               pady=5)
