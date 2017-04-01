import time
from abc import ABCMeta
import logging
import NeoPixel
from .baseplatform import BasePlatform

logger = logging.getLogger(__name__)

GPIO = None


class RPiLikePlatform(BasePlatform):
	__metaclass__ = ABCMeta

	def __init__(self, config, platform_name, p_GPIO):
		
		global GPIO
		GPIO = p_GPIO
		
		super(RPiLikePlatform, self).__init__(config, platform_name)

		self.button_pressed = False

	def setup(self):
		NeoPixel.setupNeoPixel()

	def indicate_failure(self):
		for _ in range(0, 5):
			time.sleep(.1)
			NeoPixel.errorRed()
			time.sleep(.1)
			NeoPixel.turnOff()

	def indicate_success(self):
		for _ in range(0, 5):
			NeoPixel.fadeIn(Color(0, 0, 255))
			time.sleep(.1)
			NeoPixel.fadeOut(Color(0, 0, 255))

	def after_setup(self, trigger_callback=None):

		self._trigger_callback = trigger_callback

		if self._trigger_callback:
			# threaded detection of button press
			GPIO.add_event_detect(self._pconfig['button'], GPIO.FALLING, callback=self.detect_button, bouncetime=100)

	def indicate_recording(self, state=True):
		if state is True:
			NeoPixel.fadeIn(Color(255, 0, 0))
		if state is False:
			NeoPixel.fadeOut(Color(255, 0, 0))

	def indicate_playback(self, state=True):
		if state is True:
			NeoPixel.fadeIn(Color(0, 255, 0))
		if state is False:
			NeoPixel.fadeOut(Color(0, 255, 0))

	def indicate_processing(self, state=True):
		if state is True:
			NeoPixel.fadeIn(Color(255,255, 0))
		if state is False:
			NeoPixel.fadeOut(Color(255,255, 0))

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
