#!/usr/bin/env python
from setuptools import setup, find_packages

# get version from file
version_file = open('miracl/version.txt')
version = version_file.read().strip()

setup(
    name='MIRACL',
    version=version,
    description='General-purpose pipeline for MRI / CLARITY brain & connectivity analysis',
    author='Maged Goubran',
    author_email='maged.goubran@utoronto.ca',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license='GNU GENERAL PUBLIC LICENSE v3',
    url='https://github.com/mgoubran/MIRACL',  # change later
    download_url='https://github.com/mgoubran/MIRACL',
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU  General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Unix Shell',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Image Recognition',
    ],
    install_requires=[
        'numpy==1.21.6',
        'pandas==1.3.5',
        'scipy==1.6.2',
        'opencv-python==4.2.0.32',
        'tifffile==2021.11.2',
        'nibabel==4.0.2',
        'argparse==1.4.0',
        'tables==3.7.0',
        'statsmodels==0.13.0',
        'allensdk==2.15.1',
        'lightning-python==1.2.1',
        'joblib==1.2.0',
        'matplotlib==3.4.2',
        'argcomplete==2.0.0',
        'dipy==1.6.0',
        'seaborn==0.12.2',
        'pyqt5==5.15.8',
        'nipype==1.8.5',
	    'nilearn==0.9.1',
	    'scikit-learn==1.0.2',
	    'svgwrite==1.4.3',
	    'loguru==0.6.0'
        ],
    entry_points={'console_scripts': ['miracl=miracl.cli:main'],
                  'gui_scripts': ['miraclGUI=miracl.miraclGUI:main']},
    keywords=[
        'neuroscience brain-atlas connectivity networks clarity mri neuroimaging allen-brain-atlas',
        'mouse-atlases medical-imaging mouse biomedical image-processing image-registration image-segmentation',
    ],
)
