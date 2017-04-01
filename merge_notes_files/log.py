#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Sets up logging to collect debugging information. """

import logging
import os.path
import sys

logger = logging.getLogger('merge_notes_logging')
logger.setLevel(logging.DEBUG)

# todo: set level higher once we have everything working
sh_info = logging.StreamHandler(stream=sys.stdout)
sh_info.setLevel(logging.DEBUG)

# will be caught by anki and displayed in a pop-up window
sh_error = logging.StreamHandler(stream=sys.stderr)
sh_error.setLevel(logging.ERROR)

addon_dir = os.path.dirname(__file__)
log_path = os.path.join(addon_dir, 'merge_notes_logging.log')

logger.addHandler(sh_error)
logger.addHandler(sh_info)

logger.debug("Saving log to file %s" % os.path.abspath(log_path))
fh = logging.FileHandler(log_path, mode="w")
fh.setLevel(logging.DEBUG)

logger.addHandler(fh)
