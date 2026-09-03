On this Tier-D pair we found 35 changes. Of those, 0 look like genuine surface changes, 31 are shadow/illumination effects, and 4 are alignment artifacts.

\# Lunar Change Detection



\## Purpose



This module compares two aligned lunar images and identifies regions that may have changed.



The detector is designed to distinguish potential surface changes from common artifacts such as shadow movement and registration errors.



\## Detection Pipeline



The current pipeline is:



1\. Validate image inputs

2\. Convert non-uint8 images to uint8 using a common intensity scale

3\. Match image dimensions

4\. Calculate absolute pixel difference

5\. Apply median blur

6\. Apply binary threshold

7\. Apply morphological opening

8\. Apply morphological closing

9\. Remove regions near the image border

10\. Find contours

11\. Filter very small regions

12\. Classify detected regions

13\. Calculate physical area



\## Classifications



| Classification | Meaning |

|---|---|

| `new bright` | Region became significantly brighter |

| `disappeared` | Region became significantly darker |

| `shadow?` | Long, thin region that may represent shadow displacement |

| `uncertain` | Detected change that cannot be confidently classified |



These classifications are heuristic and are not a physics-based shadow model.



\## Area Calculation



Physical area is calculated as:



&#x20;   area\_m2 = area\_px \* gsd\_mpp²



The `gsd\_mpp` value should come from the image-pair catalogue for real lunar data.



Do not assume a fixed pixel scale for different missions.



\## Testing



The detector has been tested with:



\- New bright objects

\- Disappearing objects

\- Long thin regions

\- Uncertain changes

\- Small noise

\- Border artifacts

\- uint16 input

\- Different image dimensions



All current automated tests pass.



\## Known Limitations



Simple image differencing can produce false positives because:



\- Shadows can move between images

\- Image registration may not be perfect

\- The Moon has relatively little genuine surface change over short time periods



On the real Tier-D optical/elevation-derived pair, 35 candidate changes were found. Manual inspection classified 0 as likely genuine surface changes, 31 as likely shadow/illumination effects, and 4 as likely registration artifacts. This means 100% of the detected candidates in this test were false positives under the manual classification used here. The current detector cannot reliably distinguish genuine surface changes from shadows, illumination differences, and registration artifacts. With another week, the next improvement would be a stronger shadow filter using mission Sun-azimuth metadata, followed by DEM-based shadow prediction.



\## Real Data



The next major test is a real aligned before/after lunar image pair.



Priority demonstration:



\*\*Chandrayaan-3 Vikram landing site\*\*



The real pair should be tested only after verifying its source, metadata, and GSD.



False-positive counts should be recorded honestly for each real image pair.



\## Interface



Main function:



```python

detect\_changes(

&#x20;   img\_a,

&#x20;   img\_b,

&#x20;   gsd\_mpp

)



Returns:



\- `overlay\_bgr`: Output image with detected regions and labels drawn on it

\- `changes`: List of dictionaries containing:

&#x20; - `bbox`

&#x20; - `centroid\_px`

&#x20; - `area\_px`

&#x20; - `area\_m2`

&#x20; - `classification`


## Real Kaguya Validation

A real Kaguya Terrain Camera test pair was processed through the team's
alignment pipeline before running change detection.

- Matches: 5544
- RANSAC inliers: 5544
- Aligned image: 640 × 640
- Total detections: 1
- Real changes: 1
- Alignment artefacts: 0
- Shadow/lighting detections: 0
- Classification: `new bright`
- Detected area: 83,054.09 m²
- Expected planted-circle area: 89,364 m²
- Result: PASS

The planted change was successfully detected within the expected
area tolerance of 67,000–112,000 m².


