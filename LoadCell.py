import RPi.GPIO as GPIO
import time


class LoadCell:

    def __init__(self, dout, pd_sck):

        self.last_reading_bits = {}
        self.last_reading_int = None

        self.PD_SCK = pd_sck
        self.DOUT = dout

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

    def _micros(self, us):
        # Convert microseconds to seconds

        return us * 0.000001

    def _millis(self, ms):
        # Convert milliseconds to seconds

        return ms * 0.001

    def _bit_request(self):
        # Send the HX711 chip the sequence to request a bit of data

        GPIO.output(self.PD_SCK, True)
        time.sleep(self._micros(1))  # Delay for additional 1 microsecond before releasing output
        GPIO.output(self.PD_SCK, False)

    def _end_read(self):
        # Send the HX711 chip the sequence to complete a data bit request

        self._bit_request() # send the last bit to tell the HX711 what it should read next
        if not GPIO.input(self.DOUT):
            # IMPROVE: Need to raise an error here. DOUT should go high when the 25th pulse is sent.
            pass

    def _cell_ready(self):
        return not GPIO.input(self.DOUT) and not GPIO.input(self.PD_SCK)

    def _cell_read(self):
        # Reads the bits of data from the HX711 chip

        while not self._cell_ready():  # Wait for the HX711 chip to be ready
            # IMPROVE: Need to add a timeout here and raise an error if timeout is reached
            pass

        outbits = []
        time.sleep(self._micros(1))  # Wait 1 microsecond before the first pulse

        for i in range(24):
            self._bit_request()
            outbits.append(GPIO.input(self.DOUT))
            time.sleep(self._micros(1))  # Delay for additional 1 microsecond before finishing

        self._end_read()  # End the read

        return outbits

    def _cell_start_up(self):
        # Starts the HX711 chip up and gives it time to stabilize

        GPIO.output(self.PD_SCK, False)
        time.sleep(self._millis(400))  # Give the HX711 time to stabilize

    def _cell_shut_down(self):
        # Shuts the HX711 chip down so that it enters power saving mode

        GPIO.output(self.PD_SCK, True)
        time.sleep(self._micros(60))

    def _cell_read_once(self):
        # Reads the HX711 chip once and then shuts it down

        self._cell_start_up()

        output = self._cell_read()

        self._cell_shut_down()

        return output

    def _cell_read_multiple(self, qty):
        # Reads the HX711 chip multiple times and then shuts it down

        output = []

        self._cell_start_up()

        for i in range(qty):
            output.append(self._cell_read())

        self._cell_shut_down()

        return output

    def _msb_bits_to_int(self, bitdata):
        # Convert a 24 bit numb

        base = 2 ** len(bitdata)
        num = 0

        for bit in bitdata:
            num = num + (base * int(bit))
            base = base // 2

        return num

    def cell_read_int_once(self):
        # Reads the scale once and returns an integer

        return self._msb_bits_to_int(self._cell_read_once())

    def cell_read_int_multiple(self):
        # Reads scale multiple times and returns a list of integers

        output = []

        for reading in self._cell_read_once():
            output.append(self._msb_bits_to_int(reading))

        return output

    def _int_to_value(self, num):
        pass
