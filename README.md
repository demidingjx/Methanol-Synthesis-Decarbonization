# Spatially Optimized Electrification of Methanol Production

GAMS Optimization Model + Python Figure Reproduction

## Code Availability Notice

This repository is made available for review and archival purposes only.

The source code is not licensed for reuse, modification, or redistribution 
until formal publication of the associated manuscript.

A formal open-source license will be specified upon acceptance.

------------------------------------------------------------------------

## 1. Project Overview

This repository contains the GAMS optimization model and Python post-processing scripts developed for the spatially optimized electrification of methanol production.

The framework enables:

1. Scenario-based system optimization

2. Capacity and cost analysis

3. Emission accounting

4. Figure reproduction using processed model outputs


------------------------------------------------------------------------

## 2. Reproduction Workflow

### 2.1 Run Optimization Model (Optional)

If reproducing optimization from scratch:

1.  Navigate to:

        GAMS_Methanol_op_model/

2.  Run the main `.gms` file using GAMS.

3.  Ensure the model reads input data from:

        GAMS_input_data/

4. The model will generate .gdx output files upon completion.

------------------------------------------------------------------------

### 2.2 --- Generate Figures

1.  Navigate to:

        Figure_Plotting/

2.  Convert GDX Outputs to Excel.
    Model outputs stored in .gdx format are first processed using GAMS.
    The corresponding GAMS scripts convert selected variables and parameters 
    into structured Excel files for post-processing.

    The scripts read model outputs from:

        ../GDX_documents/

3. Python scripts located in each folder are used to 
    (1) Read the processed Excel files; 
    (2) Perform data aggregation and transformation;
    (3) Calculate derived indicators; 
    (4) Organize data for visualization
    Detailed instructions for individual procedures can be found in the README file within
    each subfolder.

4. Figure Generation
    The processed datasets are then used to generate figures using Python plotting scripts.
    Figures are saved in the output directory defined within each plotting script.

------------------------------------------------------------------------

## 2.3 Reproducibility Note

GDX output files are not included in this GitHub repository due to their size.

The complete model outputs used in the manuscript are archived on Zenodo and will be made publicly available upon formal publication of the associated article.

The Zenodo record includes all processed model outputs necessary to reproduce the reported results and figures.

The DOI will be provided upon publication.
