# TD-SHE-000008-SHE-reconciliation

## Summary

This testing dataset comprises the input data needed for a run of the SHE Reconciliation pipeline on a fiducial Euclid tile. The tile used for this dataset (index 90346) was chosen solely based on its early availability, and was not selected based on the performance of any of the validation tests or other scientific analysis.

When the SHE Reconciliation pipeline is run, it performs the validation tests associated with this dataset as part of its execution.

## Relevant Tests and Test Cases

* **TC-SHE-100022-gal-N-out**
* **T-SHE-000013-data-proc**

## Data Details

All data in this testing dataset is stored in the Euclid Archive Service (EAS), and can be viewed on the DBView web service (https://eas-dps-cus-ops.esac.esa.int/) or retrieved via the DataProductRetrieval.py script through querying it appropriately.

The following sections list the different types of data products required, plus the metadata values which can be used to query for them. In addition to the metadata values listed below, all queries should include ``Header.ManualValidationStatus.ManualValidationStatus!="INVALID"`` to properly exclude any invalidated data.

### Data from PF-MER

The following data products are used from PF-MER:

* `DpdMerFinalCatalog`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease=SC8_MAIN_V0`
* `Data.TileIndex=90346`

### Data from PF-SHE

The following data products are used, which are generated manually with PF-SHE to be used as input to the SHE Analysis pipeline:

* DpdSheValidatedMeasurements
  * `Header.DataSetRelease=SC8_MAIN_V0`
  * `Data.ObservationId=` Each of the following (requiring a separate query for each):
    * `10351`
    * `10352`
* DpdSheLensMcChains
  * `Header.DataSetRelease=SC8_MAIN_V0`
  * `Data.ObservationId=` Each of the following (requiring a separate query for each):
    * `10351`
    * `10352`

This comprises data for all observations which spatially overlap the chosen MER tile.
