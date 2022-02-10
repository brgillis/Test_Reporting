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

In all cases here, we compare against the allowed errors on bias:
```
|dm| < 1e-4
|dc| < 5e-6
```

### Intrinsic galaxy ellipticity

**Result:** **OK**

The sensitivities of bias to intrinsic galaxy ellipticity were calculated to be:
```
dm/d(sigma(e)) < ~1 x 10^-1
dc/d(sigma(e)) < ~5 x 10^-3
```

To meet requirements, `sigma(e)` will thus need to be constrained to errors of less than `1 x 10^-3`. The estimated data volume for determining `sigma(e)` will allow it to be constrained to errors of `~1 x 10^-4`, which is well below the required value. The test is thus considered passed for this parameter.

### Sky background level

**Result:** **NOK**

In the case of sky background level, the tested range of sky background levels approximated the expected measurement error of this value, and so here we directly compare the measured bias differences between test and fiducial simulations to requirements. The bias errors found here at the test points at `1-sigma` distance from the fiducial points was:

```
dm = ~5 x 10^-3
dc = ~8 x 10^-5
```

Both of these values exceed requirements, and so the test is considered failed for this parameter. However, we note that the bias relationship for both `m` and `c` is approximately linear (see Figure 6.3 of the linked document), which might lead to fortuitous cancellation of bias arising from under- and over-estimation of the sky background level. Further investigation will be needed to determine the net result of this.

### Galaxy disk truncation radius

### PSF model inaccuracy
