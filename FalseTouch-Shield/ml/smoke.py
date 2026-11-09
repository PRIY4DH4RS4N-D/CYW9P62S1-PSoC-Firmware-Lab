"""Explicit artificial data for testing the training/export machinery ONLY."""
from pathlib import Path
import numpy as np
from ml.train import fit_evaluate

def main():
    rng=np.random.default_rng(17)
    x=[];y=[];g=[]
    for session in range(8):
        for label in range(4):
            for _ in range(35):
                duration=rng.uniform(100,500) if label==0 else rng.uniform(800,2500) if label==1 else rng.uniform(10,70) if label==2 else rng.uniform(80,1200)
                peak=rng.uniform(110,600)
                width=rng.integers(3,8) if label==3 else rng.integers(1,3)
                x.append([duration,peak,width,peak*width*.7,rng.uniform(0,900),duration/10+3])
                y.append(label);g.append(f'SYNTHETIC-{session}')
    out=Path(__file__).resolve().parent/'synthetic_smoke'
    fit_evaluate(np.asarray(x,dtype=np.float32),np.asarray(y),np.asarray(g),out,synthetic=True)
    print('SYNTHETIC ONLY: no physical accuracy evidence; model NOT installed in firmware')
if __name__=='__main__':main()
