#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import QAction, SIGNAL
from anki.utils import stripHTML

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

class MergeNotes():
    def __init__(self):
        self.tag_from = u"merge_readings"
        self.tag_to = u"merge_koohii"
        self.match_field = u"Expression"

        self.merge_modes = {
            u'Note': "merge_ft",
            u'Kunyomi_story': "from",
            u'Keyword': "to",
            u'Heisig_index': "to",
            u'Image': "merge_ft",
            u'Other_meanings': "from",
            u'Audio': "merge_ft",
            u'Kunyomi': "from",
            u'Diagram': "to",
            u'Combined_story': "from",
            u'Examples': "from",
            u'Number_of_readings': "from",
            u'Kanji_story': "to",
            u'Onyomi_story': "from",
            u'Expression': "to",
            u'Signal': "from",
            u'Keyword_notes': "merge_ft",
            u'Onyomi': "from"
        }

    def setup_menu(self, browser):
        """ Adds a menu item to Anki's browser. Will be called via hook.
        :param browser:
        :return:
        """
        # todo: add option to only perform this on the selected notes
        a = QAction("Merge Notes", browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"), self.loop)

    def loop(self, max=10):
        nids_from = mw.col.findNotes(u'tag:"{}"'.format(self.tag_from))
        for nid_from in nids_from:
            note_from = mw.col.getNote(nid_from)
            nids_to = mw.col.findNotes(u'tag:"{}" "{}":"{}"'.format(
                self.tag_to, self.match_field, note_from[self.match_field]))

            if not len(nids_to) == 1:
                print u"SKIPPING {}".format(note_from[self.match_field])
            else:
                note_to = mw.col.getNote(nids_to[0])
                #print u"Merging {}".format(note_from[self.match_field])
                #self.merge_notes(note_from, note_to)
                #self.join_tags(note_from, note_to)
                # todo: uncomment something here to do sth

            #time.sleep(0.5)

    def join_tags(self, note_from, note_to):
        all_tags = list(set(note_from.tags) | set(note_to.tags))
        all_tags.remove("DELETE")
        all_tags.remove("merge_readings")
        note_to.tags = all_tags
        note_to.flush()

    def merge_notes(self, note_from, note_to):
        if not set(note_from.keys()) == set(note_to.keys()):
            raise ValueError, "not compatible notes"
        if not set(note_from.keys()) == set(self.merge_modes.keys()):
            raise ValueError, "merge_fields modes doesn't have the right keys"
        for key in self.merge_modes.keys():
            note_to[key] = self.merge_fields(note_from[key], note_to[key],
                                         self.merge_modes[key])
        note_to.flush()

    @staticmethod
    def merge_fields(field_from, field_to, merge_mode):
        if not stripHTML(field_from).strip():
            field_from = ""
        if not stripHTML(field_to).strip():
            field_to = ""
        if merge_mode == "from":
            return field_from
        elif merge_mode == "to":
            return field_to
        elif merge_mode == "merge_ft":
            if field_from and field_to:
                return field_from + "\n" + field_to
            else:
                return field_from + field_to
        elif merge_mode == "merge_tf":
            if field_from and field_to:
                return field_to + "\n" + field_from
            else:
                return field_to + field_from
        else:
            raise ValueError


