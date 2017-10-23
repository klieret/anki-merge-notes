# [RUDIMENTARY] Anki Addon: Merging Notes 

**[Overview over my other Anki add-ons](http://www.lieret.net/opensource/#anki)**

Plugin for [Anki](https://apps.ankiweb.net/), a spaced repetition flashcard program.

Plugin to merge a set of notes (*from_notes*) into another set of notes (*to_notes*), i.e. to update the to_notes with information from the from_notes.

**THIS IS QUITE RUDIMENTARY: Originally only made this for a one time use. Leaving this here for anyone who may need it.
PLEASE BACKUP YOUR COLLECTION BEFORE EXPERIMENTING WITH IT!**

## Merging procedure

Notes of both sets must have *exactly* the same fields. If this is not the case, e.g. use the standard Anki interface to change the note type of the from_notes to that of the to_notes, or rename each of the fields.

Then

1. **BACKUP** your collection (main menu: ```File``` → ```Export```)
2. Install this addon (download repository contents e.g. by clicking here)
3. Modify the source of this plugin to control (see below). You can configure
    1. which field will be compared to find notes which should be merged
    2. what the new field content will be
4. (Re)start Anki
5. Tag all from_notes with ```MERGE_FROM```
6. Tag all to_notes with ```MERGE_TO``` 
7. In the browser menu, click on ```merge notes``` to start the merging process
8. All from_notes that have been merged into others, now have the tag ```WAS_MERGED_FROM```, all to_notes that had another note merged into, now have the tag ```WAS_MERGED_TO```
9. Check the log (in the folder of this addon) or the command line output to see which notes could not ber merged, or simply check for notes/cards which have the tag ```MERGE_FROM``` but not the tag ```WAS_MERGED_FROM``` or which have the tag ```MERGE_TO``` but not the tag ```WAS_MERGED_TO```. This can be done via Anki's search function.
10. If there are such notes, fix them manually, or change them such that a rerun of this addon merges them.
11. If you do not want to keep the notes which were merged into the "to notes", delete all notes with the tag ```WAS_MERGED_FROM```.

If something goes wrong, simply reimport your backup (main menu: ```File``` → ```Import```). If you forgot to make a backup, Anki probably has made some for you, go check your backup directory ```<user name>/Documents/Anki/<Anki user name>/backups``` and pick one of the newer once for reimport.

## Configuration

For configuration, go to the file ```merge_notes.py``` and change the lines of the ```__init__``` function. 
This should look something like this:

```py
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
#    note, i.e. we do not change anything)
# * ```merge_ft``` (the field value of the to note will be
#   field value of from note + line break + field value of to note
# * ```merge_tf``` (the field value of the to note will be
#   field value of to note + line break + field value of from note
# Note: Every field name of the from and to notes must be assigned a
#       merge mode, else an error will be displayed!
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
```

## License

The contents of this repository are licensed under the [*AGPL3* license](https://choosealicense.com/licenses/agpl-3.0/) (to be compatible with the license of Anki and its addons as detailed [here](https://ankiweb.net/account/terms)).
