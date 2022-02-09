# SPR-T-SHE-000006-shear-bias-001

## Summary

**Test dataset:** [TD-SHE-000006-global-validation](TD-SHE-000006-global-validation.html)

**Test procedure:** Estimated shear values from LensMC were linearly regressed against true input shear values, and the slope and intercept of the regression were used to calculate the multiplicative and additive bias respectively.

**Test result:** **NOK**

## Detailed test results

The bias requirements on the multiplative bias `m` and additive bias `c` are:
```
|m| < 1e-4
|c| < 5e-6
```

When the bias of the shear estimation method LensMC was measured, it was found to have bias of:
```
m1 = -0.19604 +/- 0.00514
c1 = -8.13002 x 10^-3 +/- 0.08181 x 10^-3
m2 = -0.18275 +/- 0.00512
c2 = -0.42275 x 10^-3 +/- 0.08161 x 10^-3
```

These values lie outside the requirements by the following numbers of standard deviations:
```
m1: 38.086
c1: 99.320
m2: 35.648
c2:  5.119
```

The threshold for failure for each of these parameters was `2` standard deviations, so this test is determined to be a failure for both test cases.
