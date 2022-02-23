# SPR-TC-SHE-100034-calibr-simul-001

## Summary

**Test dataset:** [TD-SHE-000012-calibr-simul](TD-SHE-000012-calibr-simul.html)

**Test procedure:** Shear bias was measured based on galaxy image simulations using a fiducial set of input parameters, and on variant simulations which each vary one of these parameters. The differences in bias between these simulations were used to estimate the expected error in bias for expected errors in these input parameters, and this was compared against requirements.

**Test result:** **POK**

## Detailed test results

This page presents only a brief summary of the test results, which are quite extensive. The full report can be found in the following document: https://www.overleaf.com/read/bytdbtjkyfkx

In this test campaign, the sensitivity of bias was tested against the following parameters:
* Intrinsic galaxy ellipticity
* Sky background level
* Galaxy disk truncation radius
* PSF model inaccuracy, modelled as:
    * Adjusting the simulated position of the M2 mirror
    * Varying PSF size through linear scaling
    * Varying PSF shape through a shear transformation

In the case of the PSF model inaccuracy tests, the test in which it is adjusted by varying the simulated position of the M2 mirror is the primary result for this validation test. The other tests were included to test the validity of existing equations to predict the bias sensitivity of shear measurements to changes in PSF size and shape, which were used to set the requirements on PSF model accuracy.

In all cases here, we compare against the allowed errors on bias interpreted from :

* *&sigma;*(*m*) < 1 x 10<sup>-4</sup>
* *&sigma;*(*c*) < 5 x 10<sup>-6</sup>

Each measured bias error reported in this SPR is the maximum error found across both polar components of *m* or *c*, and the maximum of both changing the tested value lower or higher, for the shear estimation method LensMC. Full details can be seen in Section 6 of the linked document.

### Intrinsic galaxy ellipticity

**Result:** **OK**

The sensitivities of bias to intrinsic galaxy ellipticity were calculated to be:

* *dm*/*d*(*&sigma;*(*e*)) < ~1 x 10<sup>-1</sup>
* *dc*/*d*(*&sigma;*(*e*)) < ~5 x 10<sup>-3</sup>

To meet requirements, *&sigma;*(*e*) will thus need to be constrained to errors of less than 1 x 10<sup>-3</sup>. The estimated data volume for determining *&sigma;*(*e*) will allow it to be constrained to errors of ~1 x 10<sup>-4</sup>, which is well below the required value. The test is thus considered passed for this parameter.

### Sky background level

**Result:** **NOK**

In the case of sky background level, the tested range of values approximated the expected measurement error, and so here we directly compare the measured bias differences between test and fiducial simulations to requirements. The bias errors found here at the test points at `1-sigma` distance from the fiducial points were:

* *&sigma;*(*m*) = ~5 x 10<sup>-3</sup>
* *&sigma;*(*c*) = ~8 x 10<sup>-5</sup>

Both of these values exceed requirements, and so the test is considered failed for this parameter. However, we note that the bias relationship for both *m* and *c* is approximately linear (see Figure 6.3 of the linked document), which might lead to fortuitous cancellation of bias arising from under- and over-estimation of the sky background level. Further investigation will be needed to determine the net result of this.

### Galaxy disk truncation radius

**Result:** **NOK**

In the case of galaxy disk truncation radius, the tested range of values approximated the current scientific uncertainty in the typical value (one set of points at the lower and higher likely values, and one set at the most extreme plausible values), and so here we directly compare the measured bias differences between test and fiducial simulations to requirements. The bias errors found here at the test points at the lower and higher likely values were:

* *&sigma;*(*m*) = ~3 x 10<sup>-3</sup>
* *&sigma;*(*c*) = ~2 x 10<sup>-4</sup>

Both of these values exceed requirements, and so the test is considered failed for this parameter.

### PSF model inaccuracy

**Result:** **POK** with warnings

In the case of PSF model inaccuracy, requirements have been imposed on it based on equations from Paulin-Henriksson (2009). Thus, here we test the validity of these equations.

In the first test, we alter the PSF by varying the simulated position of the M2 mirror, which is the model parameter with the most direct impact on PSF size and shape. In this test (shown in the top panels of Figures 6.8 and 6.9 of the linked document), we find that relationship between the multiplicative and additive biases and the change in PSF size and shape respectively is close to that predicted by Paulin-Henrikksson's equations, but with a slightly larger slope. In the case of multiplicative bias, the slope is approximately 50 per cent larger, and for additive bias it is approximately 30 per cent larger.

This is not an unanticipated finding, as Paulin-Henrikksson's equations rely on simplified models and do not incorporate the impact of any moments of the PSF higher than quadrupole. We thus assess the test on this parameter a partial success, as while the bias varies more strongly than expected, it is by an amount can possibly be accounted for by stricter constraints on the PSF model.

We further investigated the validity of the Paulin-Henrikksson equations by directly varying the PSF size and shape through linear scaling and a shear transformation respectively, and measuring the bias response. In both case, we found that the actual bias response was much lower than that predicted by the equations. In the case of multiplicative bias, the response was around half that predicted by the equations. In the case of additive bias, the response of the first component of bias was approximately `20%` lower than predicted, while there was almost no response of the second component to the change in ellipticity.

This implies that the Paulin-Henrikksson equations are not in general a reliable predictor of bias. In the case of the Euclid PSF and motion of the M2 mirror, the underestimate of the equations happens to be roughly cancelled out by the extra bias induced through changes to higher-order moments of the PSF. We thus add a warning to the conclusion of this test, that the Paulin-Henrikksson equations which were used to set the initial requirements are not in general reliable, and direct bias measurement (such as through this test) will be necessary.
