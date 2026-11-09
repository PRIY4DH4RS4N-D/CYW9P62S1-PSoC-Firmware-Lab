"""Train a small decision tree using labelled UART event records, split by session."""
import argparse
import json
import shutil
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from protocol import LABELS, FEATURES
from ml.features import baseline

ROOT=Path(__file__).resolve().parents[1]

def load(paths):
    events, labels, physical = {}, {}, set()
    for path in paths:
        for line in Path(path).read_text(encoding='utf-8').splitlines():
            r=json.loads(line)
            key=(r.get('session'),r.get('event_id'))
            if r['kind']=='metadata' and r.get('source')=='physical_uart':physical.add(r['session'])
            elif r['kind']=='event':events[key]=r
            elif r['kind']=='label':labels[key]=r['label']
    rows=[]
    for key,r in events.items():
        value=labels.get(key,r.get('label'))
        if value in LABELS and r['session'] in physical:
            rows.append((r['features'],LABELS.index(value),r['session']))
    if not rows:raise ValueError('No labelled physical UART events. Collect board sessions first.')
    return np.asarray([r[0] for r in rows],dtype=np.float32),np.asarray([r[1] for r in rows]),np.asarray([r[2] for r in rows])

def export(tree,path,trained,identity):
    t=tree.tree_
    lines=['#pragma once','#include <math.h>',f'#define FT_MODEL_TRAINED {int(trained)}',f'#define FT_MODEL_ID "{identity}"',
           'static inline unsigned char ft_predict(const float *f,float *confidence) {',
           ' for(int i=0;i<6;i++)if(!isfinite(f[i])){*confidence=0;return 255;}']
    def node(i,indent):
        if t.children_left[i]==t.children_right[i]:
            values=t.value[i][0]
            best=int(np.argmax(values))
            p=float(values[best]/sum(values))
            lines.append(f'{indent}*confidence={p:.17g};return {int(tree.classes_[best])};')
        else:
            lines.append(f'{indent}if(f[{t.feature[i]}]<={t.threshold[i]:.17g}) {{')
            node(t.children_left[i],indent+' ')
            lines.append(indent+'} else {')
            node(t.children_right[i],indent+' ')
            lines.append(indent+'}')
    node(0,' ')
    lines.append('}')
    path.write_text('\n'.join(lines)+'\n')

def fit_evaluate(x,y,groups,out,synthetic=False):
    if x.ndim!=2 or x.shape[1]!=6 or not np.isfinite(x).all():raise ValueError('invalid features')
    if set(y)!={0,1,2,3}:raise ValueError('all four labelled classes required')
    if len(set(groups))<3:raise ValueError('at least three independent recording sessions required')
    split=GroupShuffleSplit(n_splits=1,test_size=.25,random_state=42)
    train,test=next(split.split(x,y,groups))
    if set(y[train])!={0,1,2,3} or set(y[test])!={0,1,2,3}:raise ValueError('each split needs all classes; collect more sessions')
    clf=DecisionTreeClassifier(max_depth=5,min_samples_leaf=3,class_weight='balanced',random_state=42)
    clf.fit(x[train],y[train])
    pred=clf.predict(x[test])
    out.mkdir(parents=True,exist_ok=True)
    report=dict(source='SYNTHETIC SMOKE TEST ONLY' if synthetic else 'recorded physical UART events; provenance is operator asserted',features=FEATURES,
                training_sessions=sorted(set(groups[train])),test_sessions=sorted(set(groups[test])),training_events=len(train),test_events=len(test),
                classification=classification_report(y[test],pred,labels=range(4),target_names=LABELS,output_dict=True,zero_division=0),
                confusion_matrix=confusion_matrix(y[test],pred,labels=range(4)).tolist(),
                baseline=classification_report(y[test],[baseline(f) for f in x[test]],labels=range(4),target_names=LABELS,output_dict=True,zero_division=0),
                limitations='No hardware accuracy or latency claim. Grouped holdout only; collect independent people, moisture conditions and sessions.')
    (out/'evaluation.json').write_text(json.dumps(report,indent=2))
    ConfusionMatrixDisplay.from_predictions(y[test],pred,labels=range(4),display_labels=LABELS)
    plt.title(report['source'])
    plt.tight_layout()
    plt.savefig(out/'confusion_matrix.png')
    plt.close()
    export(clf,out/'model.h',not synthetic,'synthetic-smoke-only' if synthetic else 'recorded-tree-v1')
    # Both normal test vectors and decision boundaries exercise C export precision.
    vectors=list(x)
    for feature,t in zip(clf.tree_.feature,clf.tree_.threshold):
        if feature>=0:
            for val in [np.float32(t),np.nextafter(np.float32(t),np.float32(-np.inf)),np.nextafter(np.float32(t),np.float32(np.inf))]:
                row=x[0].copy();row[feature]=val;vectors.append(row)
    vectors=np.asarray(vectors,dtype=np.float32)
    np.savez(out/'parity_vectors.npz',x=vectors,pred=clf.predict(vectors),confidence=clf.predict_proba(vectors).max(axis=1))
    (out/'tree.json').write_text(json.dumps(dict(feature=clf.tree_.feature.tolist(),threshold=clf.tree_.threshold.tolist(),left=clf.tree_.children_left.tolist(),right=clf.tree_.children_right.tolist(),value=clf.tree_.value.tolist(),classes=clf.classes_.tolist())))
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('datasets',nargs='+')
    p.add_argument('--output',type=Path,default=ROOT/'ml/artifacts')
    p.add_argument('--install',action='store_true')
    a=p.parse_args()
    x,y,g=load(a.datasets)
    fit_evaluate(x,y,g,a.output)
    if a.install:shutil.copy2(a.output/'model.h',ROOT/'firmware/model.h')
    print(f'Report and portable model: {a.output}')
if __name__=='__main__':main()
