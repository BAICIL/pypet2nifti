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

convert-to-nifti [-h] --source_data SOURCE_DATA --destination_folder <br>
                        DESTINATION_FOLDER [--subject_id SUBJECT_ID] <br>
                        [--session_id SESSION_ID] [--tracer TRACER] <br>
                        [--run_id RUN_ID] [--apply_filter] <br>
                        [--scanner_type SCANNER_TYPE] <br>
                        [--filter_size FILTER_SIZE FILTER_SIZE FILTER_SIZE] <br>

Convert DICOM or ECAT images to NIfTI format with sidecar json file. <br>

options: <br>
  &nbsp;&nbsp;&nbsp;&nbsp;-h, --help<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show this help message and exit<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--source_data SOURCE_DATA<br>    
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Path to the source DICOM or ECAT data.<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--destination_folder DESTINATION_FOLDER<br>     
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Destination folder for the converted NIfTI file.<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--subject_id SUBJECT_ID<br>     
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Subject ID for the output file naming.<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--session_id SESSION_ID<br>     
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Session ID for the output file naming.<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--tracer TRACER<br>       
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Tracer information for the output file naming.<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--run_id RUN_ID<br>       
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Run ID for the output file naming.<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--apply_filter<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Apply filter during conversion if needed.<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--scanner_type SCANNER_TYPE<br>     
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Type of scanner used (if applicable).<br>
  <br>
  &nbsp;&nbsp;&nbsp;&nbsp;--filter_size FILTER_SIZE_X FILTER_SIZE_Y FILTER_SIZE_Z<br>     
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;specify the 3 float values for the filter size in 3 dimensions.<br>

*NOTE:* 
* In case of ECAT data provide the path with the file name.
* In case of DICOM data provide the path to the folder where DICOM files reside.
* If `--apply_filter` is `True`, then provide arguments for either `--scanner_type` or `--filter_size`.
* In the pypet2nifti folder there is a `scanner_filter.json` files which provide filter size for some typical scanners.

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

