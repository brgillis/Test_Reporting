# SPR-T-SHE-000010-CTI-gal-001

## Summary

**Validated Requirement(s):** R-SHE-PRD-F-140

**Relevent test or test case(s):** T-SHE-000010-CTI-gal (TC-SHE-100028-CTI-gal-SNR, TC-SHE-100029-CTI-gal-bg, TC-SHE-100030-CTI-gal-size, TC-SHE-100031-CTI-gal-col, and TC-SHE-100900-CTI-gal-tot)

**Test dataset:** [TD-SHE-000001-SHE-analysis](TD/TD-SHE-000001-SHE-analysis.html)

**Test procedure:** Estimated shear values (binned for each test case) for a given observation were regressed against the distance of the object from the readout register. The slope of the best-fit regression was compared against the expected value of zero.

**Test result:** **OK** with warnings

## Requirement Interpretation

This test validates Requirement R-SHE-PRD-F-140, which states:

**R-SHE-PRD-F-140:** The contribution to the error on the multiplicative bias (&mu;) due to the residuals of the CTI correction shall be smaller than 5x10<sup>-4</sup> (1&sigma;).

Imperfect CTI correction is in fact more likely to contribute to additive bias than to multiplicative. Given that other requirements (e.g. R-SHE-CAL-F-080) impose constraints on additive bias, we interpret this requirement to mean generally that imperfect CTI correction should contribute no statistically signifant amount of bias above a minimal threshold.

T-SHE-000010-CTI-gal tests for any statistically significant presence of a slope between measured shear and readout register distance, which is likely to occur if there is sufficient error in the CTI correction. We note imperfect CTI correction is not the only possible cause of such a slope: An imperfect telescope model fit used for the generation of PSF models could potentially cause a similar. The PSF model is tested by multiple other unit tests though, and so if this test fails, the results of those tests can be used to inform if the failure might be do instead to issues with the PSF model.

## Detailed test results

The test was run on data for a single fiducial observation, with data binned depending on the test case. We used the following definitions of parameters for binning the data:

* TC-SHE-100028-CTI-gal-SNR: Signal-to-noise ratio, defined as `FLUX_VIS_APER/FLUXERR_VIS_APER`, using data from the Final Catalog data product provided by PF-MER
* TC-SHE-100029-CTI-gal-bg: Sky background level, defined as value of the background map provided by PF-VIS as the stated position of the object, in ADU
* TC-SHE-100030-CTI-gal-size: Size, defined as size of the object's region in the segmentation map provided by PF-MER, in pixels
* TC-SHE-100031-CTI-gal-col: Colour, defined as `2.5*log10(FLUX_VIS_APER/FLUX_NIR_STACK_APER)`, using data from the Final Catalog data product provided by PF-MER
* TC-SHE-100900-CTI-gal-tot: All data is used in a single bin

The following bin limits were used for each test case, using the above parameter definitions and units:

* TC-SHE-100028-CTI-gal-SNR: 0, 3.5, 5, 7, 10, 15, 30, 1e99
* TC-SHE-100029-CTI-gal-bg: 0, 30, 35, 35.25, 36, 50, 1e99
* TC-SHE-100030-CTI-gal-size: 0, 30, 45, 75, 140, 300, 1e99
* TC-SHE-100031-CTI-gal-col: -1e99, -2.5, -2, -1.5, -1, -0.6, 1e99
* TC-SHE-100900-CTI-gal-tot: (all data)

These bin limits were selected to provide significant subsamples of the data. The test is to be deemed failed if, for any bin in which there is sufficient data to perform the test (generally at least 3 objects with well-measured shear), the slope of the shear versus the distance of objects from the readout register differs from zero by a statistically-significant margin.

While not the focus of the test, the measured intercept value was tested for consistency with zero as well. A failure in this aspect does not indicate a likely issue with CTI, and so does not constitute a failure of this test, but does indicate the presence of some other issue, and so is raised as a warning if it occurs.

The test results for each test case and bin are detailed in the tables below:

|  **Test Case** | **Bin Limits** | **Slope** | **Slope Sigma** | **Result** |
| :------------- | :------------- | :-------- | :-------------- | :--------- |
| TC-SHE-100028-CTI-gal-SNR | [0, 3.5) | (0.32 +/- 5.10) x 10<sup>-6</sup> | 0.06 | OK |
| TC-SHE-100028-CTI-gal-SNR | [3.5, 5) | (0.82 +/- 3.25) x 10<sup>-6</sup> | 0.25 | OK |
| TC-SHE-100028-CTI-gal-SNR | [5, 7) | (-0.13 +/- 2.58) x 10<sup>-6</sup> | 0.05 | OK |
| TC-SHE-100028-CTI-gal-SNR | [7, 10) | (0.32 +/- 2.24) x 10<sup>-6</sup> | 0.14 | OK |
| TC-SHE-100028-CTI-gal-SNR | [10, 15) | (-0.88 +/- 2.07) x 10<sup>-6</sup> | 0.43 | OK |
| TC-SHE-100028-CTI-gal-SNR | [15, 30) | (-0.49 +/- 1.92) x 10<sup>-6</sup> | 0.25 | OK |
| TC-SHE-100028-CTI-gal-SNR | [30, 1e99) | (2.41 +/- 1.71) x 10<sup>-6</sup> | 1.41 | OK |
| TC-SHE-100029-CTI-gal-bg | [0, 30) | N/A | N/A | N/A |
| TC-SHE-100029-CTI-gal-bg | [30, 35) | N/A | N/A | N/A |
| TC-SHE-100029-CTI-gal-bg | [35, 35.25) | N/A | N/A | N/A |
| TC-SHE-100029-CTI-gal-bg | [35.25, 36) | N/A | N/A | N/A |
| TC-SHE-100029-CTI-gal-bg | [36, 50) | (0.54 +/- 0.87) x 10<sup>-6</sup> | 0.62 | OK |
| TC-SHE-100029-CTI-gal-bg | [50, 1e99) | N/A | N/A | N/A |
