# SPR-TC-SHE-100023-gal-info-out-001

## Summary

**Test dataset:** [TD-SHE-000001-SHE-analysis](TD-SHE-000001-SHE-analysis.html)

**Test procedure:** The SHE Analysis pipeline was run on this observation. The resulting shear estimates table for LensMC was manually inspected for data quality issues.

**Test result:** **OK** with warnings

## Requirement Interpretation

This test validates Requirement R-SHE-PRD-F-180, which states:

**R-SHE-PRD-F-180:** For each galaxy used in the weak lensing analysis up to the limiting magnitude the following information should be available:

1. At least 1 ellipticity measurement such that a shear estimate can be inferred.
2. The posterior probability distribution of the true ellipticity given the data
3. The posterior probability distribution of the photometric redshift given the data
4. Estimate of the covariance between photometric redshift and ellipticity (TBD)
5. The classification star / galaxy
6. Confidence level and quality assessment
7. At least one size measurement

Due to design changes since the adoption of this requirement, we have adopted the following modifications and clarifications to these points, from the perspective of what PF-SHE is tasked with testing:

1. At least 1 ellipticity measurement such that a shear estimate can be inferred.
    * No modification or interpretation necessary
2. The posterior probability distribution of the true ellipticity given the data
    * Either a 1&sigma; error of the shear estimate or an inverse-variance weight of it should be provided
3. The posterior probability distribution of the photometric redshift given the data
    * This portion of the requirement is not to be tested by PF-SHE
4. Estimate of the covariance between photometric redshift and ellipticity (TBD)
    * Due to design changes, shear estimates are now provided conditioned on the bin assignments provided by PHZ. No value in the output measurements table from PF-SHE is necessary to indicate this
5. The classification star / galaxy
    * This may take the form of either a flag identifying star / galaxy / unknown or a probability estimate that the object is a galaxy
6. Confidence level and quality assessment
    * Flags should be provided indicating any problems which arise in the analysis of individual objects
7. At least one size measurement
    * The size measurement may be of any nature, as long it is properly documented

We further interpret that this requirement is met if a table is provided containing columns for all required information, and that for each object, either:
* Values are provided for all required information; or
* The object is flagged as a failed measurement

## Detailed test results

Columns are provided in the output shear measurements table indicating all required data.

All required information is present (no *NaN* values) for all galaxies which are flagged with `SHE_LENSMC_FIT_FLAGS==0`, and so this test is considered passed. However, some data quality issues with other columns were identified, which are listed here:

- The `SHE_LENSMC_TILE_ID` column contains a value of -99 for all objects. This is not a required value, and so does not constitute a test failure.

- When `SHE_LENSMC_FIT_CLASS==1` (indicating the object is fit as a star, comprising 577 objects), for a minority of objects (21), the `SHE_BULGE_FRAC` and `SHE_BULGE_FRAC_ERR` columns are set to *NaN*. This does not constitute a test failure since it is sensible that objects identified as stars would not need a bulge fraction value. However, it is inconsistent that a measured value for this is present for some of these objects but not all. The full list of objects identified as stars with *NaN* bulge fractions is:

```
       2319692232305728186, 2310728037305492379, 2309952936303741321,
       2317482641305260952, 2311576491307302369, 2311540336307216355,
       2309949125303742913, 2314066726310149124, 2309230123302554581,
       2317644277308784539, 2312073142305406908, 2312149179308601861,
       2313490419301160246, 2311942916308202307, 2317783931301837465,
       2313231028310499349, 2316159760302205268, 2310016505303935911,
       2309621539303022975, 2313380769309876970, 2313230057310493246
```

- In the case of exactly one object (`OBJECT_ID=2316211393305331917`), the `SHE_LENSMC_E1_ERR` and `SHE_LENSMC_E2_ERR` columns contain error values of 0, and the `SHE_LENSMC_SHAPE_WEIGHT` column contains a value of *NaN*. As the primary outputs are G1 and G2 errors (shear errors rather than shape errors), plus `SHE_LENSMC_SHEAR_WEIGHT`, which are reported with valid values, this does not constitute a test failure. This is a known possible corner-case of error estimation using MCMC chains, and this object has particularly high SNR (446.9), which is consistent with a low error. However, the presence of a *NaN* value for weight combined with the fact that this object's measurement was not flagged in any way leaves a potential pitfall for anyone using it, and it is recommended that either such objects be flagged or their error set to some minimum non-zero value which accounts for the limitations of error estimation inherent in this method.
