from pathlib import Path
import re
import hashlib
from docx import Document

folder = Path('E:/PY/TTC/presentation/presentation paper')
review = Path('E:/PY/TTC/.presentation-review/remove-last-three')
source = folder / 'test-time-compute-25min.tex'
before = (review/'slides-before.tex').read_bytes()
assert source.read_bytes() == before
text = before.decode('utf-8')
frames = list(re.finditer(r'\\begin\{frame\}.*?\\end\{frame\}',text,re.S))
assert len(frames) == 27
assert 'Backup: Difficulty Bins and Cross-Validation' in frames[24].group()
assert 'Backup: Training Rollouts and Lookahead' in frames[25].group()
assert 'Backup: Deriving the Inference Multiplier' in frames[26].group()
new = text[:frames[24].start()] + text[frames[26].end():]
new = new.replace('Backup slides contain details on validation, rollouts, and FLOPs accounting.','Backup slides cover revision training, revision failures, beam search, and difficulty estimation.')
retained = re.findall(r'\\begin\{frame\}.*?\\end\{frame\}',new,re.S)
assert len(retained) == 24
assert [m.group() for m in frames[:19]] == retained[:19]
assert [m.group() for m in frames[20:24]] == retained[20:24]
source.write_bytes(new.encode('utf-8'))

path = folder / 'test-time-compute-backup-script.docx'
assert path.read_bytes() == (review/'backup-before.docx').read_bytes()
doc = Document(path)
ps = list(doc.paragraphs)
start = next(i for i,p in enumerate(ps) if p.text.startswith('Slide 25 '))
expected = [p.text for p in ps[:start]]
for p in ps[start:]:
    p._element.getparent().remove(p._element)
assert [p.text for p in doc.paragraphs] == expected
tmp = review/'backup-updated.docx'
doc.save(tmp)
assert [p.text for p in Document(tmp).paragraphs] == expected
tmp.replace(path)
print('Removed slides 25--27. Remaining 24 slides and backup sections 21--24 preserved.')
