# [RUDIMENTARY] Anki Addon: Merging Notes 

Plugin for [Anki](https://apps.ankiweb.net/), a spaced repetition flashcard program.

Plugin to merge a set of notes (*from_notes*) into another set of notes (*to_notes*), i.e. to update the to_notes with information from the from_notes.

**THIS IS QUITE RUDIMENTARY: Originally only made this for a one time use. Leaving this here for anyone who may need it.**

## Merging procedure

Notes of both sets must have *exactly* the same fields. If this is not the case, e.g. use the standard Anki interface to change the note type of the from_notes to that of the to_notes, or rename each of the fields.

Then

1. **BACKUP** your collection (main menu: ```File``` → ```Export```)
2. Modify the source of this plugin to control 
    1. which field will be compared to find notes which should be merged
    2. what the new field content will be
   for this, change the following lines of the file ```merge_notes.py```:
        ```py 
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
        ```
3. (Re)start Anki
4. Tag all from_notes with ```MERGE_FROM```
5. Tag all to_notes with ```MERGE_TO``` 
6. In the browser menu, click on ```merge notes``` to start the merging process
7. All from_notes that have been merged into others, now have the tag ```WAS_MERGED_FROM```, all to_notes that had another note merged into, now have the tag ```WAS_MERGED_TO```
8. Check the log (in the folder of this addon) or the command line output to see which notes could not ber merged, or simply check which notes don't have the tags from 6
9. Delete all notes with the tag ```MERGE_FROM```

If something goes wrong, simply reimport your backup (main menu: ```File``` → ```Import```). If you forgot to make a backup, Anki probably has made some for you, go check your backup directory ```<user name>/Documents/Anki/<Anki user name>/backups``` and pick one of the newer once for reimport.

## License

The contents of this repository are licensed under the [*AGPL3* license](https://choosealicense.com/licenses/agpl-3.0/) (to be compatible with the license of Anki and its addons as detailed [here](https://ankiweb.net/account/terms)).