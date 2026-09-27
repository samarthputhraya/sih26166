"""The explainer's narration: one entry per beat, shared by voice.py and render.py.

Every figure spoken or shown is one the claim-checked deck v10 already carries, from REPORT.md
at the freeze commit 7dd4e5b. Live runs on screen are live: the narration never quotes their
counts, only what the evidence logs hold.

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
         cap="That makes Chandrayaan-2 images hard to register: different cameras, scales and Suns. "
             "And every method returns an answer, even when it is wrong.",
         say="That makes Chandrayaan 2 images hard to register. Different cameras, different scales, "
             "different Suns. And every method returns an answer... even when it's wrong."),
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
    dict(scene="refuse",
         cap="If the pixels disagree, the answer is refused, and a declared fallback takes its "
             "place.",
         say="If the pixels disagree with the matcher, the answer is refused, and a declared "
             "fallback takes its place."),
    dict(scene="live-accept", style="a little lift on the word Accepted",
         cap="Here it is, live. Chandrayaan-2's OHRC against NASA's LRO camera, Suns 174° apart, "
             "so every shadow is reversed. Accepted, and the map shows where it holds.",
         say="Here it is, running live. Chandrayaan 2's O-H-R-C against NASA's L-R-O camera, "
             "Suns a hundred and seventy-four degrees apart, every shadow reversed. Accepted, and "
             "the map shows where it holds."),
    dict(scene="live-refuse",
         cap="Visible light against near-infrared: the pixels contradict the matcher, so the system "
             "refuses it, openly.",
         say="Now, visible light against near infrared. The pixels contradict the matcher, so the "
             "system refuses it, openly."),
    dict(scene="live-known",
         cap="Or give it any Moon picture. Choose a rotation, a scale and a shift: it warps the "
             "image, registers it back, and measures the true error, because here the right answer "
             "is known.",
         say="Or give it any Moon picture you like. Choose a rotation, a scale and a shift. It warps "
             "the image, registers it back to the original, and measures the true error, because "
             "this time, the right answer is known."),
    dict(scene="outputs",
         cap="Every result exports a GeoTIFF on the reference grid, control points for GDAL and "
             "QGIS, and an ISIS match list.",
         say="Every result exports a GeoTIFF on the reference grid, with control points and match "
             "lists for standard G-I-S and planetary tools."),
    dict(scene="evidence",
         cap="The evidence is frozen and reproducible: 160 ground windows, 8 instrument pairings. "
             "SAC's benchmark pair: 6 of 6. A whole overlap: 37 of 37, held-out median 0.57 m.",
         say="The evidence is frozen and reproducible. A hundred and sixty ground windows, eight "
             "instrument pairings. SAC's own benchmark pair: six of six. A whole overlap: "
             "thirty-seven of thirty-seven, held-out median just over half a metre."),
    dict(scene="calibration",
         cap="We tested the checker too. Shifts planted in 30 real windows: no false alarms, and "
             "with the Suns close, every shift of 5 m or more was caught.",
         say="We tested the checker too. We planted wrong shifts in thirty real windows. No false "
             "alarms, and with the Suns close together, every shift of five metres or more was "
             "caught."),
    dict(scene="limits",
         cap="And it says what it cannot do: near-infrared refused 3 of 3; TMC-2 with the Suns 120° "
             "apart refused 4 of 4.",
         say="And it tells you what it cannot do. Near infrared: refused, three of three. T-M-C 2, "
             "with the Suns a hundred and twenty degrees apart: refused, four of four."),
    dict(scene="close", style="warm and assured, a confident close",
         cap="LunaXX. Offline, on a laptop, open source. Lunar image registration that knows when "
             "it is wrong.",
         say="Luna Double X. Offline, on a laptop, and open source. Lunar image registration... "
             "that knows when it's wrong."),
]
