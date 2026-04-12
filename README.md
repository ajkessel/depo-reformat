# depo-reformat 

# Introduction

This is a simple script that takes an excerpt from a deposition transcript and reformats it into a flowed text format.

# Usage

This script has two modes:

1. Copy a section of a deposition transcript into your system clipboard. Execute the script. Your system clipboard will be replaced with the reformatted version.
1. Execute the script without a transcript in your clipboard. A popup window will appear where you can paste your excerpt. Select OK and a new window will pop up with the reformatted version, which is also automatically saved into your system clipboard.

If it finds page numbers within the selected excerpt, it will add a page/line number range to the top of the output.

# Example

Consider the following excerpt:

> 1   Q: What is your name?  
> 2   A: John Smith.  
> 3   Q: Have you been deposed before?  
> 4   A: No.  

This will be transformed into:

> Q: What is your name?  
> A: John Smith.
>
>
> Q: Have you been deposed before?  
> A: No.

The result is thus more appropriate form pasting into other contexts like emails or legal briefs.

Deposition transcripts take many forms (e.g. "Q:" versus "Q.", with and without timestamps, different spacing), so this may not work as expected. Always check against your source material.

# Bugs

File an issue if you find one!

# Future work

I'd like to allow the user to be able to use this script with piped input/output at the command-line, but have not been able to figure out a reliable way for the compiled script on Windows to detect whether it is running in a terminal or launched from Explorer.

# Caveat

This is alpha software and barely tested.
