#!/usr/bin/env python3
"""
Deposition transcript reformatter.

Usage:
    - Copy deposition excerpt into system clipboard and run script
    - Or run script without excerpt in clipboard and paste excerpt into popup box
    - If successful, reformatted transcript will be in system clipboard
    - To map to a vim hotkey that will be run on selected text (e.g. here <leader>t), add to vimrc:
    - xnoremap xnoremap <leader>t "+y:call system('depo-reformat.py')<cr>

Strips line numbers, joins wrapped lines, and puts each Q./A. exchange
on its own line separated by a blank line, and performs other cleanup.
"""

import os
import sys
import re
import sys
import string
import pyperclip
import tkinter as tk
from pathlib import Path
from tkinter import simpledialog
from win11toast import notify

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_text_input(title="Input", prompt="Paste or type text below:", width=80, height=20, text=""):
    """Pop up a resizable multiline text input window. Returns the text or None if cancelled."""
    result = [None]

    def on_ok():
        result[0] = text_widget.get("1.0", tk.END).rstrip("\n")
        root.destroy()

    def on_cancel():
        root.destroy()

    root = tk.Tk()
    root.title(title)

    label = tk.Label(root, text=prompt, anchor="w")
    label.pack(fill="x", padx=8, pady=(8, 2))

    # Scrollable text area
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=8, pady=4)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text_widget = tk.Text(frame, width=width, height=height, wrap="word",
                          yscrollcommand=scrollbar.set, font=("Consolas", 10))
    text_widget.insert("1.0", text)

    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_widget.yview)

    # OK / Cancel buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill="x", padx=8, pady=(2, 8))

    tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side="right", padx=(4, 0))
    tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side="right")

    # Let Enter in the text area work normally (newline); Ctrl+Enter submits
    root.bind("<Control-Return>", lambda e: on_ok())
    root.protocol("WM_DELETE_WINDOW", on_cancel)

    text_widget.focus_set()
    root.mainloop()

    return result[0]

def strip_line_number(line):
    """Remove a leading line number (e.g. '  12   Some text' -> 'Some text')."""
    # remove non-alphanumeric/punctuation characters like page breaks
    line = re.sub(f"[^a-zA-Z0-9 {re.escape(string.punctuation)}]","", line)
    # remove leading timestamps
    line = re.sub(r"^\s*[0-9]+:[0-9][0-9](:[0-9][0-9])*\s*([AaPp][Mm])*\s*","",line)
    line = re.sub(r"^\s*\d+\s+", "", line)           # remove leading line number
    line = re.sub(r"\s+"," ", line)                  # replace multiple spaces with one
    line = re.sub(r"^([0-9\s]*)$","", line)          # remove page number lines
    line = re.sub(r"^([A-Z\s\-]*)$","", line)        # remove ALL CAPS lines (e.g. confidentiality legend)
    # remove trailing timestamps
    line = re.sub(r"[0-9]+:[0-9][0-9](:[0-9][0-9])*\s*([AaPp][Mm])*\s*$","",line)

    return line


def reflow(lines):
    """Join wrapped lines and split on Q./A. boundaries."""
    header = ''
    start_page = 0
    start_line = 0
    end_page = 0
    end_line = 0
    last_line = 0
    # first, try to detect start and end page number
    for l in lines:
        page = re.match(r'^\s*([0-9]+)\s*$',l)
        if page and start_page < 1:
            start_page = int(page.group())
            end_page = start_page
            if last_line > 1:
                start_page -= 1
            if last_line > 0:
                start_line = last_line
        elif page:
            end_page = int(page.group())
        line = re.match(r'^\s*([0-9]+)[A-Za-z \.]+',l)
        if line:
            if last_line == 0 or start_page > 0:
                last_line = int(line.group(1))
            if start_page > 0 and start_line < 1:
                start_line = last_line
            else:
                end_line = last_line

    # if start and end page/lines are found, create a header
    if start_page and start_line and end_page and end_line:
        header = f'{start_page}:{start_line} - {end_page}:{end_line}\n'
 
    # Strip line numbers and trailing whitespace; drop blank lines
    stripped = [strip_line_number(l).rstrip() for l in lines]
    stripped = [l for l in stripped if l]

    # Merge into logical paragraphs: a new paragraph starts at Q. or A.
    paragraphs = []
    current = []

    for line in stripped:
        if re.match(r"^([QA][\.\s])|(BY M[RS])|(MR\. )|(MRS\. )|(MS\. )|(THE )", line) and current:
            paragraphs.append(" ".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        paragraphs.append(" ".join(current))

    return (header, paragraphs)


def main():
    
    raw = ''
    icon = resource_path('icon.png')
    if not Path(icon).is_file():
        #       icon = os.path.dirname(os.path.abspath(__file__)) + "/icon.png"
       icon = Path(__file__).resolve().parent.as_posix() + "/icon.png"

    # FIXME doesn't work on Windows
    # need another method to detect if session is interactive
    # first try to read transcript from stdin
    #if sys.stdin.isatty():
    #    raw = sys.stdin.readlines()
    #    if not re.search(r'^ *[0-9][0-9]', raw, flags=re.MULTILINE):
    #        raw = ''

    # if no transcript is detected from stdin, try the system clipboard
    if not raw:
        raw = pyperclip.paste()
    
    # if no transcript is detected from stdin or system clipboard, pop up GUI
    gui = not re.search(r'^ *[0-9][0-9]', raw, flags=re.MULTILINE)
    if gui:
        raw = get_text_input("Paste Depo", "Paste deposition excerpt")
        
    # if we still don't have a transcript, exit
    if not raw or not re.search(r'^ *[0-9][0-9]', raw, flags=re.MULTILINE):
       notify(app_id='depo-reformat',body='No depo excerpt found',icon=icon,button='Dismiss',duration='long')
       return

    lines = raw.splitlines()
    if not lines:
       notify(app_id='depo-reformat',body='No depo excerpt found',icon=icon,button='Dismiss',duration='long')
       return

    (header, paragraphs) = reflow(lines)
    parts = []
    for i, p in enumerate(paragraphs):
        if i == 0:
            parts.append(p)
        elif re.search(r"^Q[\.\s]",p):
            parts.append("\n\n" + p)
        else:
            parts.append("\n" + p)
    result = header + "".join(parts)
    pyperclip.copy(result)
    if gui:
       raw = get_text_input("Result", "Reformatted transcript", text=result)
       pyperclip.copy(raw)
    else:
       notify(app_id='depo-reformat',body='Depo Excerpt Reformatted',icon=icon,button='Dismiss',duration='short')

if __name__ == "__main__":
    main()
