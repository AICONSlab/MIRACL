#! /usr/bin/env python
# Maged Goubran @ 2017, mgoubran@stanford.edu 

# coding: utf-8 

import os
import subprocess
import sys
from pathlib import Path
from PyQt4 import QtGui, QtCore


# from collections import defaultdict

class HorzTabBarWidget(QtGui.QTabBar):
    def __init__(self, parent=None, *args, **kwargs):
        self.tabSize = QtCore.QSize(kwargs.pop('width', 100), kwargs.pop('height', 25))
        QtGui.QTabBar.__init__(self, parent, *args, **kwargs)

    def paintEvent(self, event):
        painter = QtGui.QStylePainter(self)
        option = QtGui.QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(10)
            painter.drawControl(QtGui.QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, QtCore.Qt.AlignVCenter | \
                             QtCore.Qt.TextDontClip,
                             self.tabText(index))
        painter.end()

    def tabSizeHint(self, index):
        return self.tabSize


class HorzTabWidget(QtGui.QTabWidget):
    def __init__(self, parent, *args):
        QtGui.QTabWidget.__init__(self, parent, *args)
        self.setTabBar(HorzTabBarWidget(self))


# nestedict = lambda: defaultdict(nestedict)
# treedict = nestedict()

modules = ['Workflows', 'Conversion', 'Registration', 'Connectivity', 'STA', 'Labels', 'Segmentation', 'Statitstics',
           'Utilities', 'Help']

nestedict = {

    'Workflows': {
        'folder': 'flow',
        'functions': {
            0: {
                'name': 'CLARITY-Allen Registration',
                'script': 'miracl_workflow_registration_clarity-allen_wb.sh',
                'helpmsg': 'Wrapper for registering CLARITY data to Allen Reference brain atlas'
            },
            1: {
                'name': 'CALRITY STA',
                'script': 'miracl_workflow_sta.sh',
                'helpmsg': 'Wrapper for structure tensor analysis (STA), uses registered labels to create'
                           '\nseed & brain masks, then runs STA tracing'
            },
            2: {
                'name': 'CLARITY segmentation',
                'script': 'miracl_workflow_segmentation_clarity.sh',
                'helpmsg': 'Wrapper for segmentation, segments neurons in cleared mouse brain of sparse or nuclear'
                           '\nstains in 3D, voxelizes the results and computes cellular features'
            },
            3: {
                'name': 'Multiple mice',
                'script': 'miracl_workflow_multiple_mice.sh',
                'helpmsg': 'Wrapper for running a MIRACL script on multiple mice'
            }
        }
    },

    'Conversion': {
        'folder': 'io',
        'functions': {
            0: {
                'name': 'Tiff to Nii',
                'script': 'miracl_io_convertTIFFtoNII.py',
                'helpmsg': 'Converts a Tiff stack images to Nifti format and down-sample if chosen'
            },
            1: {
                'name': 'Dcm to Nii',
                'script': 'miracl_io_convertDCMtoNII.sh',
                'helpmsg': 'Converts dicoms in sub-directories to nii & renames sub-directories with sequence name'
            }
        }
    },

    'Registration': {
        'folder': 'reg',
        'functions': {
            0: {
                'name': 'CLARITY-Allen',
                'script': 'miracl_reg_clar-allen_whole_brain.sh',
                'helpmsg': 'Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas & warps'
                           '\nAllen annotations to the original high-res CLARITY space, and CLARITY to Allen space'
            },
            1: {
                'name': 'MRI-Allen',
                'script': 'miracl_reg_mri-allen.sh',
                'helpmsg': 'Registers in-vivo or ex-vivo MRI data to Allen Reference mouse brain Atlas &'
                           '\nwarps Allen annotations to the MRI space'
            },
            2: {
                'name': 'Warp CLARITY to Allen',
                'script': 'miracl_reg_warp_clar_data_to_allen.sh',
                'helpmsg': 'Warps downsampled CLARITY data/channels from native space to Allen atlas'
            },
            3: {
                'name': 'Warp MRI to Allen',
                'script': 'miracl_reg_warp_mr_data_to_allen.sh',
                'helpmsg': 'Warps MRI data from native space to Allen atlas'
            },
            4: {
                'name': 'Check registration results',
                'script': 'miracl_reg_check_results.py',
                'helpmsg': 'Checks registration results in a chosen space with a chosen visualizaiton software'
            }
        }
    },

    'Connectivity': {
        'folder': 'connect',
        'functions': {
            0: {
                'name': 'Label projection density',
                'script': 'miracl_connect_label_graph_proj_dens.py',
                'helpmsg': 'Query Allen connectivity API for injection experiments & finds the experiment'
                           '\nwith highest projection volume'
            },
            1: {
                'name': 'ROI connectogram',
                'script': 'miracl_connect_ROI_matrix_connectogram.py',
                'helpmsg': 'Finds the largest N Allen labels in the Region of Interest and extracts its N closely '
                           '\nconnected regions from the Allen Connectivity atlas'
            },
            2: {
                'name': 'CSD tractography',
                'script': 'miracl_connect_csd_tractography.sh',
                'helpmsg': 'Performs CSD tractography and track density mapping for a seed region using MRtrix3'
            }
        }
    },

    'STA': {
        'folder': 'sta',
        'functions': {
            0: {
                'name': 'Trace primary fibers',
                'script': 'miracl_sta_track_primary_eigen.sh',
                'helpmsg': 'Performs Structure Tensor Analysis (STA) on CLARITY viral tracing or stains'
            }
        }
    },

    'Labels': {
        'folder': 'lbls',
        'functions': {
            0: {
                'name': 'Get labels statistics',
                'script': 'miracl_lbls_stats.py',
                'helpmsg': 'Extract volumes of labels of interest and their subdivisions from input label file'
            },
            1: {
                'name': 'Warp to CALRITY',
                'script': 'miracl_lbls_warp_to_clar_space.sh',
                'helpmsg': 'Warps Allen annotations to the original high-res CLARITY space'
            },
            2: {
                'name': 'Warp to MRI',
                'script': 'miracl_lbls_warp_to_mri_space.sh',
                'helpmsg': 'Warps Allen annotations to the MRI space'
            },
            3: {
                'name': 'Generate Grand-parent at certain depth',
                'script': 'miracl_lbls_generate_parents_at_depth.py',
                'helpmsg': 'Generate parents labels at specific depth from Allen labels'
            },
            4: {
                'name': 'Generate Grand-parent annotations',
                'script': 'miracl_lbls_generate_grand-parent_annotation.py',
                'helpmsg': 'Generate multi-resolution atlases from Allen labels'
            },
            5: {
                'name': 'Get Grand-parent volumes',
                'script': 'miracl_lbls_get_gp_volumes.py',
                'helpmsg': 'Extract volumes of labels of interest and their subdivisions from input label file'
            },
            6: {
                'name': 'Get label ontology graph info',
                'script': 'miracl_lbls_get_graph_info.py',
                'helpmsg': 'Get label info from Allen atlas ontology graph'
            }
        }
    },

    'Segmentation': {
        'folder': 'seg',
        'functions': {
            0: {
                'name': '3D segmentation',
                'script': 'miracl_seg_clarity_neurons_wrapper.sh',
                'helpmsg': 'Segments neurons in cleared mouse brain of sparse or nuclear stains in 3D'
            },
            1: {
                'name': 'Feature extraction',
                'script': 'miracl_seg_feat_extract.pyc',
                'helpmsg': 'Computes features of segmented image and summarizes them per label'
            },
            2: {
                'name': 'Voxelize segmentations',
                'script': 'miracl_seg_voxelize_parallel.py',
                'helpmsg': 'Voxelizes segmentation results into density maps with Allen atlas resolution'
            }
        }
    },

    'Statitstics': {
        'folder': 'stats',
        'functions': {
            0: {
                'name': 'Paired-ttest ipsi/contra hemispheres',
                'script': 'miracl_stats_paired_ttest_ipsi_contra.py',
                'helpmsg': 'Computes paired_ttest test between both hemispheres for all labels across mice'
            }
        }
    },

    'Utilities': {
        'folder': 'utils',
        'functions': {
            0: {
                'name': 'CLARITY intensity correction',
                'script': 'miracl_utils_int_corr_tiffs.py',
                'helpmsg': 'Performs intensity correction on CLARITY tiff data in parallel using N4'
            },
            1: {
                'name': 'Extract label from registration',
                'script': 'miracl_utils_extract_lbl.py',
                'helpmsg': 'Outputs nifti file with only chosen label'
            },
            2: {
                'name': 'Create brain mask',
                'script': 'miracl_utils_create_brainmask.py',
                'helpmsg': 'Creates brain mask (nii/nii.gz) for CLARITY data'
            }
        }
    },

    'Help': {
        'folder': 'wiki',
        'functions': {
            0: {
                'name': 'Documentation',
                'script': 'MIRACL_documentation.pdf',
                'helpmsg': 'Documentation for all modules/functions (pdf with links)'
            }
        }
    }

}


def funbutton(miracl_home, nestedictionary, module, btnnum):
    funname = nestedictionary[module]['functions'][btnnum]['name']
    btn = QtGui.QPushButton(funname)
    btn.clicked.connect(lambda: runfunc(miracl_home, nestedictionary, module, btnnum))
    btn.setToolTip(nestedict[module]['functions'][btnnum]['helpmsg'])

    return btn


def runfunc(miracl_home, nestedictionary, module, btnnum):
    folder = nestedictionary[module]['folder']
    script = nestedictionary[module]['functions'][btnnum]['script']

    if folder == "wiki":
        try:
            subprocess.check_call('xdg-open %s/%s/%s' % (miracl_home, folder, script),
                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            subprocess.check_call('open %s/%s/%s' % (miracl_home, folder, script),
                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        subprocess.check_call('%s/%s/%s' % (miracl_home, folder, script),
                              shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    app = QtGui.QApplication(sys.argv)

    mainwidget = QtGui.QWidget()
    mainwidget.resize(500, 725)

    font = QtGui.QFont('Mono', 10, QtGui.QFont.Light)
    mainwidget.setFont(font)

    mainwidget.move(QtGui.QApplication.desktop().screen().rect().center() - mainwidget.rect().center())

    gui_cli = os.path.realpath(__file__)
    miracl_home = Path(gui_cli).parents[1]

    with open('%s/version.txt' % miracl_home, 'r') as versfile:
        vers = versfile.read()
    mainwidget.setWindowTitle("MIRACL v. %s" % vers.rstrip())

    p = mainwidget.palette()
    p.setColor(mainwidget.backgroundRole(), QtCore.Qt.black)
    mainwidget.setPalette(p)

    vbox = QtGui.QVBoxLayout(mainwidget)

    pic = QtGui.QLabel()
    pixmap = QtGui.QPixmap("%s/docs/gallery/icon.png" % miracl_home)
    pixmaps = pixmap.scaled(300, 200)  # QtCore.Qt.KeepAspectRatio
    pic.setPixmap(pixmaps)
    pic.setAlignment(QtCore.Qt.AlignCenter)

    vbox.addWidget(pic)

    tabs = QtGui.QTabWidget()
    tabs.setTabBar(HorzTabBarWidget(width=150, height=50))

    for m, mod in enumerate(modules):

        widget = QtGui.QWidget()
        widget.layout = QtGui.QVBoxLayout()

        for b in range(len(nestedict[mod]['functions'])):
            btn = funbutton(miracl_home, nestedict, mod, b)
            widget.layout.addWidget(btn)

        widget.setLayout(widget.layout)

        # widget background color

        # pw = QtGui.QPalette()
        # pw.setColor(QtGui.QPalette.Background, QtCore.Qt.darkBlue)
        # widget.setPalette(pw)
        # widget.setAutoFillBackground(True)

        tabs.addTab(widget, mod)

    tabs.setTabPosition(QtGui.QTabWidget.West)

    vbox.addWidget(tabs)

    mainwidget.setLayout(vbox)
    mainwidget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
