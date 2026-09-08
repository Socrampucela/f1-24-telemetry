import json
import matplotlib.pyplot as plt

def cargar_vueltas(nombre_archivo="vueltas.jsonl"):
    vueltas = []
    with open(nombre_archivo, "r") as archivo:
        for linea in archivo:
            vueltas.append(json.loads(linea))
    return vueltas

def punto_mas_cercano(vuelta, distancia_objetivo):
    return min(vuelta, key=lambda punto: abs(punto["distancia"] - distancia_objetivo))

def comparar_vueltas(vuelta_lenta, vuelta_rapida, paso_metros=50):
    distancia_maxima = min(vuelta_lenta[-1]["distancia"], vuelta_rapida[-1]["distancia"])
    distancia_actual = 0

    while distancia_actual < distancia_maxima:
        punto_lenta = punto_mas_cercano(vuelta_lenta, distancia_actual)
        punto_rapida = punto_mas_cercano(vuelta_rapida, distancia_actual)

        diferencia_tiempo = punto_lenta["tiempo_ms"] - punto_rapida["tiempo_ms"]
        diferencia_velocidad = punto_lenta["velocidad"] - punto_rapida["velocidad"]

        print(f"Distancia {distancia_actual:>5}m | Delta tiempo: {diferencia_tiempo:+5} ms | Delta velocidad: {diferencia_velocidad:+4} km/h")

        distancia_actual += paso_metros

vueltas = cargar_vueltas()
comparar_vueltas(vueltas[0], vueltas[1])




