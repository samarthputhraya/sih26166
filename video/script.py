"""The explainer's narration: one entry per beat, shared by voice.py and render.py.

v11 (2 Oct 2026). Every figure spoken or shown is one the claim-checked deck v11 carries, from
REPORT.md at the freeze commit 51a9ad0. Live runs on screen are live: the narration never quotes
their counts, only what the evidence logs hold.

`say` is what the voice reads (spelled for the speech engine); `cap` is the caption on screen;
`style` is an optional delivery note for that line, never read aloud.
`scene` names the picture in film.html that plays under the line.
"""

# The voice itself (Gemini 2.5 Pro TTS, Charon, Indian English) is set in voice.py.

BEATS = [
    dict(scene="hook", style="quietly intriguing, as if opening a story",
         cap="On the Moon, the ground never moves. The shadows do. Under a different Sun, the same "
             "crater can look like a different place.",
         say="On the Moon, the ground never moves. The shadows do. Under a different Sun, the same "
             "crater can look like a completely different place."),
    dict(scene="problem",
         cap="Chandrayaan-2 carries three cameras, from 0.25 m to over 80 m per pixel, and each must "
             "line up with other maps, often under a different Sun. And a matcher returns an answer, "
             "even when it is wrong.",
         say="Chandrayaan 2 carries three cameras, from a quarter of a metre per pixel to over eighty, "
             "and each must line up with other maps, often under a different Sun. And a matcher "
             "returns an answer... even when it's wrong."),
    dict(scene="title",
         cap="We are Team LunaXX. Our system registers lunar images, then tells you, region by "
             "region, whether to trust the result.",
         say="We are Team Luna Double X. Our system registers lunar images, and then tells you, "
             "region by region, whether to trust the result."),
    dict(scene="pipeline",
         cap="Both images go to one ground scale; lighting is reduced to gradient direction. LoFTR "
             "matches them on a laptop CPU, and MAGSAC++ fits the transform.",
         say="Both images go to one ground scale, and lighting is reduced to gradient direction. "
             "Loft-R matches them on an ordinary laptop CPU, and MAG-SAC plus plus fits the "
             "transform."),
    dict(scene="check",
         cap="Then our part: an independent check compares the pixels square by square, and never "
             "looks at the matches. Each square is verified, weak, or has no evidence.",
         say="Then comes our part. An independent check compares the pixels, square by square, and "
             "never looks at the matches. Each square is verified, weak, or has no evidence."),
    dict(scene="live-accept", style="a little lift on the word Accepted",
         cap="Here it is, live. Chandrayaan-2's OHRC against NASA's LRO camera, Suns 174° apart, "
             "so every shadow is reversed. Accepted, and the map shows where it holds.",
         say="Here it is, running live. Chandrayaan 2's O-H-R-C against NASA's L-R-O camera, "
             "Suns a hundred and seventy-four degrees apart, every shadow reversed. Accepted, and "
             "the map shows where it holds."),
    dict(scene="live-refuse",
         cap="Visible light against near-infrared: the pixels contradict the matcher, so its answer "
             "is refused, openly, and a declared fallback takes its place.",
         say="Now, visible light against near infrared. The pixels contradict the matcher, so its "
             "answer is refused, openly, and a declared fallback takes its place."),
    dict(scene="live-known",
         cap="Or give it any Moon picture and a transform of your choosing. It registers it back and "
             "measures the true error, because here the answer is known.",
         say="Or give it any Moon picture, and a transform of your choosing. It registers it back, "
             "and measures the true error, because this time, the answer is known."),
    dict(scene="outputs",
         cap="Every result exports a GeoTIFF on the reference grid, evenly spread control points for "
             "GDAL and QGIS, and an ISIS match list.",
         say="Every result exports a GeoTIFF on the reference grid, with evenly spread control "
             "points, and match lists for standard G-I-S and planetary tools."),
    dict(scene="evidence",
         cap="The evidence is frozen and reproducible: 400 windows, 11 instrument pairings. SAC's "
             "benchmark pair: 6 of 6. A whole overlap: 37 of 37, held-out median 0.57 m.",
         say="The evidence is frozen and reproducible. Four hundred windows, eleven instrument "
             "pairings. SAC's own benchmark pair: six of six. A whole overlap: thirty-seven of "
             "thirty-seven, held-out median just over half a metre."),
    dict(scene="sitn",
         cap="Every Chandrayaan-2 camera at one site, 60.7°N, Suns matched. OHRC → TMC-2: 10 of 10. "
             "Through LRO NAC, the loop closes to a median 2.0 m. IIRS infrared on TMC-2's pass: "
             "30 of 30. OHRC on the next orbit, views 40° apart: 8 of 8.",
         say="Now, every Chandrayaan 2 camera at one site, with the Suns matched. O-H-R-C onto "
             "T-M-C 2: ten of ten. Through NASA's camera, the loop closes to a median of two metres. "
             "I-I-R-S infrared, on T-M-C 2's pass: thirty of thirty. And O-H-R-C on the next orbit, "
             "from the other side: eight of eight."),
    dict(scene="suns",
         cap="On SAC's own frame, the Sun moved both ways. Raised by up to 41.7°, azimuth within "
             "20°: 61 of 71 accepted. Turned to the opposite side, up to 47° higher: 48 of 56.",
         say="On SAC's own benchmark frame, we moved the Sun both ways. Raised by up to forty-two "
             "degrees: sixty-one of seventy-one windows accepted. Turned to the opposite side, and "
             "raised again: forty-eight of fifty-six."),
    dict(scene="calibration",
         cap="We tested the checker too. Shifts planted in 30 real windows: no false alarms, and "
             "with the Suns close, every shift of 5 m or more was caught.",
         say="We tested the checker too. We planted wrong shifts in thirty real windows. No false "
             "alarms, and with the Suns close together, every shift of five metres or more was "
             "caught."),
    dict(scene="limits",
         cap="And it says what it cannot do: visible against near-infrared, refused 3 of 3. Sun "
             "azimuths 60–120° apart: 0 of 12 accepted, and none accepted wrongly.",
         say="And it tells you what it cannot do. Visible against near infrared: refused, three of "
             "three. With the Suns sixty to a hundred and twenty degrees apart: none of twelve "
             "accepted... and none accepted wrongly."),
    dict(scene="try",
         cap="Try it in any browser or on a phone, in English or Hindi, with nothing to install: "
             "samarthputhraya.github.io/sih26166",
         say="Try it yourself, in any browser or on a phone, in English or in Hindi, with nothing "
             "to install, at the address on screen."),
    dict(scene="close", style="warm and assured, a confident close",
         cap="LunaXX. Offline, on a laptop, open source. Lunar image registration that knows when "
             "it is wrong.",
         say="Luna Double X. Offline, on a laptop, and open source. Lunar image registration... "
             "that knows when it's wrong."),
]
