"""Build the Mission Console: web/console.template.html + the frozen evidence -> web/dist/.

    python -m web.build_console                       # dist/mission-console.html and dist/index.html
    python -m web.build_console --site                # also dist/site/ + dist/console-site.zip, the
                                                      # published copy with every pair's result to download
    python -m web.build_console --site --live-url https://lunaxx-<id>.asia-south1.run.app

The console is a DISPLAY of the evidence, never a source of it. This script only READS: the
evidence logs, the demo caches, geometry_prior.json, the exported result bundles and the LOLA
DEM. Every number the page shows is one REPORT.md also prints (Invariant 1 applies to this page
exactly as it does to the deck), and the figures typed into the template's prose are the
claim-checked deck's.

Say "MEASURED at the freeze commit", not "in REPORT.md AT the freeze commit". The freeze measures
the rows; its report step writes REPORT.md with that commit's code, and REPORT.md is committed
after it. It lives in web/, outside core/ evaluation/ ops/ app/, so building it can never restamp
an evidence row or a demo cache. Re-run it after any new freeze and update FREEZE below.

v11 (2 Oct 2026): the showcase is the national-round evidence - SAC's pair at 174 deg, the Sun
raised 42 deg on SAC's frame, OHRC -> TMC-2 and NAC -> TMC-2 under matched Suns, TMC-2 -> IIRS in
the infrared, OHRC seen from two orbits 40 deg apart, the 29.6x scale rung - and four honest
refusals. Every text has an English and a Hindi version; the page switches between them.
"""
import argparse, base64, collections, csv, json, pathlib, pickle, statistics as st, sys, zipfile
import numpy as np, cv2, tifffile

from web.panel import jpg, panel

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip())
HERE = pathlib.Path(__file__).resolve().parent
FREEZE = "04ed5f6"
REPO = "https://github.com/samarthputhraya/sih26166"
sys.path.insert(0, str(ROOT))

ap = argparse.ArgumentParser(description="Build the Mission Console")
ap.add_argument("--site", action="store_true", help="also write dist/site/ and dist/console-site.zip")
ap.add_argument("--live-url", default="", help="the hosted live workbench (web/cloud_bundle.py, on Cloud Run)")
ARGS = ap.parse_args()


def rows(p): return list(csv.DictReader(open(ROOT / p, encoding="utf-8-sig")))
def f(x): return float(x) if x not in ("", None) else None


def sharpness(path):
    """High-frequency content of a reference frame, as the variance of its Laplacian.

    Reported so the "it is only blurrier" reading can be tested rather than argued with. It is a
    relative measure between two frames on the same grid, not an absolute resolution figure.
    """
    a = tifffile.imread(str(path)).astype(np.float64)
    if a.ndim == 3:
        a = a[..., 0]
    a = (a - np.nanmin(a)) / max(np.nanmax(a) - np.nanmin(a), 1e-9)
    return float(cv2.Laplacian(np.nan_to_num(a), cv2.CV_64F).var())


def twin(pid, other, band, other_band):
    """The same source image against a different BAND of the same reference product."""
    def one(p):
        row = latest.get(p)
        return {"matches": int(f(row["n_matches"])), "inliers": int(f(row["inliers"])),
                "ratio": round(f(row["inlier_ratio"]), 3),
                "cov": round(f(row["grid_coverage_fraction"]), 2),
                "verdict": row["verdict"], "declared": row["method_declared"],
                "med": round(f(row["residual_median_px"]), 3), "gsd": round(f(row["ref_gsd_m"]), 1),
                "sharp": round(sharpness(next((ROOT / "data/pairs" / p).glob("*_ref.tif"))), 5)}
    g = json.loads((ROOT / "data/pairs" / pid / "geometry_prior.json").read_text(encoding="utf-8"))
    mm = {r["pair_id"]: r for r in rows("evaluation/multimodal_check.csv")}
    fb = mm.get(pid)
    return {"band": band, "other_band": other_band, "a": one(other), "b": one(pid),
            "src": g["source"]["product_id"], "ref": g["reference"]["product_id"].split(" band")[0],
            "fallback_px": round(f(fb["disagreement_median_px"]), 3) if fb else None,
            "fallback_m": round(f(fb["disagreement_median_m"]), 1) if fb else None}


#: Wavebands the cutter labelled on the wrong side of a round number: IIRS band 1000 centres at
#: 998.8 nm, which `ops/cut_site_pairs.py` printed as "visible/near-visible". It is near-infrared;
#: the label is corrected here, in the presentation layer, and the cutter is left alone.
BAND_FIX = {"998.8 nm (visible/near-visible)": "998.8 nm (near-infrared)"}


def _band(b):
    return BAND_FIX.get(b, b)


# The showcase, in the order a reader meets it: what it registers, then what it refuses. `tag`
# obeys Invariant 2: OHRC -> OHRC and TMC-2 fore -> aft are SAME SENSOR; only visible-to-infrared
# is MULTI-MODAL; OHRC -> TMC-2 is cross-sensor within one mission. Numbers in the prose are
# REPORT.md's at 51a9ad0 (the section is named in the comment).
ROSTER = [
    # "SAC's own benchmark pair (equatorial ...)": 6 agrees
    dict(id="sac_ohrc_nac_w06", tag="CROSS-SENSOR",
         en=("Chandrayaan-2 OHRC → LRO NAC",
             "SAC's own published benchmark pair. Sun azimuths 174° apart, so every shadow points the opposite way.",
             "Suns 174° apart, and it holds. Two cameras on two missions, under opposite Suns: the matches and the pixels independently agree on one alignment. All 6 windows of this pair are accepted."),
         hi=("चंद्रयान-2 OHRC → LRO NAC",
             "SAC की अपनी प्रकाशित बेंचमार्क जोड़ी। सूर्य के दिगंश 174° अलग, इसलिए हर छाया उलटी दिशा में है।",
             "सूर्य 174° अलग, फिर भी परिणाम टिकता है। दो मिशनों के दो कैमरे, उलटे सूर्य के नीचे: मिलान (matches) और पिक्सेल स्वतंत्र रूप से एक ही संरेखण पर सहमत हैं। इस जोड़ी की सभी 6 विंडो स्वीकार हुईं।")),
    # "Sun azimuth and elevation, on SAC's own frame": near-azimuth table, 61 of 71; highest Sun 7 of 8
    dict(id="sac_ohrclroc_nacm1356313970le_c17", tag="CROSS-SENSOR",
         en=("OHRC → LRO NAC, the Sun 42° higher",
             "The same SAC frame, against an LRO image with the Sun 41.7° higher and its azimuth within 20°.",
             "The problem statement asks for Sun elevation, not only azimuth. On SAC's own frame, nine LRO images raise the Sun by up to 41.7°: 61 of 71 windows are accepted, and 7 of 8 at the highest Sun, this one among them."),
         hi=("OHRC → LRO NAC, सूर्य 42° ऊँचा",
             "वही SAC फ्रेम, ऐसी LRO छवि के सामने जिसमें सूर्य 41.7° ऊँचा है और दिगंश 20° के भीतर।",
             "समस्या-कथन केवल दिगंश नहीं, सूर्य की ऊँचाई भी माँगता है। SAC के अपने फ्रेम पर नौ LRO छवियाँ सूर्य को 41.7° तक ऊपर ले जाती हैं: 71 में से 61 विंडो स्वीकार, और सबसे ऊँचे सूर्य पर 8 में से 7, यह उनमें से एक।")),
    # "One site, every camera ... (Site N)": OHRC -> TMC-2 10 agrees, 0.61-1.57 px (3.2-8.1 m), 9 quoted
    dict(id="siten_ohrc2031_tmc20200607_c03", tag="CROSS-SENSOR",
         en=("Chandrayaan-2 OHRC → TMC-2",
             "Two cameras on one spacecraft, at 60.7°N, passes chosen for their Sun: 2.2° apart in azimuth.",
             "At SAC's frame this pairing was refused, with the Suns 120° apart and a 5× scale gap; that test cannot separate the two. Here the passes were chosen for their Sun, at 4.2×, and all 10 windows are accepted: held-out median 0.61–1.57 TMC-2 px (3.2–8.1 m) over 9 of them. Choosing the pass by its Sun is part of the method."),
         hi=("चंद्रयान-2 OHRC → TMC-2",
             "एक ही यान के दो कैमरे, 60.7°N पर; पास सूर्य के आधार पर चुने गए: दिगंश में केवल 2.2° का अंतर।",
             "SAC के फ्रेम पर यह जोड़ी अस्वीकार हुई थी, जहाँ सूर्य 120° अलग थे और पैमाने में 5× का अंतर था; वह परीक्षण इन दोनों को अलग नहीं कर सकता। यहाँ पास सूर्य के आधार पर चुने गए, 4.2× पर, और सभी 10 विंडो स्वीकार हुईं: 9 विंडो पर held-out माध्यिका 0.61–1.57 TMC-2 px (3.2–8.1 m)। सूर्य देखकर पास चुनना हमारी विधि का हिस्सा है।")),
    # Site N: NAC -> TMC-2 4 agrees; loop RMS median 1.99 m, max 4.04 m
    dict(id="siten_nacm1282456834re_tmc20200607_c00", tag="CROSS-SENSOR",
         en=("LRO NAC → Chandrayaan-2 TMC-2",
             "The same site: an LRO image onto TMC-2, two missions, Suns within a few degrees.",
             "The third leg at this site. The chain OHRC → NAC → TMC-2 and the direct OHRC → TMC-2 agree to a loop RMS of 1.99 m (median of 4 windows, max 4.04 m): three instruments and two missions, consistent with each other. That is consistency between registrations, not absolute accuracy."),
         hi=("LRO NAC → चंद्रयान-2 TMC-2",
             "वही स्थल: LRO की छवि TMC-2 पर, दो मिशन, सूर्य कुछ ही डिग्री के अंतर पर।",
             "इस स्थल की तीसरी कड़ी। OHRC → NAC → TMC-2 की श्रृंखला और सीधा OHRC → TMC-2 1.99 m के loop RMS तक सहमत हैं (4 विंडो की माध्यिका, अधिकतम 4.04 m): तीन उपकरण और दो मिशन, एक-दूसरे से सुसंगत। यह पंजीकरणों के बीच की सुसंगति है, पूर्ण सटीकता नहीं।")),
    # "TMC-2 -> IIRS, orbit of 2020-06-07": 62 of 62 beyond 850 nm over two orbits; 0.16-0.32 px (14-27 m)
    dict(id="chain_tmc20200607_iirs1555_w05", tag="MULTI-MODAL",
         en=("Chandrayaan-2 TMC-2 → IIRS 1555 nm",
             "Visible onto near-infrared, 16× coarser, on the same orbit under the same Sun.",
             "IIRS flies with TMC-2 and images the same ground seconds apart, so the Sun is the same and only the band and the scale change. Over two orbits, 62 of 62 infrared registrations are accepted; at 1555 nm the held-out median is 0.16–0.32 IIRS px (13.9–27.3 m)."),
         hi=("चंद्रयान-2 TMC-2 → IIRS 1555 nm",
             "दृश्य प्रकाश से निकट-अवरक्त (near-infrared) पर, 16× मोटे पिक्सेल, एक ही कक्षा और एक ही सूर्य।",
             "IIRS, TMC-2 के साथ उड़ता है और कुछ ही सेकंड में वही ज़मीन देखता है, इसलिए सूर्य वही रहता है; बदलते केवल बैंड और पैमाना हैं। दो कक्षाओं में 62 में से 62 अवरक्त पंजीकरण स्वीकार; 1555 nm पर held-out माध्यिका 0.16–0.32 IIRS px (13.9–27.3 m)।")),
    # "A real viewpoint test at Site N": 8/8, 39.6-39.8 deg apart, 0.91 px (1.12 m) on 1.232 m
    dict(id="siten_ohrc2031_ohrc2229_c15", tag="SAME SENSOR",
         en=("OHRC → OHRC of the next orbit",
             "One site seen looking forward and looking back on consecutive orbits: viewing directions 40° apart, the Sun within 2.2°.",
             "A real viewpoint test. All 8 windows are accepted, held-out median 0.91 px = 1.12 m on a 1.23 m grid. It is one camera against itself, so it is a viewpoint test and is never counted as cross-sensor."),
         hi=("OHRC → अगली कक्षा का OHRC",
             "एक ही स्थल, लगातार दो कक्षाओं में आगे और पीछे देखते हुए: दृष्टि-दिशाएँ 40° अलग, सूर्य 2.2° के भीतर।",
             "एक वास्तविक दृष्टिकोण (viewpoint) परीक्षण। सभी 8 विंडो स्वीकार, 1.23 m ग्रिड पर held-out माध्यिका 0.91 px = 1.12 m। यह एक ही कैमरा है, इसलिए इसे कभी cross-sensor नहीं गिना जाता।")),
    # "Scale rung": 3 of 4; w01 26 verified, 0.545 px = 4.0 m
    dict(id="site_ohrc_tc_ortho_w01", tag="CROSS-SENSOR",
         en=("Chandrayaan-2 OHRC → Kaguya TC",
             "A 29.6× scale gap: 0.25 m imagery onto a 7.4 m ortho map.",
             "Scale invariance at nearly thirty to one. Both images are brought to one ground scale before matching, so the matcher never sees the gap. Three of the four windows at this site are accepted; this one on dense evidence, held-out median 0.55 px = 4.0 m on the 7.4 m grid."),
         hi=("चंद्रयान-2 OHRC → Kaguya TC",
             "29.6× का पैमाना-अंतर: 0.25 m की छवि 7.4 m के ऑर्थो मानचित्र पर।",
             "लगभग तीस गुना पैमाने पर स्केल-स्वतंत्रता। मिलान से पहले दोनों छवियाँ एक ही ज़मीनी पैमाने पर लाई जाती हैं, इसलिए matcher को यह अंतर दिखता ही नहीं। इस स्थल की चार में से तीन विंडो स्वीकार; यह घने प्रमाण पर, 7.4 m ग्रिड पर held-out माध्यिका 0.55 px = 4.0 m।")),
    # "Kaguya TC -> Kaguya MI": refused 3 of 3; fallback vs visible 0.283 px (4.2 m) on w01
    dict(id="site_tc_morning_mi1548_w01", limit=True, tag="MULTI-MODAL",
         en=("Kaguya TC → Kaguya MI 1548 nm",
             "Visible light matched against near-infrared. Same source file and grid as its 749 nm twin.",
             "<b>Refused, then delivered anyway.</b> The matcher's transform here is visibly wrong — open THE MATCHER'S ANSWER. The area check caught it, the system refused it and fell back to global phase correlation, <b>declaring which method it used</b>. That fallback lands 0.283 px = 4.2 m from the visible-band registration of this same window. The table below compares it with the 749 nm twin."),
         hi=("Kaguya TC → Kaguya MI 1548 nm",
             "दृश्य प्रकाश का मिलान निकट-अवरक्त से। स्रोत फ़ाइल और ग्रिड वही जो 749 nm जोड़ी के हैं।",
             "<b>अस्वीकार, फिर भी परिणाम दिया गया।</b> यहाँ matcher का रूपांतरण साफ़ ग़लत है — “matcher का उत्तर” खोलकर देखें। क्षेत्र-जाँच ने इसे पकड़ा, सिस्टम ने इसे अस्वीकार किया और global phase correlation पर लौटा, <b>यह बताते हुए कि कौन-सी विधि लगी</b>। वह fallback इसी विंडो के दृश्य-बैंड पंजीकरण से 0.283 px = 4.2 m दूर पड़ता है। नीचे की तालिका 749 nm जोड़ी से तुलना करती है।")),
    # "Kaguya TC -> Chandrayaan-2 IIRS": 10 contradicted, 1 unconfirmed of 11
    dict(id="site_tc_ortho_iirs1000_w04", limit=True, tag="MULTI-MODAL",
         en=("Kaguya TC → Chandrayaan-2 IIRS",
             "Visible onto an imaging-spectrometer band directly: 12× coarser, at 89 m per pixel.",
             "Matched straight onto the Kaguya map, none of the 11 IIRS windows is accepted: 10 are refused and one is left unconfirmed. We report that as a limit. Matched through TMC-2 of its own orbit instead, IIRS registers (the TMC-2 → IIRS pair above)."),
         hi=("Kaguya TC → चंद्रयान-2 IIRS",
             "दृश्य छवि सीधे इमेजिंग-स्पेक्ट्रोमीटर बैंड पर: 12× मोटे पिक्सेल, 89 m प्रति पिक्सेल।",
             "Kaguya मानचित्र पर सीधे मिलान करने पर 11 में से कोई IIRS विंडो स्वीकार नहीं: 10 अस्वीकार और एक अपुष्ट। हम इसे एक सीमा के रूप में बताते हैं। अपनी ही कक्षा के TMC-2 के माध्यम से IIRS पंजीकृत हो जाता है (ऊपर TMC-2 → IIRS जोड़ी)।")),
    # "SAC's benchmark site: OHRC -> TMC-2": 4 of 4 refused; Suns 120 deg az, incidence 59 deg, scale 5.0x.
    # "OHRC -> TMC-2 again": the Sun and the 5.0x scale "this test cannot separate" - never the Sun alone.
    dict(id="sac_ohrc_tmc_w01", limit=True, tag="CROSS-SENSOR",
         en=("Chandrayaan-2 OHRC → TMC-2 at SAC's frame",
             "Two cameras on one spacecraft, with the Suns 120° apart in azimuth and 59° in incidence, and a 5× scale gap.",
             "Refused on all four windows at SAC's frame, and rightly: a 1.9 km offset between the archives left these windows barely sharing ground, and re-cut in LRO's geometry they are still refused. That leaves the Sun and the 5× scale, which this test cannot separate. Where the Suns match, at 4.2×, the same two cameras register 10 of 10 (above)."),
         hi=("SAC फ्रेम पर चंद्रयान-2 OHRC → TMC-2",
             "एक ही यान के दो कैमरे, सूर्य दिगंश में 120° और आपतन (incidence) में 59° अलग, और पैमाने में 5× का अंतर।",
             "SAC के फ्रेम पर चारों विंडो अस्वीकार, और सही कारण से: आर्काइवों के बीच 1.9 km के अंतर से इन विंडो में साझा ज़मीन बहुत कम थी, और LRO की ज्यामिति में दोबारा काटने पर भी वे अस्वीकार हैं। तब बचते हैं सूर्य और 5× का पैमाना, जिन्हें यह परीक्षण अलग नहीं कर सकता। जहाँ सूर्य मेल खाते हैं, 4.2× पर, वही दो कैमरे 10 में से 10 पंजीकृत करते हैं (ऊपर)।")),
    # "Real viewpoint: TMC-2 fore -> aft": 1 of 4 accepted, ~50 deg apart
    dict(id="sac_tmcfore_tmcaft_w04", limit=True, tag="SAME SENSOR",
         en=("TMC-2 fore → TMC-2 aft",
             "One instrument, one pass, seconds apart. Only the viewing direction differs, by about 50°.",
             "One of four accepted, and this is it — because relief parallax is not a homography. When two views differ by 50° the terrain itself shifts differently at different heights, and no single flat transform can describe it. The system does not pretend otherwise; orthorectification with TMC-2's own DTM is the planned answer."),
         hi=("TMC-2 fore → TMC-2 aft",
             "एक उपकरण, एक पास, कुछ सेकंड का अंतर। केवल दृष्टि-दिशा लगभग 50° अलग है।",
             "चार में से एक स्वीकार, और वह यही है — क्योंकि उच्चावच (relief) का लंबन (parallax) एक homography नहीं है। जब दो दृश्य 50° अलग हों, तो ज़मीन अलग ऊँचाइयों पर अलग खिसकती है, और कोई एक सपाट रूपांतरण उसे नहीं बता सकता। सिस्टम इसका दिखावा नहीं करता; TMC-2 के अपने DTM से ऑर्थोरेक्टिफिकेशन अगला कदम है।")),
]


def trust(e):
    """A frozen pair, rendered by the SAME function the live server uses (web/panel.py)."""
    pid = e["id"]
    r = pickle.load(open(ROOT / f"demo_cache/results/{pid}.pkl", "rb"))
    g = json.loads((ROOT / "data/pairs" / pid / "geometry_prior.json").read_text(encoding="utf-8"))

    def side(k):
        s = g[k]
        return {"inst": s.get("instrument"), "band": _band(s.get("band")),
                "prod": s.get("product_id"), "gsd": s.get("resampled_gsd_mpp")}

    label, sub, plain = e["en"]
    m = panel(r, side("source"), side("reference"), pid=pid, label=label, sub=sub, tag=e["tag"],
              plain=plain,
              twin=twin(pid, "site_tc_morning_mi749_w01", "1548 nm (near-infrared)",
                        "749 nm (visible)") if "mi1548" in pid else None)
    m["hi"] = dict(zip(("label", "sub", "plain"), e["hi"]))
    m["limit"] = bool(e.get("limit"))   # shown under "its limits", whatever its verdict
    if ARGS.site and (DATA / "out" / pid).is_dir():
        m["bundle"] = f"bundles/{pid}.zip"
    return m


real = rows("evaluation/real_pairs_log.csv")
latest = {}  # read by twin(), which runs later, when data = {...} calls trust()
for r in real: latest[r["pair_id"]] = r
reg = {k: r for k, r in latest.items() if r["verdict"] != "INVALIDATED" and not k.startswith("loop_")}

tiles = []
for k, r in sorted(reg.items()):
    if not k.endswith("_full"): continue
    gp = json.loads((ROOT / "data/pairs" / k / "geometry_prior.json").read_text(encoding="utf-8"))
    tiles.append({"id": k.split("_")[-2], "x": gp["window_centre_map_m"][0], "y": gp["window_centre_map_m"][1],
                  "w": gp["window_m"], "med": round(f(r["residual_median_px"]), 3),
                  "inl": int(f(r["inliers"])), "ratio": round(f(r["inlier_ratio"]), 3),
                  "ver": int(f(r["verified"])), "verdict": r["verdict"], "sec": round(f(r["seconds"]), 1)})

from ops.sun_sweep import outcomes_v2
sw = {k: r for k, r in reg.items() if (r.get("outcome") or "").strip()}
v2 = outcomes_v2(list(sw.values()), rows("evaluation/results_log.csv"))
sweep = [{"az": round(f(r["d_sun_azimuth_deg"]), 1), "inl": int(f(r["inliers"]) or 0),
          "o": v2.get(k, r["outcome"]), "nac": r["reference_product"]} for k, r in sw.items()]
bins = []
for a, b in [(0, 10), (10, 30), (30, 60), (60, 90), (90, 120), (120, 180)]:
    rs_ = [s for s in sweep if a <= s["az"] < b]
    bins.append({"a": a, "b": b, "n": len(rs_), "frames": len({s["nac"] for s in rs_}),
                 "o": dict(collections.Counter(s["o"] for s in rs_)),
                 "inl": int(st.median(s["inl"] for s in rs_)) if rs_ else 0})

tr = rows("evaluation/trust_real_calibration.csv")
def pop(sel):
    by = {}
    for r in tr:
        if (r.get("kind") or "translation") != "translation" or not sel(r): continue
        by.setdefault(f(r["displacement_m"]), []).append(r["contradicted"] == "True")
    return [{"m": d, "n": len(v), "hit": sum(v)} for d, v in sorted(by.items())]
near = pop(lambda r: f(r.get("d_sun_azimuth_deg") or 0) < 10)
hard = pop(lambda r: f(r.get("d_sun_azimuth_deg") or 0) >= 10)
nt = [r for r in tr if (r.get("kind") or "translation") != "translation"]
rs = {"moved": sum(int(r["cells_moved_2px"]) for r in nt), "refused": sum(int(r["moved_not_verified"]) for r in nt),
      "still": sum(int(r["cells_under_1px"]) for r in nt), "kept": sum(int(r["under_1px_verified"]) for r in nt),
      "trials": len(nt)}


# --- the Sun ladder on SAC's frame: one dot per LRO image (REPORT, "Sun azimuth and elevation") ---
ladder = []
by_nac = collections.defaultdict(list)
for k, r in reg.items():
    if k.startswith("sac_ohrclroc_nac"):
        by_nac[r["reference_product"]].append(r)
for nac, rs_ in sorted(by_nac.items()):
    ladder.append({"nac": nac, "az": round(st.median(f(r["d_sun_azimuth_deg"]) for r in rs_), 1),
                   "el": round(st.median(-f(r["d_incidence_deg"]) for r in rs_), 1),
                   "n": len(rs_), "ok": sum(r["verdict"] == "agrees" for r in rs_)})


# --- Site N: four instruments, matched Suns (REPORT, "One site, every camera") ---
# Each leg carries what REPORT's Site N table prints: windows, accepted, and the RANGE of the
# per-window held-out medians of accepted windows with an inlier ratio above 0.5, on the leg's
# reference grid. Until 2 Oct the console drew a median of those medians (1.09, 0.92, 0.62 px),
# which REPORT never prints (pre-submission audit, L2). Every string is checked against
# REPORT.md below; the build stops if one is not printed there.
REPORT_TXT = (ROOT / "REPORT.md").read_text(encoding="utf-8")
UNPRINTED = []


def _printed(s):
    if s not in REPORT_TXT:
        UNPRINTED.append(s)
    return s


def _leg(pred, ranged=True):
    rs_ = [r for k, r in reg.items() if pred(k)]
    if not rs_:
        return None
    g = f(rs_[0]["ref_gsd_m"])
    out = {"n": len(rs_), "ok": sum(r["verdict"] == "agrees" for r in rs_), "gsd": round(g, 3),
           "src": round(f(rs_[0]["src_gsd_m"]), 3)}
    rob = [f(r["residual_median_px"]) for r in rs_ if r["verdict"] == "agrees"
           and f(r["inlier_ratio"] or 0) > 0.5 and r.get("residual_median_px")]
    if ranged and rob:
        lo, hi = min(rob), max(rob)
        _printed(f"{lo:.2f}-{hi:.2f} ({lo * g:.1f}-{hi * g:.1f} m) on {g:g} m")
        _printed(f"{g:g} m")
        out["px"], out["m"] = f"{lo:.2f}–{hi:.2f}", f"{lo * g:.1f}–{hi * g:.1f}"
    return out


loops = [r for k, r in latest.items() if k.startswith("loop_siten")]
iirs2 = [r for k, r in reg.items() if k.startswith("chain_tmc20200607_iirs") and "_iirs746_" not in k]
siten = {"ot": _leg(lambda k: k.startswith("siten_ohrc") and "_tmc" in k),
         "on": _leg(lambda k: k.startswith("siten_ohrc") and "_nac" in k),
         "nt": _leg(lambda k: k.startswith("siten_nac")),
         "vp": _leg(lambda k: k.startswith("siten_ohrc") and "_ohrc" in k[6:], ranged=False),
         "ti": {"n": len(iirs2), "ok": sum(r["verdict"] == "agrees" for r in iirs2),
                # REPORT's grid for this orbit (own-pixels table), not a median of the windows' grids
                "gsd": _printed(f"{min(f(r['ref_gsd_m']) for r in iirs2):.2f} m")[:-2],
                "lat": [round(min(f(r["window_lat"]) for r in iirs2), 1), round(max(f(r["window_lat"]) for r in iirs2), 1)]},
         "loop": {"n": len(loops), "med": round(st.median(f(r["loop_rms_m"]) for r in loops), 2),
                  "max": round(max(f(r["loop_rms_m"]) for r in loops), 2)} if loops else None}
if loops:
    _printed(f"Loop RMS median **{siten['loop']['med']:.2f} m**")
    _printed(f"max {siten['loop']['max']:.2f} m")
# v14 (3 Oct 2026): the new ledger rows, the planted-section lines and the finder carry figures typed
# into the template; each must be one REPORT.md prints, or the build stops.
for _s in ("**accepted 31/31**", "(median 287 m)", "**accepted 44/49**", "agrees 44, unconfirmed 3, contradicted 2",
           "Accepted: **1/4 without the DTM, 2/4 with it.**", "the residual threshold flags **0 of 1056**",
           "the area check flags **1056 of 1056**", "| 6 | 6/6 | 0/6 | 0/6 | 0/6 |", "| 56 | 48/56 | 0/56 | 0/56 | 0/56 |",
           "one click's precision is a median 1.47 m", "85.9%", "99.2%",
           "**208 of 300** have an image from ANOTHER orbit lit within 5°", "median 13.3 s over the 89"):
    _printed(_s)
if UNPRINTED:
    raise SystemExit("Site N values that REPORT.md does not print - regenerate REPORT.md or fix the "
                     "console: " + "; ".join(UNPRINTED))

dem = np.load(DATA / "raw/dem_site_60m.npy").astype(np.float64)
n = min(dem.shape); dem = dem[:n, :n]; N = 224
small = cv2.resize(dem, (N, N), interpolation=cv2.INTER_AREA)
lo, hi = float(small.min()), float(small.max())
q = np.round((small - lo) / (hi - lo) * 65535).astype("<u2")
demd = {"n": N, "lo": round(lo, 1), "hi": round(hi, 1), "km": round(n * 0.06, 2),
        "b64": base64.b64encode(q.tobytes()).decode()}

# --- the Sun finder over every OHRC observation (ops/reference_index.py -> web/reference_index.json) ---
def _finder():
    import datetime as _dt
    idx = json.loads((HERE / "reference_index.json").read_text(encoding="utf-8"))
    from ops.reference_index import summary

    def day(s): return str(s)[:10]

    def ts(s):
        try:
            return _dt.datetime.fromisoformat(str(s).strip().replace("Z", "").replace(" ", "T")[:26])
        except ValueError:
            return None
    # "same pass": taken within 30 min of the frame (TMC-2 and IIRS image alongside OHRC within
    # minutes). Chandrayaan-2's orbit is ~118 min, so the next orbit is never labelled same pass.
    out, default = [], 0
    for i, tg in enumerate(idx["targets"]):
        t0 = ts(tg["time"])
        cands = [[c["id"], c["instrument"], c["overlap"], c["sun_angle"], c["d_azimuth"], day(c["time"]),
                  bool(t0 and ts(c["time"]) and abs((ts(c["time"]) - t0).total_seconds()) < 1800)]
                 for c in tg["candidates"]]
        out.append([tg["id"], day(tg["time"]), tg["centre"][0], tg["centre"][1], tg["incidence"], tg["azimuth"], cands])
        if tg["id"] == "ch2_ohr_ncp_20250612T2031048828_d_img_d18":
            default = i
    return {"t": out, "def": default, "k5": summary(idx)["other_orbit_within_5"]}


data = {"freeze": FREEZE, "repo": REPO, "live": ARGS.live_url.rstrip("/"), "dem": demd, "bins": bins, "finder": _finder(),
        "maps": [trust(e) for e in ROSTER],
        "tiles": tiles, "sweep": sweep, "near": near, "hard": hard, "rotscale": rs,
        "ladder": ladder, "siten": siten}
blob = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
tpl = (HERE / "console.template.html").read_text(encoding="utf-8")
MARK = "/*__DATA__*/null"
if tpl.count(MARK) != 1:
    raise SystemExit(f"template must contain {MARK!r} exactly once, found {tpl.count(MARK)}")

# The page must work with the network off (Gate 4), so its typefaces travel inside it rather
# than coming from a font service: Jost (latin) and Poppins (Devanagari, for the Hindi page), SIL
# OFL 1.1 - see web/fonts/. A missing file fails the build loudly.
FONTS_MARK = "/*__FONTS__*/"
if tpl.count(FONTS_MARK) != 1:
    raise SystemExit(f"template must contain {FONTS_MARK!r} exactly once")
_faces = []
for _name, (_fam, _style, _wght, _stretch, _range) in json.loads(
        (HERE / "fonts" / "fonts.json").read_text(encoding="utf-8")).items():
    _b = base64.b64encode((HERE / "fonts" / _name).read_bytes()).decode()
    _faces.append(f'@font-face{{font-family:"{_fam}";font-style:{_style};font-weight:{_wght};'
                  + (f"font-stretch:{_stretch};" if _stretch else "")
                  + f'font-display:swap;src:url(data:font/woff2;base64,{_b}) format("woff2");'
                  + f"unicode-range:{_range}}}")
tpl = tpl.replace(FONTS_MARK, "\n".join(_faces))
(HERE / "dist").mkdir(exist_ok=True)
page = tpl.replace(MARK, blob)

# Paint the freeze commit into the markup instead of waiting for JS.
for _id in ("fz", "fz2"):
    src, dst = f'<span id="{_id}"></span>', f'<span id="{_id}">{FREEZE}</span>'
    if src not in page:
        raise SystemExit(f"template no longer contains {src!r}")
    page = page.replace(src, dst)

OUT = HERE / "dist" / "mission-console.html"
OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)}: {OUT.stat().st_size/1024:.0f} KB")

# mission-console.html is a FRAGMENT; index.html wraps it in a standards-mode UTF-8 document.
from web.server import SKELETON                                            # noqa: E402
IDX = HERE / "dist" / "index.html"
IDX.write_text(SKELETON.replace("<!--PAGE-->", page), encoding="utf-8")
print(f"wrote {IDX.relative_to(ROOT)}: {IDX.stat().st_size/1024:.0f} KB  (standards mode, UTF-8, viewport)")

# The published copy: the page, every showcase pair's exported result as a zip, and a zip of the
# lot for the Pages workflow (.github/workflows/console-pages.yml), which deploys it from a GitHub
# release so no binary ever enters git (Invariant 5).
if ARGS.site:
    import shutil
    site = HERE / "dist" / "site"
    shutil.rmtree(site, ignore_errors=True)
    (site / "bundles").mkdir(parents=True, exist_ok=True)   # an open browser tab can keep the folder
    shutil.copy(IDX, site / "index.html")
    (site / "favicon.svg").write_bytes(__import__("web.server", fromlist=["FAVICON"]).FAVICON)
    (site / ".nojekyll").write_text("", encoding="utf-8")
    n_b = 0
    for m in data["maps"]:
        if not m.get("bundle"):
            continue
        src = DATA / "out" / m["id"]
        with zipfile.ZipFile(site / m["bundle"], "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(src.iterdir()):
                if p.is_file():
                    z.write(p, f"{m['id']}/{p.name}")
            z.writestr(f"{m['id']}/README.txt",
                       f"{m['label']}\n\nThe pipeline's exported result for real pair {m['id']}, measured at the "
                       f"evidence freeze {FREEZE} ({REPO}). registered_product.tif is on the reference grid; "
                       "gcps.txt / gcps.points are every inlier as ground control points for GDAL and QGIS, and "
                       "gcps_uniform.* the same thinned to at most 4 per cell of an 8 x 8 grid; matches.csv has "
                       "every match with its residual and trust state; trust_map.csv the 8 x 8 cell states; "
                       "report.json / report.md the metrics, timings and input checksums.\n")
        n_b += 1
    pack = HERE / "dist" / "console-site.zip"
    with zipfile.ZipFile(pack, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(site.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(site).as_posix())
    print(f"wrote {site.relative_to(ROOT)}/ ({n_b} result bundles) and {pack.relative_to(ROOT)}: "
          f"{pack.stat().st_size/1048576:.1f} MB")

# The page is one document whose entire behaviour is one inline <script>. A syntax error in it is
# silent in the build and total in the browser, so parse it here if node is available.
import re                                                                  # noqa: E402
import shutil                                                              # noqa: E402
import subprocess                                                          # noqa: E402
import tempfile                                                            # noqa: E402
_node = shutil.which("node")
if _node:
    _scripts = [s for s in re.findall(r"<script[^>]*>(.*?)</script>", page, re.S) if s.strip()]
    for _i, _src in enumerate(_scripts):
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False,
                                         encoding="utf-8") as _f:
            _f.write(_src)
        _r = subprocess.run([_node, "--check", _f.name], capture_output=True, text=True)
        pathlib.Path(_f.name).unlink(missing_ok=True)
        if _r.returncode:
            raise SystemExit(f"inline script {_i} does not parse:\n{_r.stderr}")
    print(f"js: {len(_scripts)} inline script(s) parse clean (node --check)")
else:
    print("js: node not found, skipping the syntax check")
print("outcomes", dict(collections.Counter(s["o"] for s in sweep)))
print("ladder", [(d["nac"], d["az"], d["el"], f"{d['ok']}/{d['n']}") for d in ladder])
print("siten", siten)
print(f"roster: {len(data['maps'])} pairs")
for m in data["maps"]:
    print(f"  {m['id']:40} {m['tag']:13} {m['verdict']:13} {m['counts']['verified']:>2}/64 verified"
          + (f"  bundle {m['bundle']}" if m.get("bundle") else ""))
