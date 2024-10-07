### pypet2nifti
Converter for PET ECAT/DICOM data to bids format

# Install

Clone the github repo:

```
git clone https://github.com/BAICIL/pypet2nifti
cd pypet2nifti
pip install .
```

# Usage

convert-to-nifti [-h] --source_data SOURCE_DATA --destination_folder
                        DESTINATION_FOLDER [--subject_id SUBJECT_ID]
                        [--session_id SESSION_ID] [--tracer TRACER]
                        [--run_id RUN_ID] [--apply_filter]
                        [--scanner_type SCANNER_TYPE]
                        [--filter_size FILTER_SIZE FILTER_SIZE FILTER_SIZE]

Convert DICOM or ECAT images to NIfTI format with sidecar json file.

options:
  -h, --help            show this help message and exit
  --source_data SOURCE_DATA
                        Path to the source DICOM or ECAT data.
  --destination_folder DESTINATION_FOLDER
                        Destination folder for the converted NIfTI file.
  --subject_id SUBJECT_ID
                        Subject ID for the output file naming.
  --session_id SESSION_ID
                        Session ID for the output file naming.
  --tracer TRACER       Tracer information for the output file naming.
  --run_id RUN_ID       Run ID for the output file naming.
  --apply_filter        Apply filter during conversion if needed.
  --scanner_type SCANNER_TYPE
                        Type of scanner used (if applicable).
  --filter_size FILTER_SIZE FILTER_SIZE FILTER_SIZE
                        specify the 3 float values for the filter size in 3
                        dimensions.

* NOTE: In case of ECAT data provide the path with the file name. In case of DICOM data provide the path to the folder where DICOM files reside. *

# Example

```
convert-to-nifti --source_data /path/to/data \
                 --destination_folder /path/to/output/folder \
                 --subject_id 1234 \
                 --session_id yr1 \
                 --tracer PIB \
                 --run_id 001 \
                 --apply_filter True \
                 --filter_size 5 5 5
```

