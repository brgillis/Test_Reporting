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

### Data from PF-VIS

The following data products are used from PF-VIS:

* `DpdVisCalibratedFrame`
* `DpdVisStackedFrame`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease` = `SC8_MAIN_V0`
* `Data.ObservationSequence.ObservationId` = `10351`

### Data from PF-MER

The following data products are used from PF-MER:

* `DpdMerFinalCatalog`
* `DpdMerSegmentationMap`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease` = `SC8_MAIN_V0`
* `Data.TileIndex` = Each of the following:
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
* DpdSheLensMcTraining
* DpdSheRegaussTraining
* DpdSheAnalysisConfig
