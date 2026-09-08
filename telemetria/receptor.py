import socket
from f1 import packets
from almacenamiento.sesiones import guardar_vuelta

ultima_velocidad = 0
ultimo_tiempo = 0
tiempo = 0
acelerador = 0
freno = 0
posicion_x = 0
posicion_z = 0
distancia = 0
vuelta_actual = []

def iniciar_escucha_telemetria(cola_datos, puerto=20777):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", puerto))
    print(f"Escuchando datos de vuelta en el puerto {puerto}...")
    global ultima_velocidad, ultimo_tiempo, tiempo, acelerador, freno, vuelta_actual, posicion_x, posicion_z, distancia

    while True:
        data, direccion = sock.recvfrom(2048)
        paquete = packets.resolve(data)
        nombre_paquete = type(paquete).__name__

        if nombre_paquete == "PacketCarTelemetryData":
            mi_coche = paquete.header.player_car_index
            ultima_velocidad = paquete.car_telemetry_data[mi_coche].speed
            acelerador = paquete.car_telemetry_data[mi_coche].throttle * 100
            freno = paquete.car_telemetry_data[mi_coche].brake * 100

        elif nombre_paquete == "PacketLapData":
            mi_coche = paquete.header.player_car_index
            datos_mi_coche = paquete.lap_data[mi_coche]
            tiempo = datos_mi_coche.current_lap_time_in_ms
            distancia = datos_mi_coche.lap_distance

            if ultimo_tiempo is not None and tiempo < ultimo_tiempo and len(vuelta_actual) > 0:
                guardar_vuelta(vuelta_actual)
                vuelta_actual = []

            ultimo_tiempo = tiempo

        elif nombre_paquete == "PacketMotionData":
            mi_coche = paquete.header.player_car_index
            posicion_x = paquete.car_motion_data[mi_coche].world_position_x
            posicion_z = paquete.car_motion_data[mi_coche].world_position_z

            vuelta_actual.append({
                "distancia": distancia,
                "tiempo_ms": tiempo,
                "velocidad": ultima_velocidad,
                "acelerador": acelerador,
                "x": posicion_x,
                "z": posicion_z
            })

            cola_datos.put({
                "velocidad": ultima_velocidad,
                "tiempo_ms": tiempo,
                "distancia": distancia,
                "acelerador": acelerador,
                "freno": freno,
                "posicion_x": posicion_x,
                "posicion_z": posicion_z
            })