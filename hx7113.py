import RPi.GPIO as GPIO
import time
import numpy  # sudo apt-get python3-numpy


class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck
        self.DOUT = dout

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0
        self.REFERENCE_UNIT = 1  # Value returned that corresponds to your reference unit AFTER dividing by the SCALE.

        self.OFFSET = 1
        self.lastVal = 0

        self.LSByte = [2, -1, -1]
        self.MSByte = [0, 3, 1]

        self.MSBit = [0, 8, 1]
        self.LSBit = [7, -1, -1]

        self.byte_range_values = self.LSByte
        self.bit_range_values = self.MSBit

        self.set_gain(gain)

        time.sleep(1)

    def is_ready(self):  # Check to see if the HX711 is ready to be read
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        self.read()

    def createBoolList(self, size=8):  # Create a boolean array for storing bitwise data
        ret = []
        for i in range(size):
            ret.append(False)
        return ret

    def read(self):  # read the value from the HX711 and return as an array of 4 bytes
        while not self.is_ready():
            # print("WAITING")
            pass

        databits = [self.createBoolList(), self.createBoolList(), self.createBoolList()]
        databytes = [0x0] * 4

        for j in range(self.byte_range_values[0], self.byte_range_values[1], self.byte_range_values[2]):
            for i in range(self.bit_range_values[0], self.bit_range_values[1], self.bit_range_values[2]):
                GPIO.output(self.PD_SCK, True)  # Tell the HX711 to give you the next bit
                databits[j][i] = GPIO.input(self.DOUT)  # Read the next bit
                GPIO.output(self.PD_SCK, False)  # Tell the HX711 that you're done reading that bit
            databytes[j] = numpy.packbits(numpy.uint8(databits[j]))

        # set channel and gain factor for next reading
        for i in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)

        # check for all 1
        # if all(item is True for item in databits[0]):
        #    return self.lastVal

        databytes[2] ^= 0x80
        print(databytes)

        return databytes

    def get_binary_string(self):
        binary_format = "{0:b}"
        np_arr8 = self.read_np_arr8()
        binary_string = ""
        for i in range(4):
            # binary_segment = binary_format.format(np_arr8[i])
            binary_segment = format(np_arr8[i], '#010b')
            binary_string += binary_segment + " "
        return binary_string

    def get_np_arr8_string(self):
        np_arr8 = self.read_np_arr8()
        np_arr8_string = "["
        comma = ", "
        for i in range(4):
            if i is 3:
                comma = ""
            np_arr8_string += str(np_arr8[i]) + comma
        np_arr8_string += "]"

        return np_arr8_string

    def read_np_arr8(self):
        dataBytes = self.read()
        np_arr8 = numpy.uint8(dataBytes)

        return np_arr8

    def read_int(self):
        np_arr8 = self.read_np_arr8()
        np_arr32 = np_arr8.view('uint32')
        self.lastVal = np_arr32

        return self.lastVal

    def read_average(self, times=3):
        values = []
        avg = 0
        for i in range(times):
            values.append(self.read_int())
        avg = numpy.average(values)
        print("Average:", avg)
        for value in values:
            print("Checking:", value)
            if (value > 2 * avg) or (value < int(avg/2)):
                print("Removing:", value)
                values.remove(value)
        return int(numpy.average(values))

    def get_value(self, times=3):
        return self.read_average(times) - self.OFFSET

    def get_weight(self, times=3):
        value = self.get_value(times)
        value = value / self.REFERENCE_UNIT
        return int(value)

    def tare(self, times=15):

        # Backup REFERENCE_UNIT value
        reference_unit = self.REFERENCE_UNIT
        self.set_reference_unit(1)

        value = self.read_average(times)
        self.set_offset(value)

        self.set_reference_unit(reference_unit)

    def set_reading_format(self, byte_format="LSB", bit_format="MSB"):
        if byte_format == "LSB":
            self.byte_range_values = self.LSByte
        elif byte_format == "MSB":
            self.byte_range_values = self.MSByte

        if bit_format == "LSB":
            self.bit_range_values = self.LSBit
        elif bit_format == "MSB":
            self.bit_range_values = self.MSBit

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_reference_unit(self, reference_unit):
        self.REFERENCE_UNIT = reference_unit

    # HX711 datasheet states that setting the PDA_CLOCK pin on high for >60 microseconds would power off the chip.
    # I used 75 microseconds, just in case.
    # I've found it is good practice to reset the hx711 if it wasn't used for more than a few seconds.
    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.000075)

    def reset(self):
        self.power_down()
        self.power_up()
