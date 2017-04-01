#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import QAction, SIGNAL
from anki.utils import stripHTML
from .log import logger
from collections import defaultdict

class MergeNotes():
    def __init__(self):
        self.tag_from = u"merge_readings"
        self.tag_to = u"merge_koohii"
        self.match_field = u"Expression"

        self.field_merge_modes = {
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

        self.tag_merge_mode = "merge"

    def setup_menu(self, browser):
        """ Adds a menu item to Anki's browser. Will be called via hook.
        :param browser:
        :return:
        """
        # todo: add option to only perform this on the selected notes
        logger.debug("Setting up menu.")
        a = QAction("Merge Notes", browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"), self.loop)

    def strip_html_match_field(self):
        nids_from = mw.col.findNotes(u'tag:"{}"'.format(self.tag_from))
        nids_to = mw.col.findNotes(u'tag:"{}"'.format(self.tag_from))
        nids = nids_from + nids_to
        logger.debug("Stripping HTML from field {} from {} from notes"
                     "and {} to notes".format(self.match_field,
                                              len(nids_from),
                                              len(nids_to)))
        for nid in nids:
            note = mw.col.getNote(nid)
            note[self.match_field] = stripHTML(note[self.match_field])

    def loop(self, strip_html=True, dry=False):
        nids_from = mw.col.findNotes(u'tag:"{}"'.format(self.tag_from))
        nids_to = mw.col.findNotes(u'tag:"{}"'.format(self.tag_from))

        logger.debug("Found {} notes with tag_from {}".format(len(nids_from),
                                                              self.tag_from))

        logger.debug("Found {} notes with tag_to {}".format(len(nids_to),
                                                              self.tag_to))

        if strip_html:
            logger.debug("Stripping HTML from field {} from all notes")
            for nid in nids_from + nids_to:
                note = mw.col.getNote(nid)
                note[self.match_field] = stripHTML(note[self.match_field])
                note.flush()

        logger.debug("looping to build db")

        nids_from_dict = defaultdict(list)
        nids_to_dict = defaultdict(list)


        for nid in nids_from:
            note = mw.col.getNote(nid)
            nids_from_dict[note["Expression"]].append(nid)

        for nid in nids_to:
            note = mw.col.getNote(nid)
            nids_to_dict[note["Expression"]].append(nid)

        ok = []
        zero_from = []      # nothing to update, that's ok
        zero_to = []        # bad, don't have a candidate to merge into
        many_from = []      # bad
        many_to = []        # bad, too many candidates to merge into

        for expr in nids_to_dict.keys() + nids_to_dict.keys():
            num_from = len(nids_from_dict[expr])
            num_to = len(nids_to_dict[expr])
            if num_from == 0:
                zero_from.append(expr)
            elif num_from >= 2:
                many_from.append(expr)

            if num_to == 0:
                zero_to.append(expr)
            elif num_to >=2:
                many_to.append(expr)

            if num_from == 1 and num_to == 1:
                ok.append(expr)

        logger.debug("Statistics: \n"
                     "ok: {}\n"
                     "zero_from: {}\n"
                     "zero_to: {}\n"
                     "many_from: {}\n"
                     "many_to: {}\n".format(ok, zero_from, zero_to, many_from,
                                            many_to))


        # for nid_from in nids_from:
        #     note_from = mw.col.getNote(nid_from)
        #     nids_to = mw.col.findNotes(u'tag:"{}" "{}":"{}"'.format(
        #         self.tag_to, self.match_field, note_from[self.match_field]))
        #
        #
        #     match_field = note_from[self.match_field]
        #
        #     if len(nids_to) == 0:
        #         zero.append(match_field)
        #     elif len(nids_to) >= 2:
        #         many.append(match_field)
        #     elif len(nids_to) == 1:
        #         ok.append(match_field)
        #         note_to = mw.col.getNote(nids_to[0])
        #         #self.merge_notes(note_from, note_to)
        #         #self.merge_tags(note_from, note_to)
        #         # todo: uncomment something here to do sth


    def merge_notes(self, note_from, note_to):
        if not set(note_from.keys()) == set(note_to.keys()):
            raise ValueError, "not compatible notes"
        if not set(note_from.keys()) == set(self.field_merge_modes.keys()):
            raise ValueError, "merge_fields modes doesn't have the right keys"
        for key in self.field_merge_modes.keys():
            note_to[key] = self.merge_fields(note_from[key], note_to[key],
                                             self.field_merge_modes[key])
        note_to.flush()

    def merge_tags(self, note_from, note_to):
        tags_from = note_from.tags
        tags_to = note_to.tags
        if self.tag_merge_mode == "merge":
            new_tags_to = list(set(tags_from) | set(tags_to))
        elif self.tag_merge_mode == "from":
            new_tags_to = tags_from
        elif self.tag_merge_mode == "to":
            new_tags_to = tags_to
        else:
            raise ValueError, "Invalid merge mode for tags"
        # IMPORTANT: do not copy the tag self.tag_from to the target note
        # also remove self.tag_to, so that we know which notes have been merged
        # and which have yet to be merged.
        new_tags_to.remove(self.tag_from)
        new_tags_to.remove(self.tag_to)
        note_to.tags = list(new_tags_to)

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
