# Spatially Optimized Electrification of Methanol Production

GAMS Optimization Model + Python Figure Reproduction

## Code Availability Notice

This repository is made available for review and archival purposes only.

The source code is not licensed for reuse, modification, or redistribution 
until formal publication of the associated manuscript.

A formal open-source license will be specified upon acceptance.

------------------------------------------------------------------------

## 1. Project Overview

This repository contains the optimization model and post-processing
scripts used to generate the results and figures in the associated study
on electrified methanol production.

The workflow consists of:

1.  Input data preparation\
2.  GAMS-based optimization\
3.  Export of GDX results\
4.  Python-based post-processing and figure generation\
5.  Final figure refinement and export of editable figures

------------------------------------------------------------------------

## 2. Repository Structure

    .
    ├── GAMS_input_data/
    │   Model input datasets
    │
    ├── GAMS_Methanol_op_model/
    │   Core GAMS optimization model
    │
    ├── GDX_documents/
    │   Completed GDX output files from model runs
    │
    ├── Figure_Plotting/
    │   Python scripts for figure generation
    │
    └── Origin_Figs_Editable/
        Final editable figures exported after layout adjustment

------------------------------------------------------------------------

## 3. Reproduction Workflow

### 3.1 Run Optimization Model (Optional)

If reproducing optimization from scratch:

1.  Navigate to:

        GAMS_Methanol_op_model/

2.  Run the main `.gms` file using GAMS.

3.  Ensure the model reads input data from:

        GAMS_input_data/

4.  GDX output files will be generated upon completion.

------------------------------------------------------------------------

### 3.2 --- Use Provided GDX Outputs

The completed optimization outputs used in the paper are located in:

    GDX_documents/

These files are sufficient to reproduce all reported figures without
rerunning the optimization model.

------------------------------------------------------------------------

### 3.3 --- Generate Figures

1.  Navigate to:

        Figure_Plotting/

2.  Convert GDX Outputs to Excel.
    Model outputs stored in .gdx format are first processed using GAMS.
    The corresponding GAMS scripts convert selected variables and parameters 
    into structured Excel files for post-processing.

    The scripts read model outputs from:

        ../GDX_documents/

3. Python scripts located in each folder are used to 
    (1) Read the processed Excel files; (2) Perform data aggregation and transformation;
    (3) Calculate derived indicators; (4) Organize data for visualization
    Detailed instructions for individual procedures can be found in the README file within
    each subfolder.

4. Figure Generation
    The processed datasets are then used to generate figures using Python plotting scripts.
    Figures are saved in the output directory defined within each plotting script.

------------------------------------------------------------------------

### Step 4 --- Final Figure Editing

Final layout adjustments (if required) are performed in PowerPoint, and editable versions are exported to:

    Origin_Figs_Editable/

