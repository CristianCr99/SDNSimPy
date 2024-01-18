import threading


# Clase run_process, encargada de recopilar las funciones para la parada, reanudacion y finalizacion de un hilo a partir
# del envio de seniales.
class run_process(threading.Thread):

    # Constructor por defecto de la clase run_process.
    def __init__(self, *args, **kwargs):
        super(run_process, self).__init__(*args, **kwargs)
        self.__flag = kwargs['args'][7]  # La bandera utilizada para pausar el hilo
        self.__flag.set()  # Fijar como verdadero
        self.__running = kwargs['args'][8]  # Se utiliza para detener la identificacion del hilo
        self.__running.set()

    # Funcion pause, encargada de poner en False la bandera para bloquear el hilo.
    def pause(self):
        self.__flag.clear()

    # Funcion resume, encargada de establecer a True la bandera para que el hilo deje de estar bloqueado.
    def resume(self):
        self.__flag.set()

    # Funcion stop, encargada de reanudar el hilo desde el estado de suspension, si ya esta suspendido.
    def stop(self):
        self.__flag.set()
        self.__running.clear()
