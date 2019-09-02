#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import QAction, SIGNAL
from anki.utils import stripHTML
from .log import logger
from collections import defaultdict


def remove_duplicates_preserve_order(lst):
    """ Remove all duplicates from list lst but do not mess up the order
    of them. """
    # https://stackoverflow.com/questions/480214/
    seen = set()
    seen_add = seen.add
    return [x for x in lst if not (x in seen or seen_add(x))]


class MergeNotes(object):
    def __init__(self):
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #                       BEGIN CONFIGURATION
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # --------------------- FIELDS TO MERGE -------------------------------

        # todo: write about warnings
        # Fields that should be merged
        self.fields_to_merge = [
            u'merge1',
            u'merge2',
            u'merge3',
            u'merge4'
        ]

        # --------------------- TAG MERGE MODES -------------------------------

        # todo: explain
        # Mode to merge the tags of the from notes and to notes. Choose from
        # 3 modes:
        # *  ```from```
        # *  ```to```
        # *  ```merge```
        # With meaning as above.
        # Note that the special tags defined below will be set automatically.
        self.tag_merge_mode = "merge"

        # --------------------- MATCH CONTROL ---------------------------------

        # Which field should be compared to find out which notes should be
        # merged together?
        self.match_field = u"Expression"

        # When comparing self.match_field, strip all HTML around the field
        # value (i.e. notes with match_field "<b>Test</b>" and "Test" are
        # still recognized to be merged
        self.strip_html = True

        # --------------------- RUN CONTROL -----------------------------------

        # Dry run: Only compare notes and display which notes can be merged,
        # but do not do any merging
        self.dry = False

        # --------------------- ADVANCED --------------------------------------

        # These two tags controll which notes are from notes and which are
        # to notes. If a note either acted as a to_note or from_note, the
        # respective tag is replaced with the two tags after.
        self.tag_from = u"MERGE_FROM"
        self.tag_to = u"MERGE_TO"
        self.tag_was_merged_from = u"WAS_MERGED_FROM"
        self.tag_was_merged_to = u"WAS_MERGED_TO"

        # When merging multiple field contents into one, which string is used
        # to separate them? Default is '<br>' (HTML line break)
        self.merge_join_string = u"<br>"

        # Try to remove empty field contents, which only have (supposedly)
        # invisible HTML content
        self.remove_html_ghost_field_content = True

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #                       END CONFIGURATION
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def setup_menu(self, browser):
        """ Adds a menu item to Anki's browser. Will be called via hook.
        :param browser:
        :return:
        """
        logger.debug("Setting up menu.")
        a = QAction("Merge Notes", browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"), self.loop)

    def get_match_field_from_nid(self, nid):
        note = mw.col.getNote(nid)
        expr = note[self.match_field]
        if not isinstance(expr, (str, unicode)):
            return None
        if self.strip_html:
            expr = stripHTML(expr).strip()
        return expr

    @staticmethod
    def get_nids_with_tag(tag):
        return mw.col.findNotes(u'tag:"{}"'.format(tag))

    @staticmethod
    def get_notes_from_nids(nids):
        return [mw.col.getNote(nid) for nid in nids]

    def loop(self, *arsg, **kwargs):
        nids_from = self.get_nids_with_tag(self.tag_from)
        nids_to = self.get_nids_with_tag(self.tag_to)

        logger.debug("Found {} notes with tag_from {}".format(len(nids_from),
                                                              self.tag_from))

        logger.debug("Found {} notes with tag_to {}".format(len(nids_to),
                                                              self.tag_to))

        logger.debug("looping to build db")

        nids_from_dict = defaultdict(list)
        nids_to_dict = defaultdict(list)

        for nid in nids_from:
            nids_from_dict[self.get_match_field_from_nid(nid)].append(nid)

        for nid in nids_to:
            nids_to_dict[self.get_match_field_from_nid(nid)].append(nid)

        # Remove None (corresponds to not properly retrieved expressions)
        nids_from_dict.pop(None, None)
        nids_to_dict.pop(None, None)

        all_notes = []
        for expr in nids_to_dict:
            notes_from = self.get_notes_from_nids(nids_from_dict[expr])
            notes_to = self.get_notes_from_nids(nids_to_dict[expr])
            for note_to in notes_to:
                self.merge_notes(notes_from, note_to)
            all_notes.extend(notes_from)
            all_notes.extend(notes_to)

        # Write only now that we know everything runs without error
        # Note that we have to write notes_from too, because we have added
        # a tag to them
        for note in all_notes:
            note.flush()

    def merge_notes(self, notes_from, note_to):
        self.merge_fields(notes_from, note_to)
        self.merge_tags(notes_from, note_to)

    def merge_fields(self, notes_from, note_to):
        for field in self.fields_to_merge:
            self.merge_field(notes_from, note_to, field)

    def merge_field(self, notes_from, note_to, field):
        if field not in note_to:
            logger.warning(
                u"Could not find field '{}' in note_to with match "
                u"field '{}'".format(field, note_to[self.match_field])
            )
            return
        field_to = note_to[field]
        fields_from = []
        for note_from in notes_from:
            if field not in note_from:
                logger.warning(
                    u"Could not find field '{}' in note_from with match "
                    u"field '{}'".format(field, note_to[self.match_field])
                )
                continue
            fields_from.append(note_from[field])
        note_to[field] = self.merge_field_contents([field_to] + fields_from)

    def merge_field_contents(self, field_contents):
        # If a field contains only HTML content, should we remove it?
        if self.remove_html_ghost_field_content:
            real_field_contents = [
                field_content for field_content in field_contents 
                if stripHTML(field_content)
            ]
        else:
            real_field_contents = field_contents

        return self.merge_join_string.join(real_field_contents)

    def merge_tags(self, notes_from, note_to):
        tags_from = []
        for note_from in notes_from:
            tags_from.extend(note_from.tags)
        tags_to = list(note_to.tags)

        if self.tag_merge_mode == "merge":
            new_tags_to = tags_from + tags_to
        elif self.tag_merge_mode == "from":
            new_tags_to = tags_from
        elif self.tag_merge_mode == "to":
            new_tags_to = tags_to
        else:
            msg = "Invalid merge mode for tags: {}".format(self.tag_merge_mode)
            logger.critical(msg)
            raise ValueError(msg)

        # IMPORTANT: do not copy the tag self.tag_from to the target note
        # also remove self.tag_to, so that we know which notes have been merged
        # and which have yet to be merged.
        for tag in [self.tag_from, self.tag_to]:
            while tag in new_tags_to:
                new_tags_to.remove(tag)
        new_tags_to.append(self.tag_was_merged_to)

        # Remove duplicates
        note_to.tags = remove_duplicates_preserve_order(new_tags_to)

        for note_from in notes_from:
            new_tags_from = list(note_from.tags)
            while self.tag_from in new_tags_from:
                new_tags_from.remove(self.tag_from)
            new_tags_from.append(self.tag_was_merged_from)
            note_from.tags = remove_duplicates_preserve_order(new_tags_from)
