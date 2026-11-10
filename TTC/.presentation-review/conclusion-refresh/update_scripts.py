from copy import deepcopy
from pathlib import Path
import hashlib
import re
from docx import Document

folder = Path('E:/PY/TTC/presentation/presentation paper')
review = Path('E:/PY/TTC/.presentation-review/conclusion-refresh')
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
main = folder / 'test-time-compute-main-script.docx'
backup = folder / 'test-time-compute-backup-script.docx'
assert digest(main) == digest(review / 'main-before.docx'), 'Main script changed since reading.'
assert digest(backup) == digest(review / 'backup-before.docx'), 'Backup script changed since reading.'

def set_text(p, text):
    properties = deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    p.clear()
    run = p.add_run(text)
    if properties is not None:
        run._r.insert(0, properties)

doc = Document(main)
before = [p.text for p in doc.paragraphs]
first = next(i for i,t in enumerate(before) if t.startswith('Slide 19 '))
last = next(i for i,t in enumerate(before) if t.startswith('Slide 21 '))
assert before[first] == 'Slide 19 Example Choosing a Model to Check Answers'
assert before[last] == 'Slide 21 Conclusions'
for p in list(doc.paragraphs)[first:last]:
    p._element.getparent().remove(p._element)

old_transition = 'Next, let us apply this accuracy-and-cost comparison to choosing a model that checks training answers.'
new_transition = 'These findings lead to the final conclusions.'
matching = [p for p in doc.paragraphs if old_transition in p.text]
assert len(matching) == 1
set_text(matching[0], matching[0].text.replace(old_transition,new_transition))

ps = doc.paragraphs
idx = next(i for i,p in enumerate(ps) if p.text == 'Slide 21 Conclusions')
assert [p.text for p in ps[idx:idx+4]] == before[last:last+4]
set_text(ps[idx], 'Slide 19 Conclusions')
set_text(ps[idx+1], '22:15 to 24:00')
body = [
    'The experiments show that a model can improve its answers with more compute at inference time. The best use of that compute changes with the question and the budget.',
    'For PRM search, beam search works better on harder questions and at low budgets. On easier questions or at high budgets, best-of-N is often better.',
    'For revisions, easy questions favor longer chains. Harder questions often need a mix: revise earlier answers, but also try several independent starts.',
    'Choosing the setting by difficulty and budget gives concrete savings. Adaptive search at sixteen generations nearly matches best-of-N at sixty-four. Adaptive revisions with sixty-four generations can beat parallel best-of-N with two hundred and fifty-six. These budgets exclude the compute used to estimate difficulty.',
    'Finally, at equal total compute for pretraining and inference, the smaller model with extra inference can beat a model with about fourteen times more parameters. This works on questions within its capabilities and often with a low inference workload. For very hard questions or a high inference workload, extra pretraining is often more effective.'
]
set_text(ps[idx+2], body[0])
set_text(ps[idx+3], body[1])
anchor = ps[idx+3]._element
template = deepcopy(anchor)
for text in body[2:]:
    new_element = deepcopy(template)
    anchor.addnext(new_element)
    from docx.text.paragraph import Paragraph
    set_text(Paragraph(new_element,doc._body),text)
    anchor = new_element
questions = [p for p in doc.paragraphs if p.text == 'Slide 22 Questions']
assert len(questions) == 1
set_text(questions[0], 'Slide 20 Questions')

expected = before[:first] + ['Slide 19 Conclusions','22:15 to 24:00'] + body + ['Slide 20 Questions'] + before[before.index('Slide 22 Questions')+1:]
expected = [t.replace(old_transition,new_transition) for t in expected]
assert [p.text for p in doc.paragraphs] == expected, 'Unexpected change outside ending.'
temp_main = review / 'main-updated.docx'
doc.save(temp_main)
assert [p.text for p in Document(temp_main).paragraphs] == expected
temp_main.replace(main)

doc = Document(backup)
before = [p.text for p in doc.paragraphs]
expected = []
changed = 0
for p in doc.paragraphs:
    m = re.match(r'^Slide (2[3-9])\b',p.text)
    text = p.text
    if m:
        text = text.replace('Slide '+m.group(1),'Slide '+str(int(m.group(1))-2),1)
        set_text(p,text)
        changed += 1
    expected.append(text)
assert changed == 7
temp_backup = review / 'backup-updated.docx'
doc.save(temp_backup)
assert [p.text for p in Document(temp_backup).paragraphs] == expected
temp_backup.replace(backup)
print('Main script: deleted old Slides 19 and 20; rewrote conclusion as Slide 19; questions now Slide 20.')
print('Backup script: renumbered seven headings to Slides 21--27; all explanation text preserved.')
