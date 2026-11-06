from machine import Pin, PWM

ANGULO_MIN = 0
ANGULO_MAX = 180
DUTY_MIN = 26
DUTY_MAX = 128

led_rojo = Pin(2, Pin.OUT)
led_verde = Pin(4, Pin.OUT)
buzzer = Pin(5, Pin.OUT)
servo = PWM(Pin(18), freq=50)


def mover_ventana(angulo):
    angulo = max(ANGULO_MIN, min(angulo, ANGULO_MAX))
    duty = int(DUTY_MIN + (angulo / ANGULO_MAX) * (DUTY_MAX - DUTY_MIN))
    servo.duty(duty)
    return angulo


def actualizar_alertas(en_alerta):
    led_rojo.value(en_alerta)
    led_verde.value(not en_alerta)
    buzzer.value(en_alerta)
