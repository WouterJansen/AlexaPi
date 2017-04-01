import sys
import threading
import time
from abc import ABCMeta
import logging
from neopixel import *
from .baseplatform import BasePlatform


logger = logging.getLogger(__name__)
GPIO = None
strip = Adafruit_NeoPixel(12, 18, 800000, 5, False, 255)

def fadeIn(color):
    strip.setBrightness(0)
    strip.show()
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    for j in range(255):
        strip.setBrightness(j)
        strip.show()
        time.sleep(2 / 1000.0)


def fadeOut(color):
    strip.setBrightness(255)
    strip.show()
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    for j in range(255, -1, -1):
        strip.setBrightness(j)
        strip.show()
        time.sleep(2 / 1000.0)


def errorRed():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 255, 0))
    strip.show()


class SetupGreen(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.done = False

    def run(self):
        while not self.done:
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i + q, Color(255, 0, 0))
                strip.show()
                print "test"
                time.sleep(50 / 1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i + q, 0)
        turnOff()


def rotateBlue():
    for i in range(0, 11, 1):
        strip.setPixelColor(i, Color(0, 0, 255))
        if i + 1 > 11:
            strip.setPixelColor(i + 1 - 12, Color(0, 0, 160))
        else:
            strip.setPixelColor(i + 1, Color(0, 0, 160))
        if i + 2 > 11:
            strip.setPixelColor(i + 2 - 12, Color(0, 0, 100))
        else:
            strip.setPixelColor(i + 2, Color(0, 0, 100))
        if i + 3 > 11:
            strip.setPixelColor(i + 3 - 12, Color(0, 0, 50))
        else:
            strip.setPixelColor(i + 3, Color(0, 0, 50))
        if i + 4 > 11:
            strip.setPixelColor(i + 4 - 12, Color(0, 0, 100))
        else:
            strip.setPixelColor(i + 4, Color(0, 0, 100))
        if i + 5 > 11:
            strip.setPixelColor(i + 5 - 12, Color(0, 0, 160))
        else:
            strip.setPixelColor(i + 5, Color(0, 0, 160))
        if i + 6 > 11:
            strip.setPixelColor(i + 6 - 12, Color(0, 0, 255))
        else:
            strip.setPixelColor(i + 6, Color(0, 0, 255))
        if i + 7 > 11:
            strip.setPixelColor(i + 7 - 12, Color(0, 0, 160))
        else:
            strip.setPixelColor(i + 7, Color(0, 0, 160))
        if i + 8 > 11:
            strip.setPixelColor(i + 8 - 12, Color(0, 0, 100))
        else:
            strip.setPixelColor(i + 8, Color(0, 0, 100))
        if i + 9 > 11:
            strip.setPixelColor(i + 9 - 12, Color(0, 0, 50))
        else:
            strip.setPixelColor(i + 9, Color(0, 0, 50))
        if i + 10 > 11:
            strip.setPixelColor(i + 10 - 12, Color(0, 0, 100))
        else:
            strip.setPixelColor(i + 10, Color(0, 0, 100))
        if i + 11 > 11:
            strip.setPixelColor(i + 11 - 12, Color(0, 0, 160))
        else:
            strip.setPixelColor(i + 11, Color(0, 0, 160))
        strip.show()
        time.sleep(0.2)


def setupNeoPixel():
    strip.begin()
    

def turnOff():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
        strip.setBrightness(255)
    strip.show()


class RPiLikePlatform(BasePlatform):
	__metaclass__ = ABCMeta

	def __init__(self, config, platform_name, p_GPIO):
		
		global GPIO
		GPIO = p_GPIO
		
		super(RPiLikePlatform, self).__init__(config, platform_name)

		self.button_pressed = False

	def setup(self):
		logger.info("setting up NeoPixel")
		GPIO.setup(self._pconfig['button'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self._pconfig['rec_light'], GPIO.OUT)
		GPIO.setup(self._pconfig['plb_light'], GPIO.OUT)
		GPIO.output(self._pconfig['rec_light'], GPIO.LOW)
		GPIO.output(self._pconfig['plb_light'], GPIO.LOW)
		strip.begin()

	def indicate_failure(self):
		logger.info("failure")
		for _ in range(0, 5):
			time.sleep(.1)
			errorRed()
			time.sleep(.1)
			turnOff()

	def indicate_success(self):
		logger.info("success")
		for _ in range(0, 5):
			errorRed()
			time.sleep(.1)
			turnOff()

	def after_setup(self, trigger_callback=None):

		self._trigger_callback = trigger_callback

		if self._trigger_callback:
			# threaded detection of button press
			GPIO.add_event_detect(self._pconfig['button'], GPIO.FALLING, callback=self.detect_button, bouncetime=100)

	def indicate_recording(self, state=True):
		logger.info("recording")
		if state is True:
			errorRed()
		if state is False:
			turnOff()

	def indicate_playback(self, state=True):
		logger.info("playback")
		if state is True:
			errorRed()
		if state is False:
			turnOff()

	def indicate_processing(self, state=True):
		logger.info("processing")
		if state is True:
			errorRed()
		if state is False:
			turnOff()

	def detect_button(self, channel=None): # pylint: disable=unused-argument
		self.button_pressed = True

		self._trigger_callback(self.force_recording)

		logger.debug("Button pressed!")

		time.sleep(.5)  # time for the button input to settle down
		while GPIO.input(self._pconfig['button']) == 0:
			time.sleep(.1)

		logger.debug("Button released.")

		self.button_pressed = False

		time.sleep(.5)  # more time for the button to settle down

	# def wait_for_trigger(self):
	# 	# we wait for the button to be pressed
	# 	GPIO.wait_for_edge(self._pconfig['button'], GPIO.FALLING)

	def force_recording(self):
		return self.button_pressed

	def cleanup(self):
		GPIO.remove_event_detect(self._pconfig['button'])

		GPIO.output(self._pconfig['rec_light'], GPIO.LOW)
		GPIO.output(self._pconfig['plb_light'], GPIO.LOW)
