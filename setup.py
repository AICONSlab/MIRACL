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
    author_email='mgoubran@stanford.edu',
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
        'pandas==0.24.2', 'scipy==1.2.1', 'opencv-python', 'tifffile', 'nibabel', 'argparse', 'tables==3.5.2', 'allensdk',
        'lightning-python', 'multiprocessing', 'joblib', 'matplotlib==2.1', 'argcomplete', 'dipy', 'seaborn',
    ],
    entry_points={'console_scripts': ['miracl=miracl.cli:main'],
                  'gui_scripts': ['miraclGUI=miracl.miraclGUI:main']},
    keywords=[
        'neuroscience brain-atlas connectivity networks clarity mri neuroimaging allen-brain-atlas',
        'mouse-atlases medical-imaging mouse biomedical image-processing image-registration image-segmentation',
    ],
)
