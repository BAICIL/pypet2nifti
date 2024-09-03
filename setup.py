from setuptools import setup, find_packages

setup(
    name='image_converter_package',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pydicom',
        'nibabel'
        'dcm2niix'
    ],
    entry_points={
        'console_scripts': [
            'pet-to-bids=cli:main',
        ],
    },
)