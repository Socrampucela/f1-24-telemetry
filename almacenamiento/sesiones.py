import json

def guardar_vuelta(vuelta_actual, ruta="vueltas.jsonl"):
    with open(ruta, "a") as archivo:
        archivo.write(json.dumps(vuelta_actual) + "\n")
    print(f"Vuelta guardada con {len(vuelta_actual)} puntos")