#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import QAction, SIGNAL
from anki.utils import stripHTML
from .log import logger
from collections import defaultdict


class MergeNotes():
    def __init__(self):
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

        self.dry = False
        self.strip_html = True
        self.strip_html_permanently = True

        self.tag_from = u"MERGE_FROM"
        self.tag_to = u"MERGE_TO"
        self.tag_was_merged_from = u"WAS_MERGED_FROM"
        self.tag_was_merged_to = u"WAS_MERGED_TO"
        self.match_field = u"Expression"

    def setup_menu(self, browser):
        """ Adds a menu item to Anki's browser. Will be called via hook.
        :param browser:
        :return:
        """
        logger.debug("Setting up menu.")
        a = QAction("Merge Notes", browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"),
                        lambda loop: self.loop(self.strip_html,
                                               self.strip_html_permanently,
                                               self.dry))

    def loop(self, strip_html, permanently_strip_html, dry):
        nids_from = mw.col.findNotes(u'tag:"{}"'.format(self.tag_from))
        nids_to = mw.col.findNotes(u'tag:"{}"'.format(self.tag_to))

        logger.debug("Found {} notes with tag_from {}".format(len(nids_from),
                                                              self.tag_from))

        logger.debug("Found {} notes with tag_to {}".format(len(nids_to),
                                                              self.tag_to))

        if permanently_strip_html:
            logger.debug("Stripping HTML from match field from all notes")
            for nid in nids_from + nids_to:
                note = mw.col.getNote(nid)
                old = note[self.match_field]
                new = stripHTML(note[self.match_field]).strip()
                if not old == new:
                    logger.debug(u"Changed match field from {} to {}".format(
                        old, new))
                    note[self.match_field] = new
                    note.flush()

        logger.debug("looping to build db")

        nids_from_dict = defaultdict(list)
        nids_to_dict = defaultdict(list)

        for nid in nids_from:
            note = mw.col.getNote(nid)
            expr = note["Expression"]
            if strip_html:
                expr = strip_html(expr).strip()
            nids_from_dict[expr].append(nid)

        for nid in nids_to:
            note = mw.col.getNote(nid)
            expr = note["Expression"]
            if strip_html:
                expr = strip_html(expr).strip()
            nids_to_dict[expr].append(nid)

        ok = []
        zero_from = []      # nothing to update, that's ok
        zero_to = []        # bad, don't have a candidate to merge into
        many_from = []      # bad
        many_to = []        # bad, too many candidates to merge into
        # todo: check if has tags was_merged_from/to and exclude those

        for expr in nids_to_dict.keys() + nids_from_dict.keys():
            num_from = len(nids_from_dict[expr])
            num_to = len(nids_to_dict[expr])
            if num_from == 0:
                zero_from.append(expr)
            elif num_from >= 2:
                many_from.append(expr)

            if num_to == 0:
                zero_to.append(expr)
            elif num_to >= 2:
                many_to.append(expr)

            if num_from == 1 and num_to == 1:
                ok.append(expr)

        # remove duplicates
        ok = list(set(ok))
        zero_from = list(set(zero_from))
        zero_to = list(set(zero_to))
        many_from = list(set(many_from))
        many_to = list(set(many_to))

        logger.debug(u"Statistics: \n"
                     u"ok: {}\n"
                     u"zero_from: {}\n"
                     u"zero_to: {}\n"
                     u"many_from: {}\n"
                     u"many_to: {}\n".format(u', '.join(ok),
                                             u', '.join(zero_from),
                                             u', '.join(zero_to),
                                             u', '.join(many_from),
                                             u', '.join(many_to)))

        if dry:
            return

        for expr in ok:
            note_from = mw.col.getNote(nids_from_dict[expr][0])
            note_to = mw.col.getNote(nids_to_dict[expr][0])
            self.merge_notes(note_from, note_to)
            self.merge_tags(note_from, note_to)

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
        logger.debug(note_from[self.match_field]+"before"+ str(type(note_from.tags))+ str(list(note_from.tags))+ str(list(note_to.tags)))
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
        for tag in [self.tag_from, self.tag_to]:
            if tag in new_tags_to:
                new_tags_to.remove(tag)
        new_tags_to.append(self.tag_was_merged_to)
        note_to.tags = list(set(new_tags_to))
        note_to.flush()

        new_tags_from = note_from.tags
        for tag in [self.tag_from]:
            if tag in new_tags_from:
                new_tags_from.remove(tag)
        new_tags_from.append(self.tag_was_merged_from)
        note_from.tags = list(set(new_tags_from))
        note_from.flush()

        logger.debug(note_from[self.match_field]+"after"+ str(type(note_from.tags))+ str(list(note_from.tags))+ str(list(note_to.tags)))

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
