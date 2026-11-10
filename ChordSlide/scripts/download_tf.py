import urllib.request,concurrent.futures,time
from pathlib import Path
url='https://files.pythonhosted.org/packages/e0/36/6278e4e7e69a90c00e0f82944d8f2713dd85a69d1add455d9e50446837ab/tensorflow_intel-2.16.1-cp311-cp311-win_amd64.whl'
size=376955589;step=4*1024*1024
p=Path('ChordSlide/build/wheels');p.mkdir(exist_ok=True)
def part(i):
 a=i*step;b=min(size,a+step)-1
 for attempt in range(4):
  try:
   r=urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={a}-{b}'}),timeout=40);data=r.read()
   if len(data)!=b-a+1:raise ValueError('range length')
   return i,data
  except Exception:
   if attempt==3:raise
   time.sleep(1)
with (p/'tensorflow_intel-2.16.1-cp311-cp311-win_amd64.whl').open('wb') as f:
 f.truncate(size)
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for i,data in pool.map(part,range((size+step-1)//step)):f.seek(i*step);f.write(data)
print('range download complete')
