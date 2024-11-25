from setuptools import setup, find_packages
# Full setup configuration
setup(
    name='pypet2nifti',  
    version='0.2',  
    license='MIT License',
    description='A tool to convert DICOM and ECAT images to NIfTI format.',  
    author='Dhruman Goradia, PhD', 
    author_email='Dhruman.Goradia2@bannerhealth.com',  
    url='https://github.com/BAICIL/pypet2nifti',
    
    # Automatically find and include all packages in the project
    packages=find_packages(),  
    include_package_data=True,
    package_data={
        'pypet2nifti':['*.json'],
    },

    # List dependencies (install_requires can also directly list dependencies if requirements.txt is not used)
    install_requires=[
        'pydicom',
        'nibabel',
        'dcm2niix',
        'scipy'
    ],

    # Entry point configuration
    entry_points={
        'console_scripts': [
            'convert-to-nifti=pypet2nifti.pet_to_bids:main',  # Links the CLI script 'convert-to-nifti' to the 'main' function in cli.py
        ],
    },

    # Additional metadata
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    
    python_requires='>=3.9',  # Specifies that Python 3.9 or newer is required
)
