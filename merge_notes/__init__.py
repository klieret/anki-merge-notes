#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from anki.hooks import addHook
from .merge_notes import MergeNotes

mn = MergeNotes()
addHook('browser.setupMenus', mn.setup_menu)