# TD-SHE-000001-SHE-analysis

## Summary

This testing dataset comprises the input data needed for a run of the SHE Analysis pipeline on a fiducial Euclid observation. The observation used for this dataset was chosen solely based on its early availability, and was not selected based on the performance of any of the validation tests or other scientific analysis.

When the SHE Analysis pipeline is run, it performs the validation tests associated with this dataset as part of its execution.

## Relevant Tests and Test Cases

* **T-SHE-000001-PSF-res-star-pos** (all test cases except epoch)
* **T-SHE-000008-gal-info**
* **T-SHE-000009-CTI-PSF** (all test cases except epoch)
* **T-SHE-000010-CTI-gal** (all test cases except epoch)
* **T-SHE-000013-data-proc**

## Data Details

All data in this testing dataset is stored in the Euclid Archive Service (EAS), and can be viewed on the DBView web service (https://eas-dps-cus-ops.esac.esa.int/) or retrieved via the DataProductRetrieval.py script through querying it appropriately.

The following sections list the different types of data products required, plus the metadata values which can be used to query for them. In addition to the metadata values listed below, all queries should include ``Header.ManualValidationStatus.ManualValidationStatus!="INVALID"`` to properly exclude any invalidated data.

### Data from PF-VIS

The following data products are used from PF-VIS:

* `DpdVisCalibratedFrame`
* `DpdVisStackedFrame`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease=SC8_MAIN_V0`
* `Data.ObservationSequence.ObservationId=10351`

### Data from PF-MER

The following data products are used from PF-MER:

* `DpdMerFinalCatalog`
* `DpdMerSegmentationMap`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease=SC8_MAIN_V0`
* `Data.TileIndex=` Each of the following (requiring a separate query for each):
  * `89671`
  * `90008`
  * `90009`
  * `90010`
  * `90346`
  * `90347`
  * `90348`
  * `90685`

This comprises data for all MER tiles which spatially overlap the chosen VIS observation.

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

### Other Data

This testing dataset also includes a Mission Database (MDB) file (data product type DpdMdbDataBase), which is used as input to the run of the SHE Analysis pipeline. The specific MDB used in this dataset is identified as:

* `mdb.Header.ProductId.ObjectId=="EUC_MDB_MISSIONCONFIGURATION-DevSC8_2020-09-16T18:24:00.00Z_04"`

Only the following data files associated with the MDB are used:

* gain_params_sc8.fits
* RON_params_BIAS02.fits
