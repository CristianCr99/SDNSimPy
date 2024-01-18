from os import path
from pathlib import Path

from scapy.layers.inet import *

# Clase Utilities, encargada de recopilar funciones generales empleadas en diversas clases.
class Utilities:

    # Funcion mac_address_check, encargada de comprobar si una direccion mac es correcta.
    def mac_address_check(self, mac_address):
        try:
            if re.match("[0-9a-f]{2}([:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_address.lower()):
                return True
            return False
        except:
            return False

    # Funcion ip_address_check, encargada de comprobar si una direccion ip es correcta.
    def ip_address_check(self, ip_address):
        try:
            if len(ip_address.split('.')) == 4:
                for i in ip_address.split('.'):
                    if not int(i) >= 0:
                        return False
                return True
            return False
        except:
            return False

    # Funcion port_check, encargada de comprobar si un puerto es correcto.
    def port_check(self, port):
        try:
            port_number = int(port)
            if 1 <= port_number <= 65535:
                return True
            return False
        except:
            return False

    # Funcion is_number_positive, encargada de comprobar si un numero es un numero y positivo.
    def is_number_positive(self, number):
        try:
            number = int(number)
            if number > 0:
                return True
            return False
        except:
            return False

    # Funcion calculate_jitter, encargada de calcular el jitter a partir de una lista de retardos.
    def calculate_jitter(self, list_delays):
        if len(list_delays) < 2:
            return 0.0
        sum = 0.0
        for i in range(0, len(list_delays)):
            sum += abs(list_delays[i - 1] - list_delays[i])
        return sum / (len(list_delays) - 1)

    # Funcion create_graph, encargada de crear los graficos.
    def create_graph(self, x=[], y=[], color='#526B84', markerfacecolor='#95A5A6', x_range_min=1,
                     x_label='', y_label='', title_graph='', path_image='./GraphsImages', name='', dpi=300,
                     bbox_inches='tight', is_delay=True):

        if is_delay:
            plt.figure(figsize=(10, 3.4))
            plt.plot(x, y, color=color, linestyle='dashed', linewidth=2,
                     marker='o', markerfacecolor=markerfacecolor, markersize=12)
            y_max = max(y)
            plt.ylim(0, y_max + 0.4 * y_max)
            try:
                plt.xlim(1, len(x))
            except:
                print('')
        else:
            plt.figure(figsize=(15, 3.3))

            plt.step(x, y, where='post')

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title_graph)

        if not path.exists(path_image):
            Path("./GraphsImages").mkdir(parents=True, exist_ok=True)

        if is_delay:
            text_pos_x = 0.2
            text_pos_y = - 0.07

            jitter = self.calculate_jitter(y)
            plt.text(text_pos_x, text_pos_y,
                     'Jitter: ' + str(round(jitter, 2)) + ' mms   Max Delay:' + str(
                         round(max(y), 2)) + ' ms   Min Delay:' + str(round(min(
                         y), 2)) + ' ms   Avg Delay: ' + str(round(sum(y) / len(y), 2)) + ' ms', fontsize=10,
                     transform=plt.gcf().transFigure)
        else:
            text_pos_x = 0.35
            text_pos_y = - 0.07

            plt.text(text_pos_x, text_pos_y, 'Max load:' + str(round(max(y), 2)) + ' Bytes   Min Load:' + str(round(min(
                y), 2)) + ' Bytes   Avg Load: ' + str(round(sum(y) / len(y), 2)) + ' Bytes', fontsize=10,
                     transform=plt.gcf().transFigure)

        plt.savefig(path_image + '/' + name, dpi=dpi, bbox_inches=bbox_inches)

        plt.clf()
