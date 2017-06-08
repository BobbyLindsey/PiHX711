import RPi.GPIO as GPIO
import time
import sys
from hx71131 import HX711
import smtplib
from email.mime.text import MIMEText

def cleanandexit():
    print("Cleaning...")
    GPIO.cleanup()
    print("Bye!")
    sys.exit()

hx = HX711(5, 6)

hx.set_reading_format("LSB", "MSB")

hx.set_reference_unit(92)

hx.reset()
hx.tare()

while True:
    try:
        val = hx.get_weight(10)
        print(val)

        hx.power_down()
        hx.power_up()
        time.sleep(0)

    except (KeyboardInterrupt, SystemExit):
        cleanandexit()

msg = MIMEText()

msg['Subject'] = 'The contents of %s' % textfile
msg['From'] = 'FitBowl@358.io'
msg['To'] = '2709991567@tmomail.net'

# Send the message via our own SMTP server.
s = smtplib.SMTP('localhost')
s.send_message(msg)
s.quit()