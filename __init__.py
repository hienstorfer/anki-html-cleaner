import json
import os
import re
from aqt import mw
from aqt.qt import QAction, QFileDialog
from aqt.utils import showInfo
from anki.notes import Note

# Load configuration
addon_path = os.path.dirname(__file__)
config_path = os.path.join(addon_path, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

# Define the data cleaning function
def clean_data(note: Note, fields, allowed_tags):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    allowed_tags_re = re.compile(r'|'.join(re.escape(tag) for tag in allowed_tags))
    for field in fields:
        if field in note:
            content = note[field]
            cleaned_content = tag_re.sub(lambda match: match.group(0) if allowed_tags_re.match(match.group(0)) else '', content)
            note[field] = cleaned_content
            note.flush()

# Create the menu entry
def start_cleaning():
    selected_notes = mw.col.find_notes("tag:*")
    if not selected_notes:
        showInfo("No notes selected.")
        return
    note_type = config["note_type"]
    fields = config["fields"]
    allowed_tags = config["allowed_tags"]
    for note_id in selected_notes:
        note = mw.col.get_note(note_id)
        if note.note_type()["name"] == note_type:
            clean_data(note, fields, allowed_tags)
    showInfo("Data cleaning completed.")

action = QAction("Clean Data", mw)
action.triggered.connect(start_cleaning)
mw.form.menuTools.addAction(action)

# Configurable settings
def load_config():
    with open(config_path, "r") as f:
        return json.load(f)

def save_config(config):
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

def configure_cleaning_settings():
    config = load_config()
    note_type, ok = QFileDialog.getOpenFileName(mw, "Select Note Type", config["note_type"])
    if ok:
        config["note_type"] = note_type
    fields, ok = QFileDialog.getOpenFileNames(mw, "Select Fields", "", "All Files (*)")
    if ok:
        config["fields"] = fields
    allowed_tags, ok = QFileDialog.getOpenFileNames(mw, "Select Allowed Tags", "", "All Files (*)")
    if ok:
        config["allowed_tags"] = allowed_tags
    save_config(config)
    showInfo("Configuration saved.")

config_action = QAction("Configure Data Cleaning", mw)
config_action.triggered.connect(configure_cleaning_settings)
mw.form.menuTools.addAction(config_action)
