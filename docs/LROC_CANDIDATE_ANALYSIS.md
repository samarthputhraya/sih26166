\# LROC Candidate Analysis



\## Purpose



This document records the analysis of a candidate localized dark feature identified in

Lunar Reconnaissance Orbiter Camera (LROC) Narrow Angle Camera (NAC) data.



The analysis is intended to provide a reproducible evidence trail for the SIH lunar

surface anomaly workflow.



\---



\## Source Product



\*\*LROC NAC product:\*\*



`NAC\_PHO\_E010N0230\_M102000149R.IMG`



The corresponding LROC XML label is retained with the source data outside the Git

repository because the raw image product is too large for GitHub.



The raw `.IMG` product is intentionally excluded by the repository `.gitignore`.



\### Data layout used



The analysis reads four float32 channels from the binary image product:



\- Channel 0: I/F

\- Channel 3: incidence angle



Binary data parameters used for this product:



\- Data offset: `15292` bytes

\- Lines: `25408`

\- Samples: `3823`

\- Pixel scale used for approximate measurements: `1.1 m/pixel`



\---



\## Candidate Location



The investigated candidate is centered at approximately:



\- Line: `1565`

\- Sample: `2626`



The surrounding image was inspected using multiple independent measurements rather

than relying only on visual darkness.



\---



\# Analysis Results



\## 1. Local I/F Contrast



A local background region was compared with a 15-pixel-radius candidate region.



Candidate radius:



\*\*15 pixels ≈ 16.5 m\*\*



Measured local background median:



`0.0047597154`



Candidate median I/F:



`0.005415132`



Candidate/background median ratio:



`1.1377`



This simple comparison is strongly affected by illumination geometry and therefore

should not be treated as the primary evidence by itself.



\---



\## 2. Incidence Angle



The candidate and surrounding terrain have similar high incidence angles.



Measured medians from the initial analysis:



\- Candidate median incidence: approximately `80.42°`

\- Background median incidence: approximately `80.71°`



This makes incidence geometry an important consideration when interpreting apparent

brightness or darkness.



\---



\## 3. Matched-Incidence Comparison



The candidate was compared with nearby control terrain within the same incidence-angle

ranges.



The final local-control test produced:



| Incidence | Candidate / Control |

|-----------|---------------------|

| 75–77° | 0.887× |

| 77–79° | 0.547× |

| 79–81° | 1.106× |

| 81–83° | 1.092× |

| 83–85° | 0.650× |

| 85–87° | 0.297× |

| 87–89° | 0.580× |

| 89–91° | 1.117× |



The median ratio across these matched bins was approximately:



\*\*1.05×\*\*



The result is therefore not uniformly darker than the surrounding terrain after

matching by incidence angle.



This is an important limitation and prevents the feature from being classified solely

as a photometric anomaly.



\---



\# 4. Radial Morphology



A radial I/F profile was calculated around the candidate center.



The profile shows a pronounced central depression followed by an increase in I/F

toward an annular bright region.



Key measurements:



\- Central median I/F at 0–2 px: approximately `0.000723`

\- Minimum median I/F within the inner region: approximately `0.000608`

\- Bright-rim peak radius: approximately `12 px`

\- Bright-rim radius: approximately `13.2 m`

\- Approximate rim diameter: approximately `26.4 m`



The outer background median used in the radial profile was:



`0.0047118114`



The minimum interior median was approximately:



`0.0006077401`



The resulting interior/background ratio was:



`0.12898`



or approximately:



\*\*87.1% lower I/F than the selected outer radial background.\*\*



The radial profile therefore provides substantially stronger morphological evidence

than a single pixel or simple local brightness comparison.



\---



\# 5. Rim Geometry



An azimuthal rim analysis estimated the radius of the brightest surrounding annulus.



Measured bright-rim radii:



| Sector | Radius |

|--------|--------|

| 0–45° | 10 px |

| 45–90° | 12 px |

| 90–135° | 14 px |

| 135–180° | 14 px |

| 180–225° | 14 px |

| 225–270° | 14 px |

| 270–315° | 10 px |

| 315–360° | 10 px |



Mean rim radius:



\*\*12.25 px ≈ 13.48 m\*\*



Standard deviation:



\*\*1.85 px ≈ 2.04 m\*\*



Approximate rim diameter:



\*\*26.95 m\*\*



The variation is consistent with a non-perfectly circular feature and/or strong

illumination and terrain effects.



\---



\# 6. Dark-Region Shape



A threshold-based dark-region extraction was also performed.



The threshold was defined as:



`65% of the local background median I/F`



Measured local background:



`0.004836624`



Threshold:



`0.0031438055`



The resulting dark region contained:



`359 pixels`



Ellipse-equivalent dimensions:



\- Major axis: approximately `19.78 m`

\- Minor axis: approximately `15.47 m`

\- Axis ratio: approximately `0.782`

\- Eccentricity: approximately `0.623`

\- Equivalent circular diameter: approximately `17.49 m`



The dark-pixel centroid was close to the selected candidate center:



\- X offset: approximately `-0.50 m`

\- Y offset: approximately `-1.52 m`



This indicates that the dark region is spatially localized rather than being a

randomly distributed set of isolated pixels.



\---



\# 7. Azimuthal Structure



The feature was also tested for azimuthal symmetry.



The measured median I/F varied substantially between sectors.



The strongest and weakest sector medians were approximately:



\- Maximum: `0.009253`

\- Minimum: `0.005352`



Maximum/minimum ratio:



\*\*approximately 1.73×\*\*



Opposite-sector comparisons showed smaller differences in several directions but

increased asymmetry in others.



This indicates that illumination/topography effects are significant and must be

considered when interpreting the feature.



\---



\# Evidence Assessment



The current analysis supports the following observations:



\### Supported



1\. A spatially localized low-I/F region exists around the investigated coordinates.

2\. The feature has a coherent radial structure.

3\. A surrounding higher-I/F annular region is present.

4\. The radial profile produces a strong central-to-background contrast.

5\. The dark region has a compact, measurable shape.

6\. The apparent feature is not simply a single anomalous pixel.

7\. The candidate exhibits significant azimuthal variation.



\### Important limitations



1\. The matched-incidence analysis does \*\*not\*\* show uniformly reduced I/F across

&#x20;  all incidence bins.

2\. Illumination geometry strongly influences the measured I/F.

3\. The feature therefore should not be described as definitively anomalous solely

&#x20;  from photometry.

4\. The current measurements establish a strong morphological candidate, not a

&#x20;  confirmed physical interpretation.

5\. Further validation using independent observations, photometric correction,

&#x20;  topographic data, and/or additional LROC images is desirable.



\---



\# Reproducibility



The analysis code is located at:



`ops/lroc/analyze\_candidate.py`



The raw LROC `.IMG` product is intentionally not committed to GitHub because of its

large size.



The analysis can be reproduced locally when the original LROC product is available.



Example:



```powershell

python ops/lroc/analyze\_candidate.py `

&#x20;   "C:\\path\\to\\NAC\_PHO\_E010N0230\_M102000149R.IMG"
