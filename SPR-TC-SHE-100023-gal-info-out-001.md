# SPR-TC-SHE-100023-gal-info-out-001

## Summary

**Test dataset:** [TD-SHE-000001-SHE-analysis](TD-SHE-000001-SHE-analysis.html)

**Test procedure:** The SHE Analysis pipeline was run on this observation. The resulting shear estimates table for LensMC was manually inspected for data quality issues.

**Test result:** OK

## Detailed test results

All required information is present (no `NaN` values) for all galaxies which are flagged with `SHE_LENSMC_FIT_FLAGS==0`, and so this test is considered passed. However, some data quality issues with other columns were identified, which are listed here:

- The `SHE_LENSMC_TILE_ID` column contains a value of `-99` for all objects. This is not a required value, and so does not constitute a test failure.

- When `SHE_LENSMC_FIT_CLASS==1` (indicating the object is fit as a star, comprising 577 objects), for a minority of objects (21), the `SHE_BULGE_FRAC` and `SHE_BULGE_FRAC_ERR` columns are set to `NaN`. This does not constitute a test failure since it is sensible that objects identified as stars would not need a bulge fraction value. However, it is inconsistent that a measured value for this is present for some of these objects but not all. The full list of objects identified as stars with `NaN` bulge fractions is:

```
       2319692232305728186, 2310728037305492379, 2309952936303741321,
       2317482641305260952, 2311576491307302369, 2311540336307216355,
       2309949125303742913, 2314066726310149124, 2309230123302554581,
       2317644277308784539, 2312073142305406908, 2312149179308601861,
       2313490419301160246, 2311942916308202307, 2317783931301837465,
       2313231028310499349, 2316159760302205268, 2310016505303935911,
       2309621539303022975, 2313380769309876970, 2313230057310493246
```

- In the case of exactly one object (`OBJECT_ID=2316211393305331917`), the `SHE_LENSMC_E1_ERR` and `SHE_LENSMC_E2_ERR` columns contain error values of `0`, and the `SHE_LENSMC_SHAPE_WEIGHT` column contains a value of `NaN`. As the primary outputs are G1 and G2 errors (shear errors rather than shape errors), plus `SHE_LENSMC_SHEAR_WEIGHT`, which are reported with valid values, this does not constitute a test failure. This is a known possible corner-case of error estimation using MCMC chains, and this object has particularly high SNR (`446.89276`), which is consistent with a low error. However, the presence of a `NaN` value for weight combined with the fact that this object's measurement was not flagged in any way leaves a potential pitfall for anyone using it, and it is recommended that either such objects be flagged or their error set to some minimum non-zero value which accounts for the limitations of error estimation inherent in this method.
