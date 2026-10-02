# Typefaces embedded in the Mission Console

`python -m web.build_console` inlines these files into the built page as base64 `@font-face` rules,
so the page renders the same with the network off. `fonts.json` lists each file with its family,
style, weight range and unicode range, as Google Fonts serves them (latin subset).

| File | Typeface | Licence |
|---|---|---|
| `jost-normal-latin.woff2` | Jost, variable weight 100–900 | SIL OFL 1.1, `OFL-Jost.txt` |
| `jost-italic-latin.woff2` | Jost italic, variable weight 100–900 | SIL OFL 1.1, `OFL-Jost.txt` |
| `poppins-{400,500,600}-devanagari.woff2` | Poppins, Devanagari subset, for the Hindi page | SIL OFL 1.1, `OFL-Poppins.txt` |

Jost is Owen Earl's revival of Futura, the typeface on the plaque Apollo 11 left on the Moon.

Downloaded 27 Sep 2026 from fonts.gstatic.com; the licence texts are from github.com/google/fonts.

Poppins (Indian Type Foundry) is a geometric sans with a Devanagari design, so the Hindi page keeps Jost's geometry. Its Devanagari subset was downloaded 2 Oct 2026 from fonts.gstatic.com; the licence text is from github.com/itfoundry/Poppins. Latin text stays in Jost: the Poppins faces carry the Devanagari unicode range only.
