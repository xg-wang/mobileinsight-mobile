import kivy
kivy.require('1.4.0')

from kivy.lang import Builder
import traceback
import logging
from logging import StreamHandler
from . import MobileInsightScreenBase

logger = logging.getLogger(__name__)
logger.addHandler(StreamHandler())

Builder.load_file('screens/demo.kv')

class DemoScreen(MobileInsightScreenBase):
    pass
