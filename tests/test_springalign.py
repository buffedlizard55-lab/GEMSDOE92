import numpy as np
from gems.springalign import hot_points, alignment_votes
def test_hot_points_dedupe_and_threshold():
    rc,tt = hot_points([0,0,1,2],[0,0,1,2],[50.,80.,39.,41.])
    assert rc.tolist()==[[0,0],[2,2]] and tt.tolist()==[80.,41.]
def test_alignment_votes_line_and_extension():
    shape=(21,61); pts=np.array([[10.,10.],[10.,50.]]); tt=np.array([100.,100.])
    v,meta=alignment_votes(shape,pts,tt)
    assert meta["n_pairs"]==1 and v[10,30]>0 and v[10,5]>0 and v[0,30]==0
def test_no_pairs():
    v,meta=alignment_votes((5,5), np.array([[0.,0.]]), np.array([50.]))
    assert meta["n_pairs"]==0 and not v.any()
