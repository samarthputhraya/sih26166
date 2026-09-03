"""Settings shared by all three classical baselines.

WHY THIS FILE EXISTS
--------------------
Gate 2 asks whether our method is at least twice as good as the best classical
one. The first thing a judge will ask about that claim is whether the comparison
was fair - and if SIFT, ORB and AKAZE were each tuned differently, the honest
answer is no.

Until Day 5 they were: SIFT used a ratio test of 0.70 and ORB and AKAZE used
0.75. Each detector defaulted to its own value, so nobody could see the three
side by side and notice.

*** ONE VALUE, IMPORTED, NEVER RETYPED. ***

If a baseline ever needs its own threshold - and there are legitimate reasons one
might - pass `ratio=` explicitly at the call site and record it in the `config`
column of the results row. What must never happen again is three different
defaults sitting in three different files where no one number is visibly the
odd one out.
"""

# Lowe's ratio test. A match is kept only if the best descriptor distance is
# less than RATIO_TEST x the second-best, which throws away matches that had a
# near-equally-good alternative and were therefore probably ambiguous.
#
# 0.75 is the value two of the three already used, and it is the looser of the
# two - so adopting it does not quietly make the classical baselines look worse
# than they were measured to be. Picking the tighter 0.70 would have handed our
# own method an advantage by suppressing classical matches.
RATIO_TEST = 0.75
