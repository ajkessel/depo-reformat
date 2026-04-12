# depo-reformat 

# Introduction

This is a simple script that takes an excerpt from a deposition transcript and reformats it into a flowed text format.

# Usage

This script has two modes:
1. Copy a section of a deposition transcript into your system clipboard. Execute the script. Your system clipboard will be replaced with the reformatted version.
1. Execute the script without a transcript in your clipboard. A popup window will appear where you can paste your excerpt. Select OK and a new window will pop up with the reformatted version, which is also automatically saved into your system clipboard.

# Example

Consider the following excerpt:

> 1   Q: What is your name?
> 2   A: John Smith.
> 3   Q: Have you been deposed before?
> 4   A: No.

This will be transformed into:

> Q: What is your name?
>
> A: John Smith.
>
>
>
>
> Q: Have you been deposed before?
>
> A: No.

The result is thus more appropriate form pasting into other contexts like emails or legal briefs.

Deposition transcripts take many forms, so this may not work as expected. Always check against your source material.

# Caveat

This is alpha software and barely tested.
