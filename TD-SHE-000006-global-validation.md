# TD-SHE-000006-global-validation

## Summary

This testing dataset comprises the input data needed for a run of the SHE Global Validation pipeline on a set of Euclid observations which have been processed by the SHE Analysis pipeline. 

When the SHE Global Validation pipeline is run, it performs the validation tests associated with this dataset.

## Relevant Tests and Test Cases

* T-SHE-000006-shear-bias
* T-SHE-000007-pdf-eps-s
* TC-SHE-100009-PSF-res-interp-star-pos-epoch
* TC-SHE-100027-CTI-PSF-epoch
* TC-SHE-100032-CTI-gal-epoch

## Data Details

All data in this testing dataset is stored in the Euclid Archive Service (EAS), and can be viewed on the DBView web service (https://eas-dps-cus-ops.esac.esa.int/) or retrieved via the DataProductRetrieval.py script through querying it appropriately.

The following sections list the different types of data products required, plus the metadata values which can be used to query for them. In addition to the metadata values listed below, all queries should include ``Header.ManualValidationStatus.ManualValidationStatus!="INVALID"`` to properly exclude any invalidated data.

### Data from PF-VIS

The following data products are used from PF-VIS:

* `DpdVisCalibratedFrame`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease=SC8_MAIN_V0`
* `Data.ObservationSequence.ObservationId=` Each of the following (requiring a separate query for each):

```
10351, 10352, 10353, 10354, 10355, 10356, 10357, 10358, 10359, 10389, 10393, 10394, 10395, 10396, 10397, 10401, 10402, 10403,
10404, 10405, 10406, 10409, 10410, 10411, 10413, 10417, 10418, 18347, 18628, 18649, 18650, 18653, 18675, 18676, 18691, 18695,
18704, 18705, 18708, 18709, 18710, 25400, 25401, 25402, 25408, 25410, 25411, 25412, 25413, 25418, 25419, 25420, 25421, 25422,
25423, 25630, 25631, 25632, 25633, 25640, 25641, 25642, 25643, 25644, 25645, 25655, 25656, 25657, 25658, 25659, 25660, 25664,
25665, 25666, 25667, 25668, 25669, 25681, 25682, 25683, 25684, 25685, 25686, 25692, 25693, 25694, 25695, 25696, 25697, 25707,
25708, 25709, 25710, 25711, 25712, 31953, 34923, 34924, 34925, 34926, 34927, 34928, 34929, 34930, 34931, 34932, 34933, 34934,
34959, 40441, 40458, 40470, 40471, 40472, 40480, 40481, 40482, 40495, 40496
```


### Data from PF-MER

The following data products are used from PF-MER:

* `DpdMerFinalCatalog`
* `DpdMerSegmentationMap`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease=SC8_MAIN_V0`
* `Data.TileIndex=` Each of the following (requiring a separate query for each):

```

```

This comprises data for all observations which were fully processed by the SHE Analysis pipeline during Science Challenge 8.

### Data from PF-SHE

The following data products are used, which are generated manually with PF-SHE to be used as input to this pipeline:

* DpdSheKsbTraining
  * `Header.ProductId.ObjectId=2dba6df3-e4cb-4aad-b98a-e1126c7d431f`
* DpdSheLensMcTraining
  * `Header.ProductId.ObjectId=7b213d33-6c34-4a38-8523-e7ceba50411e`
* DpdSheRegaussTraining
  * `Header.ProductId.ObjectId=f97e9592-175d-4571-be14-a1eb783920d8`
* DpdSheAnalysisConfig
  * `Header.ProductId.ObjectId=she_analysis_rc_5`

Each of these products can be retrieved with the corresponding `Header.ProductId.ObjectId` valued listed above.
