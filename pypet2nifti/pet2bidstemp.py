import nibabel as nib
import numpy as np
import subprocess as sp

# sidecar template
def sidecar():
    sidecar = {
        "Modality": "PT",
        "ImagingFrequency": 0,
        "Manufacturer": "Siemens",
        "ManufacturersModelName": "",
        "PatientPosition": "HFS",
        "ProcedureStepDescription": "",
        "SoftwareVersions": "",
        "SeriesDescription": "",
        "ProtocolName": "",
        "ImageType": [],
        "SeriesNumber": "",
        "AcquisitionTime": "",
        "Radiopharmaceutical": "",
        "RadionuclidePositronFraction": "",
        "RadionuclideTotalDose": "",
        "RadionuclideHalfLife": "",
        "DoseCalibrationFactor": "",
        "Units": "",
        "DecayCorrection": "",
        "AttenuationCorrectionMethod": "",
        "ReconstructionMethod": "",
        "DecayFactor": [],
        "FrameTimesStart": [],
        "FrameDuration": [],
        "FrameReferenceTime": [],
        "SliceThickness": "",
        "ImageOrientationPatientDICOM": [],
        "ConversionSoftware": "dcm2niix",
        "ConversionSoftwareVersion": ""
    }
    return sidecar

def ecat2nii(infile=None, outpath=None, outfile='pet')
    if filename is not None:
        cmd = ['dcm2niix -b n -o']