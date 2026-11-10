from pathlib import Path
from docx import Document

root = Path('E:/PY/TTC')
old = '''We train a process reward model, or PRM, to give the scores. It looks at the question and the reasoning up to the current step. Its score estimates how likely the base model is to finish correctly from there.

Where do the training targets come from? We keep a solution prefix and let the base model complete it several times. We check the final answers. If seven of ten completions are correct, the training target is 0.7. These numbers are an example.

After training on many such examples, the PRM can predict this value directly for a new prefix. During search, we use that learned prediction. We do not need to run all those training continuations again each time we score a candidate.'''
new = '''We train a process reward model, or PRM, to give the scores. Look first at the solid box. It contains the question and all reasoning up to the current step. We keep this prefix fixed.

From this same prefix, the base model samples four independent continuations, each all the way to a final answer. The dashed boxes and paths show these possible futures. We check the final answers against the ground truth. Three checks and one cross mean three correct answers out of four. The brace groups these results, giving 0.75 as the training target for the current prefix. Four is just an example.

We repeat this for many prefixes and train the PRM to predict these targets. During search, the trained PRM scores a new prefix directly. We do not run these four continuations again every time we need a score. The prediction estimates the chance that the base model will finish correctly from here.'''

path = root / 'presentation/presentation paper/test-time-compute-main-script.docx'
doc = Document(path)
paras = doc.paragraphs
start = next(i for i, p in enumerate(paras) if p.text == 'Slide 6 Who Can Score the Reasoning')
end = next(i for i, p in enumerate(paras[start+1:], start+1) if p.style.name == 'Heading 1')
section = paras[start:end]
for before, after in zip(old.split('\n\n'), new.split('\n\n')):
    matches = [p for p in section if p.text == before]
    assert len(matches) == 1, before
    p = matches[0]
    assert len(p.runs) == 1
    p.runs[0].text = after
doc.save(path)

builder = root / '.presentation-review/build_speaking_scripts.py'
text = builder.read_text(encoding='utf-8')
assert text.count(old) == 1
builder.write_text(text.replace(old, new), encoding='utf-8')
print('Updated only the three Slide 6 speaking paragraphs.')
