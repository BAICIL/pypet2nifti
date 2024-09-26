"""
This is a Class for converting ECAT or Dicom data to nifti format for PET

__author__ = "Dhruman Goradia"
__email__ = "dhruman.goradia2@bannerhealth.com"
__credits__ = ["OpenNeuro Team"]
__copyright__ = "Banner Alzheimer's Institute"
__version__ = "0.0.1"
__license__ = "MIT License"
"""
import os
import pathlib
import pydicom
import nibabel as nib
import numpy as np
import subprocess
from datetime import datetime
import re
from .petsidecar import sidecar_template_custom
import json
import importlib.resources as pkg_resources
import pypet2nifti
from scipy.ndimage import gaussian_filter


class Converter:
    """
    A class to convert DICOM or ECAT images to NIfTI format and generate JSON metadata.

    Attributes:
        source_data (str): Path to the source DICOM or ECAT data.
        destination_folder (str): Path to the destination folder for the converted files.
        subject_id (str): Subject ID for naming the output files.
        session_id (str): Session ID for naming the output files.
        tracer (str): Tracer information for naming the output files.
        recon (str): Reconstruction information for naming the output files.
        run_id (str): Run ID for naming the output files.
        apply_filter (bool): Flag to apply a filter during conversion.
        scanner_type (str): Type of scanner used, if applicable.
    """

    def __init__(self, source_data: str,
                 destination_folder: str,
                 subject_id: str = None,
                 session_id: str = None,
                 tracer: str = None,
                 run_id: str = None,
                 apply_filter = False,
                 scanner_type = None,
                 filter_size = []):
        """
        Initializes the Converter class with the provided parameters.

        Args:
            source_data (str): Path to the source DICOM or ECAT data.
            destination_folder (str): Path to the destination folder. 
            subject_id (str, optional): Subject ID for output naming. Defaults to None.
            session_id (str, optional): Session ID for output naming. Defaults to None.
            tracer (str, optional): Tracer information for output naming. Defaults to None.
            recon (str, optional): Reconstruction info for output naming. Defaults to None.
            run_id (str, optional): Run ID for output naming. Defaults to None.
            apply_filter (bool, optional): Apply filter during conversion. Defaults to True.
            scanner_type (str, optional): Type of scanner used. Defaults to None.
            filter_size (list, optional): Filter size in 3 dimensions. Defaults to [].
        """
        self.source_data = pathlib.Path(source_data)
        self.destination_folder = pathlib.Path(destination_folder)
        self.subject_id = subject_id
        self.session_id = session_id
        self.tracer = tracer
        self.run_id = f"_run-{run_id}" if run_id else ''
        self.apply_filter = apply_filter
        self.scanner_type = scanner_type
        self.filter_size = filter_size

        if not self.source_data.exists():
            raise FileNotFoundError(f"Source data error: {self.source_data} does not exist")

        if self.check_for_dcm2niix() != 0:
            pkged = "https://github.com/rordenlab/dcm2niix/releases"
            instructions = "https://github.com/rordenlab/dcm2niix#install"
            raise EnvironmentError(f"Dcm2niix does not appear to be installed. "
                                   f"Installation instructions can be found here: {instructions} "
                                   f"and packaged versions can be found at {pkged}")
        
        if self.source_data.is_dir():
            self.input_folder = self.source_data
            self.input_file = ''
            if self.check_dir_for_dicoms():
                self.input_format = 'dicom'
            else:
                raise Exception(f"Error: Input folder {self.input_folder} does not have any dicom files")
        else:
            self.input_folder = self.source_data.parent
            self.input_file = self.source_data.name
            if '.v' in self.input_file:
                self.input_format = 'ecat'
            else:
                raise Exception("Error: Invalid source data. Source data can be Dicom folder or ECAT file with '.v' extension.")

        if self.input_format == 'dicom':
            self.header = self.extract_dicom_headers()
            self.subheaders = None
        elif self.input_format == 'ecat':
            self.header, self.subheaders = self.extract_ecat_header_subheaders()
        else:
            raise Exception(f"Something is wrong with the data. Check the data and retry")
        
        if self.subject_id is None:
            if self.input_format == 'dicom':
                self.subject_id = self.header[0].get('PatientID', '')
            elif self.input_format == 'ecat':
                self.subject_id = self.header.get('patient_id', '')
            else:
                self.subject_id = ''
        if self.subject_id == '':
            raise Exception("Subject ID information could not be extracted from the header.\nUser needs to provide it.")
        
        if self.session_id is None:
            if self.input_format == 'dicom':
                self.session_id = self.header[0].get('StudyDate', '')
            elif self.input_format == 'ecat':
                self.session_id = self.convertdatetime(self.header.get('scan_start_time', ''))[:8]
            else:
                self.session_id = ''
        if self.session_id == '':
            raise Exception("Session ID information could not be extracted from the header.\nUser needs to provide it.")
        
        if self.tracer is None:
            if self.input_format == 'dicom':
                self.tracer = re.sub(r'\[.*?\]', '', self.header[0].RadiopharmaceuticalInformationSequence[0].get('Radiopharmaceutical', None)).upper()
            elif self.input_format == 'ecat':
                self.tracer = self.header.get('radiopharmaceutical', '')
            else:
                self.tracer = ''
        if self.tracer == '':
            raise Exception("Tracer information could not be extracted from the header.\nUser needs to provide it.")
        
        self.output_folder = pathlib.Path(self.destination_folder) / f'sub-{self.subject_id}' / f'ses-{self.session_id}' / self.tracer
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.output_file = f'sub-{self.subject_id}_ses-{self.session_id}_tracer-{self.tracer}{self.run_id}_PET'

    @staticmethod
    def check_for_dcm2niix():
        """
        Checks if the dcm2niix tool is installed on the system.

        Returns:
            int: Status code of the dcm2niix command (0 if present).
        """
        check = subprocess.run(["dcm2niix", "-h"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return check.returncode
    
    @staticmethod
    def convertdatetime(timestamp):
        """
        Convert an integer timestamp to date time fromat.
        The output format is yyyymmddHHMMSS

        Args:
            timestamp (int): Timestamp in integer format.

        Returns:
            formatted_dt (str): Date time formatted string.
        """
        if timestamp is not None:
            dt = datetime.fromtimestamp(timestamp)
            formatted_dt = dt.strftime('%Y%m%d%H%M%S')
            return str(formatted_dt)
        else:
            return None

    def check_dir_for_dicoms(self):
        """
        Checks if the input folder contains at least one valid DICOM file.

        Returns:
            bool: True if at least one DICOM file is found, False otherwise.
        """
        return any(
            self.is_dicom_file(self.input_folder / f)
            for f in os.listdir(self.input_folder)
            if os.path.isfile(self.input_folder / f)
        )

    def is_dicom_file(self, file_path):
        """
        Helper function to determine if a file is a valid DICOM file.

        Args:
            file_path (Path): Path to the file to be checked.

        Returns:
            bool: True if the file is a valid DICOM, False otherwise.
        """
        try:
            pydicom.dcmread(file_path, stop_before_pixels=True)
            return True
        except pydicom.errors.InvalidDicomError:
            return False
        except Exception:
            return False  # Handle other potential exceptions gracefully

    def extract_dicom_headers(self):
        """
        Extracts DICOM headers from files in the input folder and sorts them by instance number.

        Returns:
            list: A sorted list of DICOM headers.
        """
        files = [f for f in os.listdir(self.input_folder) if os.path.isfile(os.path.join(self.input_folder, f))]
        dicom_headers = []
        for f in files:
            try:
                dicom_header = pydicom.dcmread(os.path.join(self.input_folder, f), stop_before_pixels=True)
                dicom_headers.append(dicom_header)
            except pydicom.errors.InvalidDicomError:
                pass
        sorted_dicom_headers = sorted(dicom_headers, key=lambda x: x.InstanceNumber)
        return sorted_dicom_headers
    
    def extract_ecat_header_subheaders(self):
        """
        Extracts Ecat header and subheaders and converts it to dictionary
        
        Returns:
            header: Ecat header information
            subheaders: Ecat sub-headers information
        """
        try:
            ecat_data = nib.ecat.load(self.source_data)
        except nib.filebasedimages.ImageFileError as err:
            raise err
        
        header = {}
        for key, value in dict(ecat_data.header).items():
            if isinstance(value, np.ndarray):
                header[key] = value.tolist().decode(errors='ignore') if isinstance(value.tolist(), bytes) else value.tolist()
            elif isinstance(value, bytes):
                header[key] = value.decode(errors='ignore')
            else:
                header[key] = value

        subheaders = []
        for subheader in ecat_data.get_subheaders().subheaders:
            holder = {}
            subheader_values = subheader.tolist()
            subheader_dtypes = subheader.dtype.descr
            for i in range(len(subheader_values)):
                holder[subheader_dtypes[i][0]] = subheader_values[i].decode(errors='ignore') if isinstance(subheader_values[i], bytes) else subheader_values[i]
            subheaders.append(holder)
        
        return header, subheaders
    def filter_image(self):
        """
        This function filters the image so that the effect smoothing is 8x8x8 mm3. This is done to 
        harmonize the data across different scanners. 

        Raises:
            fe: FileNotFound Error
            ie: ImageFileError from nibabel exceptions.
            e: Other Exceptions
            ValueError: Error in input values
        """
        file_path = pathlib.Path(self.output_folder) / f"{self.output_file}.nii.gz"
        try:
            img = nib.load(file_path)
            data = img.get_fdata()
        except FileNotFoundError as fe:
            raise fe
        except nib.filebasedimages.ImageFileError as ie:
            raise ie
        except Exception as e:
            raise e    
        fwhm = np.array(self.filter_size)
        if np.any(fwhm > 8):
            raise ValueError("Filter size in any dimensions should not be greater than 8")
        sigma = fwhm / 2.355
        voxel_size = np.abs(np.diag(img.affine))[:3]
        sigma_voxel = sigma / voxel_size
        try:
            if data.ndim == 3:
                smoothed_data = gaussian_filter(data, sigma=sigma_voxel)
            elif data.ndim == 4:
                smoothed_data = np.zeros_like(data)
                for t in range (data.shape[3]):
                    smoothed_data[:, :, :, t] = gaussian_filter(data[:, :, :, t], sigma=sigma_voxel)
            else:
                raise ValueError("Input NIFTI image must be 3D or 4D.")
        except Exception as e:
            raise e
        try:
            smoothed_img = nib.Nifti1Image(smoothed_data, img.affine, img.header)
            nib.save(smoothed_img, file_path)
        except nib.filebasedimages.ImageFileError as ie:
            raise ie
        except Exception as e:
            raise e

    def make_nifti(self):
        """
        Converts the DICOM or ECAT data to NIfTI format using dcm2niix.
        If `apply_filter = True`, applies smoothing with appropriate smoothing kernel 
        based on the `scanner_type` provided to harmonize the data to 8x8x8 filter.

        Raises:
            FileNotFoundError: If the NIfTI output file is not created.
            RuntimeError: If there is an error during the conversion process.
        """

        if self.input_format == 'dicom' or self.input_format == 'ecat':
            cmd = ["dcm2niix", "-b", "n", "-z", "y", "-o", str(self.output_folder), "-f", self.output_file, str(self.source_data)]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error during DICOM to NIFTI conversion: {e}")
            output_path = pathlib.Path(self.output_folder) / f"{self.output_file}.nii.gz"
            if not output_path.exists():
                raise FileNotFoundError("Output file not created")
        else:
            raise Exception("ERROR: Something is wrong.\nIf input is not DICOM or ECAT, the program should have errored out before executing this function.")
        
        # Apply smoothing
        if self.apply_filter:
            if len(self.filter_size) == 3:
                self.filter_image()
            elif self.scanner_type is not None:
                with pkg_resources.open_text(pypet2nifti, 'scanner_filter.json') as f:
                    scanners = json.load(f)
                    if self.scanner_type in scanners.keys():
                        self.filter_size = scanners[self.scanner_type]
                    else:
                        raise Exception(f"Error: Not a valid filter type. Scanner should be one of the following:\n{list(scanners.keys())}")
                self.filter_image()
            else:
                raise Exception("Error: Provide scanner type or a valid filter size for apply smoothing")

    def make_json(self):
        """
        Generates JSON metadata based on the input format.

        Raises:
            ValueError: If the input format cannot be converted to JSON.
        """
        if self.input_format == 'dicom':
            self.dicom_json()
        elif self.input_format == 'ecat':
            self.ecat_json()
        else:
            raise ValueError(f"Format {self.input_format} cannot be converted. No JSON file generated")
    def write_json(self, sidecar):
        """
        Writes a json sidecar file with metadata

        Args:
            sidecar (dict): Dictionary of meta data for sidecar json file.

        Returns:
            None
        """
        filename = pathlib.Path(self.output_folder) / f"{self.output_file}.json"
        try:
            with open(filename, 'w') as json_file:
                json.dump(sidecar, json_file, indent=4)
        except (FileNotFoundError, IOError) as e:
            print(f"Error opening or writing to file: {e}")
        except (TypeError, ValueError) as e:
            print(f"Error serializing data to JSON: {e}")
        except Exception as e:
            print(f"An unexpected error occured: {e}")

        return None

    def dicom_json(self):
        """
        Creates the json sidecar file for DICOM inputs

        Returns:
            None
        """
        sidecar_template_custom['Manufacturer'] = self.header[0].get('Manufracturer', None)
        sidecar_template_custom['ManufacturersModelName'] = self.header[0].get('ManufacturerModelName', None)
        sidecar_template_custom['SoftwareVersions'] = self.header[0].get('SoftwareVersions', None)
        sidecar_template_custom['SeriesDescription'] = self.header[0].get('SeriesDescription', None)
        sidecar_template_custom['ProtocolName'] = self.header[0].get('ProtocolName', None)
        sidecar_template_custom['ImageType'] = list(self.header[0].get('ImageType', []))
        sidecar_template_custom['SeriesNumber'] = self.header[0].get('SeriesNumber', None)
        sidecar_template_custom['StudyDate'] = self.header[0].get('StudyDate', None)
        sidecar_template_custom['AcquisitionTime'] = self.header[0].get('AcquisitionTime', None)
        sidecar_template_custom['Radiopharmaceutical'] = self.tracer
        sidecar_template_custom['RadionuclidePositronFraction'] = float(self.header[0].RadiopharmaceuticalInformationSequence[0].get('RadionuclidePositronFraction', None))
        sidecar_template_custom['RadionuclideTotalDose'] = float(self.header[0].RadiopharmaceuticalInformationSequence[0].get('RadionuclideTotalDose', None))
        sidecar_template_custom['RadionuclideHalfLife'] = float(self.header[0].RadiopharmaceuticalInformationSequence[0].get('RadionuclideHalfLife', None))
        sidecar_template_custom['DoseCalibrationFactor'] = float(self.header[0].get('DoseCalibrationFactor', 1))
        sidecar_template_custom['Units'] = self.header[0].get('Units', None)
        sidecar_template_custom['DecayCorrection'] = self.header[0].get('DecayCorrection', None)
        sidecar_template_custom['AttenuationCorrectionMethod'] = self.header[0].get('AttenuationCorrectionMethod', None)
        sidecar_template_custom['ReconstructionMethod'] = self.header[0].get('ReconstructionMethod', None)
        nslices = self.header[0].NumberOfSlices
        if 'SUMMED' in list(self.header[0].get('ImageType', [])):
            nframes = self.header[0].NumberOfTimeSlots
        else:
            nframes = self.header[0].NumberOfTimeSlices
        nfiles = nslices * nframes
        sidecar_template_custom['DecayFactor'] = [float(self.header[i].get('DecayFactor', 1)) for i in range(0, nfiles, nslices)]
        sidecar_template_custom['FrameTimesStart'] = [(self.header[i].get('FrameReferenceTime', 0)) / 60000 for i in range(0, nfiles, nslices)]
        sidecar_template_custom['FrameDuration'] = [(self.header[i].get('ActualFrameDuration', 0)) / 60000 for i in range(0, nfiles, nslices)]
        sidecar_template_custom['FrameTimesEnd'] = [(self.header[i].get('FrameReferenceTime', 0) + self.header[i].get('ActualFrameDuration', 0)) / 60000 for i in range(0, nfiles, nslices)]
        sidecar_template_custom['SliceThickness'] = float(self.header[0].get('SliceThickness', None))
        sidecar_template_custom['ImageOrientationPatientDICOM'] = list(self.header[0].get('ImageOrientationPatient', []))
        sidecar_template_custom['ConversionSoftwareVersion'] = 'v1.0.20220505'
        sidecar_template_custom['PyPET2NIFTIVersion'] = '0.0.1'
        if self.apply_filter:
            sidecar_template_custom['Smoothed'] = 'yes'
            sidecar_template_custom['FilterSize'] = self.filter_size
        else:
            sidecar_template_custom['Smoothed'] = 'no'
            sidecar_template_custom['FilterSize'] = []
        self.write_json(sidecar_template_custom)
        return None

    def ecat_json(self):
        """
        Creates the json sidecar file for ECAT inputs

        Returns:
            None
        """
        sidecar_template_custom['ManufacturersModelName'] = self.header.get('system_type', None)
        sidecar_template_custom['SoftwareVersions'] = self.header.get('sw_version', None)
        sidecar_template_custom['SeriesDescription'] = self.header.get('study_description', None)
        sidecar_template_custom['ProtocolName'] = self.header.get('study_description', None)
        sidecar_template_custom['ImageType'] = ['ORIGINAL', 'PRIMARY']
        sidecar_template_custom['SeriesNumber'] = self.header.get('serial_number', None)
        sidecar_template_custom['StudyDate'] = self.convertdatetime(self.header.get('scan_start_time', None))[:8]
        sidecar_template_custom['AcquisitionTime'] = self.convertdatetime(self.header.get('scan_start_time', None))[8:]
        sidecar_template_custom['Radiopharmaceutical'] = self.tracer
        sidecar_template_custom['RadionuclidePositronFraction'] = ''
        sidecar_template_custom['RadionuclideTotalDose'] = self.header.get('dosage', None)
        sidecar_template_custom['RadionuclideHalfLife'] = self.header.get('isotope_halflife', None)
        sidecar_template_custom['DoseCalibrationFactor'] = self.header.get('ecat_calibration_factor', None)
        sidecar_template_custom['Units'] = self.header.get('data_units', None)
        sidecar_template_custom['DecayCorrection'] = 'START'
        sidecar_template_custom['AttenuationCorrectionMethod'] = ''
        sidecar_template_custom['ReconstructionMethod'] = self.subheaders[0].get('annotation', '')
        sidecar_template_custom['DecayFactor'] = [self.subheaders[i].get('decay_corr_fctr', 1) for i in range(len(self.subheaders))]
        sidecar_template_custom['FrameTimesStart'] = [(self.subheaders[i].get('frame_start_time',0)) / 60000 for i in range(len(self.subheaders))]
        sidecar_template_custom['FrameDuration'] = [(self.subheaders[i].get('frame_duration', 0)) / 60000 for i in range(len(self.subheaders))]
        sidecar_template_custom['FrameTimesEnd'] = [(self.subheaders[i].get('frame_start_time',0) + self.subheaders[i].get('frame_duration', 0)) / 60000 for i in range(len(self.subheaders))]
        sidecar_template_custom['SliceThickness'] = (self.subheaders[0].get('z_pixel_size', None)) * 10
        sidecar_template_custom['ImageOrientationPatientDICOM'] = []
        sidecar_template_custom['ConversionSoftwareVersion'] = 'v1.0.20220505'
        sidecar_template_custom['PyPET2NIFTIVersion'] = '0.0.1'
        if self.apply_filter:
            sidecar_template_custom['Smoothed'] = 'yes'
            sidecar_template_custom['FilterSize'] = self.filter_size
        else:
            sidecar_template_custom['Smoothed'] = 'no'
            sidecar_template_custom['FilterSize'] = []
        self.write_json(sidecar_template_custom)
        return None