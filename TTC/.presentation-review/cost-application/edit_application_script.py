from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

root = Path('E:/PY/TTC')
target = root / 'presentation/presentation paper/test-time-compute-main-script.docx'
snapshot = root / '.presentation-review/cost-application/user-script-before.docx'
assert sha256(target.read_bytes()).digest() == sha256(snapshot.read_bytes()).digest(), 'Document changed after reading; reload before editing.'
doc = Document(target)

def sections():
    result = {}
    current = None
    for p in doc.paragraphs:
        match = re.match(r'^Slide (\d+)\b', p.text)
        if match:
            current = int(match.group(1))
            result[current] = []
        if current is not None:
            result[current].append(p)
    return result

before = {n: [p._p.xml for p in ps] for n, ps in sections().items()}

def set_text(p, text):
    if p.runs:
        p.runs[0].text = text
        for run in p.runs[1:]:
            run.text = ''
    else:
        p.add_run(text)

def rewrite(number, title, texts):
    ps = sections()[number]
    header = ps[0]
    set_text(header, f'Slide {number} {title}')
    template = next(p for p in ps[1:] if p.style.name == 'Normal')
    ppr = deepcopy(template._p.pPr)
    rpr = deepcopy(template.runs[0]._r.rPr) if template.runs else None
    for p in ps[1:]:
        p._p.getparent().remove(p._p)
    anchor = header._p
    for text in texts:
        element = OxmlElement('w:p')
        if ppr is not None:
            element.append(deepcopy(ppr))
        anchor.addnext(element)
        p = Paragraph(element, header._parent)
        run = p.add_run(text)
        if rpr is not None:
            run._r.insert(0, deepcopy(rpr))
        anchor = element

rewrite(17, 'Using R to Compare Total Compute', [
    'R is the ratio of inference tokens to pretraining tokens. We use this ratio for the cost comparison. R is different from a, the small model\'s inference budget multiplier.',
    'The small-model curve tells us the accuracy at each inference budget. R tells us which budget has the same total cost as the larger model. This total includes pretraining and inference.',
    'Start with the equal-cost equation from the previous slide. Solve for a, replace X and Y with their cost formulas, and cancel the parameter count. Six divided by two gives three. The training-to-inference token ratio is one divided by R. This gives the final formula.',
    'For one fixed R, only the matched value of a gives equal total cost. If we give the small model more compute than this, its total cost becomes higher. We can now compare accuracy at the matched positions in the next figure.',
])

rewrite(19, 'Example Choosing a Model to Check Answers', [
    'Here is an application idea. Suppose we have a batch of written math answers that we want to use as training data. First, we need to check which answers are correct. Should we use a larger model once, or give a smaller model more reasoning?',
    'For routine algebra and calculation errors, the smaller model may already understand the solutions. We test it on answers with known correctness. If extra checking reaches our accuracy target with less total compute, we choose the smaller model.',
    'Now consider subtle errors in difficult proofs. If the smaller model still misses these errors after more reasoning, extra compute has not solved the capability problem. If the larger checker reaches our accuracy target within the budget, we choose the larger model.',
    'For this example, we follow the paper\'s full-cost comparison: count each checker model\'s pretraining and all its checking compute. This is an application of the decision principle. The paper did not measure these checking results.',
    'Choose the model that meets the accuracy target with less total compute.',
])

old = 'Let us follow one medium-difficulty group to see exactly how the three R values can change the result.'
new = 'Next, let us apply this accuracy-and-cost comparison to choosing a model that checks training answers.'
matches = [p for p in sections()[18] if old in p.text]
assert len(matches) == 1
set_text(matches[0], matches[0].text.replace(old, new))

for n, ps in sections().items():
    if n not in (17, 18, 19):
        assert [p._p.xml for p in ps] == before[n], f'Unexpected change to Slide {n}'
doc.save(target)

source = root / 'presentation/presentation paper/test-time-compute-25min.tex'
before_source = (root / '.presentation-review/cost-application/slides-before.tex').read_text(encoding='utf-8')
assert source.read_text(encoding='utf-8').split('\\appendix', 1)[1] == before_source.split('\\appendix', 1)[1]
print('Updated Slides 17 and 19 and the transition at the end of Slide 18.')
print('Preserved every other script section and all backup slide source.')
