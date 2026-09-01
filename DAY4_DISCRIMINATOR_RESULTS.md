# Day 4 - Change Discriminator Experiments

## Objective

Evaluate whether a simple discriminator can reduce false-positive
detections caused by illumination/shadow changes while preserving
genuine surface-change detections.

## Baseline

Known shaded-relief lighting-only pair:

| Threshold | Detections | Detected coverage |
|---:|---:|---:|
| 30 | 1 | 62.0% |
| 60 | 9 | 41.5% |
| 90 | 9 | 31.0% |
| 120 | 9 | 20.4% |

These values were reproduced from the current production detector.

## Experiment 1 - Orientation

Tested contour/gradient orientation as a possible illumination
discriminator.

Result: calculating orientation alone did not change the detector's
false-positive coverage. No orientation-based filter was promoted to
production.

## Experiment 2 - Intensity Ratio

Global intensity ratio on the shaded-relief pair:

A mean intensity: 102.73
B mean intensity: 102.67
B/A ratio: 0.9994

A regional test also produced:

A: 102.49
B: 102.49
B/A ratio: 1.000

Result: no useful intensity-ratio separation was demonstrated.

## Experiment 3 - Gradient Direction

The shaded-relief difference contained a measurable directional
gradient structure.

However, testing the gradient direction against the available Kaguya
pair did not establish a reliable separation between illumination
artefacts and genuine changes.

Result: gradient direction was not promoted to production.

## Decision

No discriminator was added to the production change-detection
algorithm because none of the tested approaches demonstrated the
required reduction in false-positive coverage while preserving a
genuine change.

The verified change-detection implementation remains the production
baseline.

## Verification

Existing automated tests:

    python -m pytest app -q

Expected:

    9 passed

The repository should remain clean after committing this validation
record.
