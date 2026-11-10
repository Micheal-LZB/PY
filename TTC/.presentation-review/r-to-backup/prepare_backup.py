from pathlib import Path
from copy import deepcopy
from docx import Document
from docx.text.paragraph import Paragraph

folder=Path('E:/PY/TTC/presentation/presentation paper')
review=Path('E:/PY/TTC/.presentation-review/r-to-backup')
assert (folder/'test-time-compute-main-script.docx').read_bytes()==(review/'main-before.docx').read_bytes()
assert (folder/'test-time-compute-backup-script.docx').read_bytes()==(review/'backup-before.docx').read_bytes()
assert (review/'main-updated.docx').is_file()
main=Document(review/'main-before.docx')
ps=main.paragraphs
s=next(i for i,p in enumerate(ps) if p.text.startswith('Slide 16 '))
moved_numbers=ps[s+4].text
moved_positions=ps[s+5].text.replace('in the next figure','in Figure 9')
doc=Document(review/'backup-before.docx')
before=[p.text for p in doc.paragraphs]
s=next(i for i,t in enumerate(before) if t.startswith('Slide 25 '))
def set_text(p,text):
    rpr=deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    p.clear()
    run=p.add_run(text)
    if rpr is not None: run._r.insert(0,rpr)
new_definition=before[s+1].replace('the ratio of inference tokens to pretraining tokens','the ratio of total baseline inference tokens to pretraining tokens')
set_text(doc.paragraphs[s+1],new_definition)
template=deepcopy(doc.paragraphs[-1]._element)
for value in (moved_numbers,moved_positions):
    element=deepcopy(template)
    doc._body._body.insert_element_before(element,'w:sectPr')
    set_text(Paragraph(element,doc._body),value)
expected=before[:]
expected[s+1]=new_definition
expected += [moved_numbers,moved_positions]
assert [p.text for p in doc.paragraphs]==expected
doc.save(review/'backup-updated.docx')
assert [p.text for p in Document(review/'backup-updated.docx').paragraphs]==expected
print('Both updated scripts are prepared; original files unchanged before saving.')
