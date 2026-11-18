from machine import Pin, PWM

import config

ANGULO_MIN = 0       # compuerta abierta
ANGULO_MAX = 145     # compuerta cerrada (el servo nunca pasa de aqui)
ESCALA_SERVO = 180   # el duty se calcula sobre 0-180 grados
DUTY_MIN = 26
DUTY_MAX = 128

led_rojo = Pin(config.PIN_LED_ROJO, Pin.OUT)
led_verde = Pin(config.PIN_LED_VERDE, Pin.OUT)
buzzer = Pin(config.PIN_BUZZER, Pin.OUT)
servo = PWM(Pin(config.PIN_SERVO), freq=50)
rele = Pin(config.PIN_RELE, Pin.OUT, value=0)


def mover_ventana(angulo):
    angulo = max(ANGULO_MIN, min(angulo, ANGULO_MAX))
    duty = int(DUTY_MIN + (angulo / ESCALA_SERVO) * (DUTY_MAX - DUTY_MIN))
    servo.duty(duty)
    return angulo


def encender_bombillo(encender):
    rele.value(1 if encender else 0)
    return bool(encender)


def actualizar_alertas(en_alerta):
    led_rojo.value(en_alerta)
    led_verde.value(not en_alerta)
    buzzer.value(en_alerta)
