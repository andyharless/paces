# paces

A project to estimate multiple musical tempos from an audio segment. E.g., a song marked at ♩=160, in 4/4 time with secondary stress on beat 3 and a lot of ♫, could be timed as 40, 80, 160, or 320 bpm depending how you define a beat, and depending on the particular sound of the song, which may or may not lend itself to any or all of these timings.

Beat detection and tempo estimation are standard problems, for which (imperfect) solutions exist. But one thing I've found trying to jog to music is that a single tempo estimate (even if it's accurate) doesn't necessarily solve the relevant problem.  For example, if a song has ♩=105 but has a lot of 8th notes, you can jog with very quick steps (210 per minute) or with very slow steps (105). And a song compatible with a normal jogging pace (say 160) may not be recognizable as such from a single tempo estimate (e.g. maybe 80).

The problem is complicated by the fact that, while most songs have an even time signature (2 or 4), many have odd (usually 3), and some have both even and odd factors (6 or 12). So the relation of the official tempo to the possible alternatives differs from song to song.

I'm referring to this the "pace compatibility" problem, or sometimes the "multiple tempo estimation" problem, because I don't know what it's supposed to be called or whether it even has a name or if anyone else has even thought to work on it.I call this the "pace compatibility" problem, or sometimes the "multiple tempo estimation" problem, because I don't know what it's supposed to be called or whether it even has a name or if anyone else has even thought to work on it.
