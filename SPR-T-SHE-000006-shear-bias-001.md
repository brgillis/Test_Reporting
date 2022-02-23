# SPR-T-SHE-000006-shear-bias-001

## Summary

**Test dataset:** [TD-SHE-000006-global-validation](TD-SHE-000006-global-validation.html)

**Test procedure:** Estimated shear values from LensMC were linearly regressed against true input shear values, and the slope and intercept of the regression were used to calculate the multiplicative and additive bias respectively. &sigma;

**Test result:** **NOK** for multiplicative bias, **POK** for additive bias

## Detailed test results

The algorithmic bias requirements on the multiplative bias *m* and additive bias *c* for an uncalibrated shear estimation algorithm are interpreted to be:

* *&sigma;*(*m*) < 1 x 10^-4
* *&sigma;*(*c*) < 5 x 10^-6

When the bias of the shear estimation method LensMC was measured, it was found to have bias and errors on such of:

* *m*<sub>1</sub> = -0.19604 +/- 0.00514
* *m*<sub>2</sub> = -0.18275 +/- 0.00512
* *c*<sub>1</sub> = -8.13002 x 10^-3 +/- 0.08181 x 10^-3
* *c*<sub>2</sub> = -0.42275 x 10^-3 +/- 0.08161 x 10^-3

We first note that for all components, the absolute value of the bias differs from zero at very high significance (at least 5&sigma; in all cases). Although the requirements do not directly test this, as this algorithm was expected to have near-zero bias, we raise this issue as a warning.

Secondly, we look at the main outputs of this test, the errors on the bias values. The requirements implicitly assume that the bias is measured on a sufficiently-large dataset, such as simulations covering the same sky area as the Euclid Wide survey, 14,514 sq. deg. As this test was limited to a much smaller area of 59.5 sq. deg., we choose to extrapolate what these errors would be on this larger area using root-N statistics. This gives us estimated errors of:

* *&sigma;*(*m*<sub>1</sub>) = 3.29 x 10^-4
* *&sigma;*(*m*<sub>2</sub>) = 3.28 x 10^-4
* *&sigma;*(*c*<sub>1</sub>) = 5.24 x 10^-6
* *&sigma;*(*c*<sub>2</sub>) = 5.23 x 10^-6

All of these values exceed the requirements, though in the case of the errors on additive bias, the excess is very slight (less than 5 percent of the required value for both components). Given that there are known data quality issues affecting some of the data used here, such as poor astrometric solutions for certain observations, it is possible that the additive bias requirement would be met if these issues were resolved and the test re-run.

With this in mind, we decide to deem this test a failure in the case of multiplicative bias, and a partial success in the case of additive bias.
