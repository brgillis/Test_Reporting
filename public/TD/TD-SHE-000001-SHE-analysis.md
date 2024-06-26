# TD-SHE-000001-SHE-analysis

## Summary

This testing dataset comprises the input data needed for a run of the SHE Analysis pipeline on a fiducial Euclid observation. The observation used for this dataset was chosen solely based on its early availability, and was not selected based on the performance of any of the validation tests or other scientific analysis.

When the SHE Analysis pipeline is run, it performs the validation tests associated with this dataset as part of its execution.

## Relevant Tests and Test Cases

* **T-SHE-000001-PSF-res-star-pos** (all test cases except epoch)
* **TC-SHE-100023-gal-info-out**
* **T-SHE-000009-CTI-PSF** (all test cases except epoch)
* **T-SHE-000010-CTI-gal** (all test cases except epoch)

## Data Description

The data included in this testing dataset consists of:
* Simulated Euclid VIS-channel images and associated data for a single observation (0.5 sq. deg of spatial coverage), processed by PF-VIS
* Object catalogs and segmentation maps generated by PF-MER through processing the above VIS-channel images, for all tiles overlapping the selected observation
* Training data for PF-SHE's shear estimation methods
* A pipeline configuration data product, which provides configuration parameters to tasks with the SHE Analysis pipeline
* A Mission Database file

Of note, we detail here the object selection performed on the catalog provided by PF-MER:
* The PSF Model Fitting task uses a selection of the 5 highest-S/N objects identified as stars in the catalog
* The PSF Model Generation task and Shear Estimation tasks process all objects which are labelled in MER's catalog as being detected using only the VIS-channel data, regardless of whether these objects are labelled as stars or galaxies, and regardless of S/N. This results in a selection of 153,755 objects for this particular observation
* For validation tests, only objects for which the shear estimate is provided without any error flags are used, and these objects are separated into those believed to be galaxies, those believed to be stars, and those of an unknown type. This results in a selection of 82,399 well-measured galaxies for this particular observation, of which 78,975 are believed to be galaxies and 534 are believed to be stars.

## Data Details

All data in this testing dataset is stored in the Euclid Archive Service (EAS), and can be viewed on the DBView web service (https://eas-dps-cus-ops.esac.esa.int/) or retrieved via the DataProductRetrieval.py script through querying it appropriately.

The following sections list the different types of data products required, plus the metadata values which can be used to query for them. In addition to the metadata values listed below, all queries should include ``Header.ManualValidationStatus.ManualValidationStatus!="INVALID"`` to properly exclude any invalidated data.

### Data from PF-VIS

The following data products are used from PF-VIS:

* `DpdVisCalibratedFrame`
* `DpdVisStackedFrame`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease=SC8_MAIN_V0`
* `Data.ObservationSequence.ObservationId=25463`

### Data from PF-MER

The following data products are used from PF-MER:

* `DpdMerFinalCatalog`
* `DpdMerSegmentationMap`

The specific products used for this test can be retrieved by querying for each of the above products with the specific metadata values:

* `Header.DataSetRelease=SC8_MAIN_V0`
* `Data.TileIndex=` Each of the following (requiring a separate query for each):
  * `78831`
  * `78832`
  * `78833`
  * `79170`
  * `79171`
  * `79172`
  * `79509`
  * `79510`
  * `79511`

This comprises data for all MER tiles which spatially overlap the chosen VIS observation.

### Data from PF-SHE

The following data products are used, which are generated manually with PF-SHE to be used as input to the SHE Analysis pipeline:

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
