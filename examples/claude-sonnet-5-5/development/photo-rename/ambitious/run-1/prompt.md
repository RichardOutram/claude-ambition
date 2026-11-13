# dev/photo-rename · ambitious

## Before the prompt

/be-ambitious

(blocked by the plugin's hook before Claude sees it; it arms the session)

## Prompt

Write a Python script that renames my photos by the date they were taken

## Client reply 1

Push it further.

## Client reply 2

B, an ongoing import. I copy photos off my phone and camera into a folder every so often, so I'd run it again and again on the same folder. It should skip files that are already renamed and not clobber anything if two photos share the same timestamp.

## Client reply 3

D. I want the full thing, because I'll be running this on years of photos from my phone and an older camera, and some have no date or the wrong one. Safe re-runs and duplicate detection matter most. The undo log is a must too, since I'd be nervous renaming thousands of files without a way back. For missing dates, fall back to the file's modified time but flag those files so I can check them.

## Client reply 4

B. I'd like the synthetic test suite, and I'd also like you to run it on a copy of a real photo folder and confirm that a run followed by an undo restores every file exactly. I'll do my own spot check of the flagged files, so the script should write a readable report listing them, but I don't need you to build anything beyond that.

## Client reply 5

Go with B. I'll copy a sample into `/Volumes/My Shared Files/work/sample_photos`, a mix of phone and camera shots, including some HEIC. Installing Pillow is fine, and add `pillow-heif` since the sample has HEIC files. Work only on a copy and leave my originals alone. Go ahead and finish the work without stopping.
