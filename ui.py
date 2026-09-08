import customtkinter
import queue
import threading
import tkinter as tk
from main import iniciar_escucha_telemetria

cola_datos = queue.Queue()

root = customtkinter.CTk()
root.title("Telemetria F1 - Mapa del Circuito")
root.geometry("850x500")

# Panel izquierdo (Datos)
frame_datos = customtkinter.CTkFrame(root, width=300)
frame_datos.pack(side="left", fill="both", expand=False, padx=10, pady=10)

lbl_velocidad = customtkinter.CTkLabel(frame_datos, text="Velocidad 0 km/h", font=("Arial", 16))
lbl_velocidad.pack(pady=10)

lbl_tiempo = customtkinter.CTkLabel(frame_datos, text="Tiempo vuelta: 0 ms", font=("Arial", 16))
lbl_tiempo.pack(pady=10)

lbl_distancia = customtkinter.CTkLabel(frame_datos, text="Distancia 0 m", font=("Arial", 16))
lbl_distancia.pack(pady=10)

bar_acelerador = customtkinter.CTkProgressBar(frame_datos, width=200, height=15, progress_color="green")
bar_acelerador.set(0)
bar_acelerador.pack(pady=5)

bar_freno = customtkinter.CTkProgressBar(frame_datos, width=200, height=15, progress_color="red")
bar_freno.set(0)
bar_freno.pack(pady=5)

# Panel derecho (Canvas para el mapa)
canvas_mapa = tk.Canvas(root, bg="#1a1a1a", highlightthickness=0)
canvas_mapa.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Variables para dibujar y escalar la pista
puntos_pista = []
min_x, max_x = float("inf"), float("-inf")
min_z, max_z = float("inf"), float("-inf")
punto_coche = None

def transformar_coordenadas(x, z, width, height):
    """ Escala las coordenadas del juego (x, z) a los píxeles del Canvas """
    global min_x, max_x, min_z, max_z
    
    # Evita división por cero durante los primeros puntos
    range_x = (max_x - min_x) if (max_x - min_x) > 0 else 1
    range_z = (max_z - min_z) if (max_z - min_z) > 0 else 1

    padding = 30
    px = padding + ((x - min_x) / range_x) * (width - 2 * padding)
    # Se invierte Z para corregir la orientación del mapa en pantalla
    py = height - (padding + ((z - min_z) / range_z) * (height - 2 * padding))
    return px, py

def actualizar_ui():
    global min_x, max_x, min_z, max_z, punto_coche

    while not cola_datos.empty():
        datos = cola_datos.get()

        lbl_velocidad.configure(text=f"Velocidad: {int(datos['velocidad'])} km/h")
        lbl_tiempo.configure(text=f"Tiempo vuelta: {datos['tiempo_ms']} ms")
        lbl_distancia.configure(text=f"Distancia: {datos['distancia']:.1f} m")
        bar_acelerador.set(datos['acelerador'] / 100.0)
        bar_freno.set(datos['freno'] / 100.0)

        x = datos["posicion_x"]
        z = datos["posicion_z"]

        if x != 0 and z != 0:
            # Actualizar bordes máximos del circuito
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_z = min(min_z, z)
            max_z = max(max_z, z)

            puntos_pista.append((x, z))

            w = canvas_mapa.winfo_width()
            h = canvas_mapa.winfo_height()

            # Dibujar la trazada del circuito si hay suficientes puntos
            if len(puntos_pista) > 1 and w > 10:
                canvas_mapa.delete("pista")
                puntos_pantalla = []
                for px, pz in puntos_pista:
                    cx, cy = transformar_coordenadas(px, pz, w, h)
                    puntos_pantalla.extend([cx, cy])

                if len(puntos_pantalla) >= 4:
                    canvas_mapa.create_line(puntos_pantalla, fill="#555555", width=3, tags="pista")

            # Dibujar o mover el indicador del coche (círculo rojo)
            cx, cy = transformar_coordenadas(x, z, w, h)
            r = 6  # radio del punto
            if punto_coche is None:
                punto_coche = canvas_mapa.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#FF1801", outline="white", width=2)
            else:
                canvas_mapa.coords(punto_coche, cx - r, cy - r, cx + r, cy + r)

    root.after(30, actualizar_ui)

hilo_red = threading.Thread(
    target=iniciar_escucha_telemetria, 
    args=(cola_datos,), 
    daemon=True
)
hilo_red.start()

actualizar_ui()
root.mainloop()