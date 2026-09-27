# Typefaces embedded in the Mission Console

`python -m web.build_console` inlines these files into the built page as base64 `@font-face` rules,
so the page renders the same with the network off. `fonts.json` lists each file with its family,
style, weight and width ranges and unicode range, as Google Fonts serves them (latin subset).

| File | Typeface | Licence |
|---|---|---|
| `archivo-normal-latin.woff2` | Archivo, variable weight 100–900 and width 62–125 % | SIL OFL 1.1, `OFL-Archivo.txt` |
| `newsreader-italic-latin.woff2` | Newsreader italic, variable weight 200–800 | SIL OFL 1.1, `OFL-Newsreader.txt` |

Downloaded 27 Sep 2026 from fonts.gstatic.com; the licence texts are from github.com/google/fonts.
