from machine import Pin
import dht

import config

MAX_LECTURAS = 5

sensor_clima = dht.DHT22(Pin(config.PIN_DHT22))
historial_temp = []


def guardar_temperatura(temp):
    historial_temp.append(temp)
    if len(historial_temp) > MAX_LECTURAS:
        historial_temp.pop(0)


def promedio_temperatura():
    return sum(historial_temp) / len(historial_temp)


def leer_clima():
    try:
        sensor_clima.measure()
    except OSError:
        return 0.0, 0.0, 0.0

    temp = sensor_clima.temperature()
    hum = sensor_clima.humidity()
    guardar_temperatura(temp)

    return round(temp, 1), round(promedio_temperatura(), 1), round(hum, 1)
