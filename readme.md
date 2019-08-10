# Anki Addon: Merging Notes 

**[Overview over my other Anki add-ons](http://www.lieret.net/opensource/#anki)**

Plugin for [Anki](https://apps.ankiweb.net/), a spaced repetition flashcard program.

Plugin to merge a set of notes (*from_notes*) into another set of notes (*to_notes*), i.e. to update the to_notes with information from the from_notes.

**THIS IS QUITE RUDIMENTARY: Originally only made this for a one time use. Leaving this here for anyone who may need it.
PLEASE BACKUP YOUR COLLECTION BEFORE EXPERIMENTING WITH IT!**

There is also another addon by [vgck](https://github.com/vgck) which is also about merging notes: [Link to Addon](https://github.com/vgck/merge-notes), so also consider using this. That one also copies scheduling information but maybe allows for a bit less configuration (?). 

## Merging procedure

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

## License

The contents of this repository are licensed under the [*AGPL3* license](https://choosealicense.com/licenses/agpl-3.0/) (to be compatible with the license of Anki and its addons as detailed [here](https://ankiweb.net/account/terms)).
