import argparse
from image_converter import Converter  # Assuming the Converter class is in a file named image_converter.py

def main():
    """
    Main function to handle command-line arguments and perform DICOM or ECAT to NIfTI conversion.

    Uses argparse to capture command-line inputs and initialize the Converter class with the provided arguments.
    """
    parser = argparse.ArgumentParser(description="Convert DICOM or ECAT images to NIfTI format.")
    parser.add_argument('--source_data', type=str, help='Path to the source DICOM or ECAT data.')
    parser.add_argument('--destination_folder', type=str, help='Destination folder for the converted NIfTI file.')
    parser.add_argument('--subject_id', type=str, default=None, help='Subject ID for the output file naming.')
    parser.add_argument('--session_id', type=str, default=None, help='Session ID for the output file naming.')
    parser.add_argument('--tracer', type=str, default=None, help='Tracer information for the output file naming.')
    parser.add_argument('--run_id', type=str, default=None, help='Run ID for the output file naming.')
    parser.add_argument('--apply_filter', action='store_true', help='Apply filter during conversion if needed.')
    parser.add_argument('--scanner_type', type=str, default=None, help='Type of scanner used (if applicable).')

    args = parser.parse_args()

    # Initialize the Converter class with the provided arguments
    converter = Converter(
        source_data=args.source_data,
        destination_folder=args.destination_folder,
        subject_id=args.subject_id,
        session_id=args.session_id,
        tracer=args.tracer,
        recon=args.recon,
        run_id=args.run_id,
        apply_filter=args.apply_filter,
        scanner_type=args.scanner_type
    )

    # Perform the NIfTI conversion
    try:
        print("Starting the conversion process...")
        converter.make_nifti()
        print("NIfTI conversion completed successfully.")

        # Generate JSON metadata if applicable
        converter.make_json()
        print("JSON metadata generation completed.")
    except Exception as e:
        print(f"An error occurred during the conversion process: {e}")


if __name__ == "__main__":
    main()