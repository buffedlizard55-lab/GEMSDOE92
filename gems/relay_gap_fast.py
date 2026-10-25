"""Fast relay-gap tip-density (no per-tip trig loop)."""
import numpy as np
from scipy import ndimage as ndi
STRUCT8 = np.ones((3,3), bool)
CAP_PX = 60.0
SIG_GAP=1.5
def _ep(mask):
    m=np.asarray(mask,bool)
    nb=ndi.convolve(m.astype(np.uint8), np.ones((3,3),bool).astype(np.uint8), mode="constant")-m if False else 0
    # correct
    return None
