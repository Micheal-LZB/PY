from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
from docx import Document

root = Path('E:/PY/TTC')
target = root / 'presentation/presentation paper/test-time-compute-main-script.docx'
snapshot = root / '.presentation-review/slide11-simple/user-script-before.docx'
assert sha256(target.read_bytes()).digest() == sha256(snapshot.read_bytes()).digest(), 'The user document changed; reload before editing.'
doc = Document(target)

def sections():
    result = {}
    current = None
    for p in doc.paragraphs:
        m = re.match(r'^Slide (\d+)\b', p.text)
        if m:
            current = int(m.group(1))
            result[current] = []
        if current is not None:
            result[current].append(p)
    return result

before = {n: [p._p.xml for p in ps] for n, ps in sections().items()}
ps = sections()[11]
assert len(ps) == 4
texts = [
    'Slide 11 Less Compute Can Reach Similar Accuracy',
    'Choosing the right search setting helps us reach similar accuracy with less compute.',
    'Look at the green line, PRM best-of-N weighted, at sixty-four generations. Now look at the blue Oracle line at sixteen generations. The accuracy is almost the same. The orange Predicted line at sixteen also comes close to the green line at sixty-four.',
    'So choosing the search setting by difficulty can reduce the compute needed for a similar result. This figure does not include the compute used to estimate difficulty. Next, we let the model revise its earlier answers.',
]
for p, text in zip(ps, texts):
    assert p.runs
    p.runs[0].text = text
    for run in p.runs[1:]:
        run.text = ''
for n, other in sections().items():
    if n != 11:
        assert [p._p.xml for p in other] == before[n], n
doc.save(target)
source = root / 'presentation/presentation paper/test-time-compute-25min.tex'
old = (root / '.presentation-review/slide11-simple/slides-before.tex').read_text(encoding='utf-8')
assert source.read_text(encoding='utf-8').split('\\appendix', 1)[1] == old.split('\\appendix', 1)[1]
print('Only Slide 11 changed in the user script; all other sections and backup source preserved.')
