from pathlib import Path
from docx import Document

root = Path('E:/PY/TTC')
builder = root / '.presentation-review/build_speaking_scripts.py'
old_cue = 'Trace one path, then point to the shared final selection.'
new_cue = 'Point to a gray cross, then follow a retained branch through the next expansion.'
old_speech = '''This picture gives the whole process before we look at its parts. Starting from the question, the model generates possible next steps. We score the reasoning written so far and retain some candidates. Then we generate more steps from those candidates.

We repeat this process until solutions finish or the allowed number of rounds is reached. The three rows illustrate paths that survive. A search can keep several paths at the same time and produce several complete answers.

Finally, we select one answer. This leaves three questions. Who gives the scores? How do we choose the final answer? And which candidates should we keep during search? The next slides answer these questions in that order.'''
new_speech = '''Start from the question and follow the branches. The model proposes several first steps. The PRM scores each partial solution. A gray node with a cross stops here. We spend no more generation compute on that branch.

Each retained prefix can produce different next steps. We score these longer prefixes and prune again. The dots mean we repeat this process. Only surviving paths become complete answers for final selection.

Best-of-N completes all its independent candidates before selection. Here, feedback during generation decides which branches receive more compute. This leaves three questions. Who gives the scores? How do we choose the final answer? And which candidates should we retain? The next slides answer these in order.'''

path = root / 'presentation/presentation paper/test-time-compute-main-script.docx'
doc = Document(path)
paras = doc.paragraphs
start = next(i for i, p in enumerate(paras) if p.text == 'Slide 5 PRM Guided Search from Steps to an Answer')
end = next(i for i, p in enumerate(paras[start + 1:], start + 1) if p.style.name == 'Heading 1')
section = paras[start:end]
expected = ['[' + old_cue + ']'] + old_speech.split('\n\n')
replacement = ['[' + new_cue + ']'] + new_speech.split('\n\n')
for old, new in zip(expected, replacement):
    matches = [p for p in section if p.text == old]
    assert len(matches) == 1, old
    p = matches[0]
    assert len(p.runs) == 1, p.text
    p.runs[0].text = new
doc.save(path)

text = builder.read_text(encoding='utf-8')
assert text.count(old_cue) == 1
assert text.count(old_speech) == 1
builder.write_text(text.replace(old_cue, new_cue).replace(old_speech, new_speech), encoding='utf-8')
print('Updated only the Slide 5 cue and three speaking paragraphs.')
