import os
import miracl.connect
import miracl.flow
import miracl.conv
import miracl.lbls
import miracl.reg
import miracl.seg
import miracl.sta
import miracl.stats
import miracl.utilfn

__all__ = ['connect', 'flow', 'conv', 'lbls', 'reg', 'seg', 'sta', 'stats', 'utilfn']

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEPENDS_DIR = os.path.abspath(os.path.join(ROOT_DIR, "..", "depends"))
ATLAS_DIR = os.path.abspath(os.path.join(ROOT_DIR, "..", "atlases"))
