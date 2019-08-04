#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import QAction, SIGNAL
from anki.utils import stripHTML
from .log import logger
from collections import defaultdict


class MergeNotes(object):
    def __init__(self):
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #                       BEGIN CONFIGURATION
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # --------------------- FIELD MERGE MODES -----------------------------

        # Merge modes for the field contents as a dictionary of the form
        #   ```field name (unicode string) : merge mode (string)```
        # where merge mode is one of the following 4 options
        # *  ```from``` (the field value of the to note will be that of the
        #    from note)
        # * ```to``` (the field value of the to note will be that of the to
        #    note, i.e. we do not change anything -- in this case you can also
        #    leave out the field)
        # * ```merge_ft``` (the field value of the to note will be
        #   field value of from note + line break + field value of to note
        # * ```merge_tf``` (the field value of the to note will be
        #   field value of to note + line break + field value of from note
        self.field_merge_modes = {
            u'Note': "merge_ft",
            u'Kunyomi': "from",
            u'Kanji_story': "to",
            u'Onyomi_story': "from",
            u'Expression': "to",
            u'Onyomi': "from"
        }

        # --------------------- TAG MERGE MODES -------------------------------

        # Mode to merge the tags of the from notes and to notes. Choose from
        # 3 modes:
        # *  ```from```
        # *  ```to```
        # *  ```merge```
        # With meaning as above.
        # Note that the special tags defined below will be set automatically.
        self.tag_merge_mode = "merge"

        # --------------------- MATCH CONTROL-- -------------------------------

        # Which field should be compared to find out which notes should be
        # merged together?
        self.match_field = u"Expression"

        # When comparing self.match_field, strip all HTML around the field
        # value (i.e. notes with match_field "<b>Test</b>" and "Test" are
        # still recognized to be merged
        self.strip_html = True
        # Permanently strip the html of the self.match_field
        self.strip_html_permanently = True

        # --------------------- RUN CONTROL-- -------------------------------

        # Dry run: Only compare notes and display which notes can be merged,
        # but do not do any merging
        self.dry = False

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #                       END CONFIGURATION
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # Those two tags controll which notes are from notes and which are
        # to notes. If a note either acted as a to_note or from_note, the
        # respective tag is replaced with the two tags below.
        self.tag_from = u"MERGE_FROM"
        self.tag_to = u"MERGE_TO"
        self.tag_was_merged_from = u"WAS_MERGED_FROM"
        self.tag_was_merged_to = u"WAS_MERGED_TO"

    def setup_menu(self, browser):
        """ Adds a menu item to Anki's browser. Will be called via hook.
        :param browser:
        :return:
        """
        logger.debug("Setting up menu.")
        a = QAction("Merge Notes", browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"), self.loop)

    def loop(self, *arsg, **kwargs):
        nids_from = mw.col.findNotes(u'tag:"{}"'.format(self.tag_from))
        nids_to = mw.col.findNotes(u'tag:"{}"'.format(self.tag_to))

        logger.debug("Found {} notes with tag_from {}".format(len(nids_from),
                                                              self.tag_from))

        logger.debug("Found {} notes with tag_to {}".format(len(nids_to),
                                                              self.tag_to))

        if self.strip_html_permanently and not self.dry:
            logger.debug("Stripping HTML from match field from all notes")
            for nid in nids_from + nids_to:
                note = mw.col.getNote(nid)
                old = note[self.match_field]
                if not isinstance(old, (str, unicode)):
                    continue
                new = stripHTML(old).strip()
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
            expr = note[self.match_field]
            if not isinstance(expr, (str, unicode)):
                continue
            if self.strip_html:
                expr = stripHTML(expr).strip()
            nids_from_dict[expr].append(nid)

        for nid in nids_to:
            note = mw.col.getNote(nid)
            expr = note[self.match_field]
            if not isinstance(expr, (str, unicode)):
                continue
            if self.strip_html:
                expr = stripHTML(expr).strip()
            nids_to_dict[expr].append(nid)

        ok = []
        zero_from = []      # nothing to update, that's ok
        zero_to = []        # bad, don't have a candidate to merge into
        many_from = []      # bad
        many_to = []        # bad, too many candidates to merge into
        # todo: check if has tags was_merged_from/to and exclude those

        for expr in list(nids_to_dict.keys()) + list(nids_from_dict.keys()):
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

        if self.dry:
            return

        for expr in ok:
            note_from = mw.col.getNote(nids_from_dict[expr][0])
            note_to = mw.col.getNote(nids_to_dict[expr][0])
            self.merge_notes(note_from, note_to)
            self.merge_tags(note_from, note_to)

    def merge_notes(self, note_from, note_to):
        missing_to = [
            key for key in self.field_merge_modes if not key in note_to
        ]
        if missing_to:
            msg = "note_to fields are missing key(s) {}".format(
                ", ".join(missing_to)
            )
            logger.critical(msg)
            raise ValueError, msg
        missing_from = [
            key for key in self.field_merge_modes if not key in note_from
        ]
        if missing_from:
            msg = "note_from fields are missing key(s) {}".format(
                ", ".join(missing_from)
            )
            logger.critical(msg)
            raise ValueError, msg
        for key in self.field_merge_modes.keys():
            note_to[key] = self.merge_fields(note_from[key], note_to[key],
                                             self.field_merge_modes[key])
        note_to.flush()

    def merge_tags(self, note_from, note_to):
        tags_from = note_from.tags
        tags_to = note_to.tags
        #logger.debug(note_from[self.match_field]+"before"+ str(type(note_from.tags))+ str(list(note_from.tags))+ str(list(note_to.tags)))
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

        #logger.debug(note_from[self.match_field]+"after"+ str(type(note_from.tags))+ str(list(note_from.tags))+ str(list(note_to.tags)))

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
