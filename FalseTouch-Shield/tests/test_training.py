import json
import numpy as np
import pytest
from ml.train import load,export
from ml.parity import native_exe
from sklearn.tree import DecisionTreeClassifier
import subprocess

def test_refuse_unlabelled(tmp_path):
    p=tmp_path/'empty.jsonl';p.write_text('')
    with pytest.raises(ValueError,match='No labelled'):load([p])

def test_export_boundaries(tmp_path):
    rng=np.random.default_rng(5)
    x=rng.uniform(0,1000,(300,6)).astype(np.float32)
    y=(x[:,0]>500).astype(int)+2*(x[:,2]>500)
    clf=DecisionTreeClassifier(max_depth=5,random_state=0).fit(x,y)
    export(clf,tmp_path/'model.h',False,'test-only')
    exe=native_exe(tmp_path/'model.h',tmp_path)
    rows=subprocess.run([str(exe)],input='\n'.join(' '.join(map(str,r)) for r in x),text=True,capture_output=True,check=True).stdout.splitlines()
    actual=np.asarray([list(map(float,r.split())) for r in rows])
    np.testing.assert_array_equal(actual[:,0],clf.predict(x))
    np.testing.assert_allclose(actual[:,1],clf.predict_proba(x).max(axis=1),atol=1e-7)
