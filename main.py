# Example Led on/ Led off program from raspberry pi foundation for Pico W that has been updated to show ip address on inky pack

from machine import Pin
from pimoroni import Button
from picounicorn import PicoUnicorn
from picographics import PicoGraphics, DISPLAY_UNICORN_PACK
from rainbow import uni_clear, rainbow
import network
import socket
import time
import uasyncio as asyncio
import WIFI_CONFIG


picounicorn = PicoUnicorn()
display = PicoGraphics(display=DISPLAY_UNICORN_PACK)
w = picounicorn.get_width()
h = picounicorn.get_height()

led = Pin("LED", Pin.OUT, value=0)


html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
    </body>
</html>
"""


def clear():
    for x in range(w):
        for y in range(h):
            picounicorn.set_pixel(x, y, 0, 0, 0)


ssid = WIFI_CONFIG.SSID
password = WIFI_CONFIG.PSK

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)


max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    clear()
    time.sleep(2)

if wlan.status() != 3:
    clear()
    time.sleep(0.5)
    raise RuntimeError('network connection failed')

else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    clear()
    time.sleep(0.5)

addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)
stateis = ""
print('listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print(request)

        request = str(request)
        print( 'request = ' + request)
        rainbow_on = request.find('/rainbow/on')
        rainbow_off = request.find('/rainbow/off')
        led_on = request.find('/led/on')
        led_off = request.find('/led/off')
        print( 'rainbow on = ' + str(rainbow_on))
        print( 'rainbow off = ' + str(rainbow_off))
        print( 'led on = ' + str(led_on))
        print( 'led off = ' + str(led_off))
        
        if rainbow_on == 6:
            print("rainbow on")
            rainbow()

        if rainbow_off == 6:
            print("rainbow off")
            uni_clear()

        if led_on == 6:
            print("led on")
            led.value(1)
            stateis = "LED is ON"
            time.sleep(0.5)

        if led_off == 6:
            print("led off")
            led.value(0)
            stateis = "LED is OFF"
            time.sleep(0.5)

        response = html % stateis

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
