from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json, hashlib
ROOT=Path(__file__).resolve().parent
names=['generative-baselines.ipynb','generative-baselines.pdf','density_forest.py',
       'requirements.txt','README.txt','moon_results.csv','digit_results.csv',
       'digit_test_scores.csv']
for name in names:
    assert (ROOT/name).is_file(), name
with ZipFile(ROOT/'ex01.zip','w',ZIP_DEFLATED) as archive:
    for name in names: archive.write(ROOT/name,arcname=name)
with ZipFile(ROOT/'ex01.zip') as archive:
    assert archive.testzip() is None
    assert archive.namelist()==names
manifest={name:{'bytes':(ROOT/name).stat().st_size,
                'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()}
          for name in names+['ex01.zip']}
(ROOT/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Verified archive:',ROOT/'ex01.zip')
print('Archive size:',(ROOT/'ex01.zip').stat().st_size,'bytes')
