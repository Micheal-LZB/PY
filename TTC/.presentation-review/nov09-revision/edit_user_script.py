from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

root = Path('E:/PY/TTC')
target = root / 'presentation/presentation paper/test-time-compute-main-script.docx'
snapshot = root / '.presentation-review/nov09-revision/user-script-before.docx'
assert sha256(target.read_bytes()).digest() == sha256(snapshot.read_bytes()).digest(), 'The user edited the document again; reload before writing.'
doc = Document(target)

def sections(document):
    result = {}
    current = None
    for p in document.paragraphs:
        m = re.match(r'^Slide (\d+)\b', p.text)
        if m:
            current = int(m.group(1))
            result[current] = []
        if current is not None:
            result[current].append(p)
    return result

before_sections = sections(doc)
before_xml = {n: [p._p.xml for p in ps] for n, ps in before_sections.items()}
before_text = {n: [p.text for p in ps] for n, ps in before_sections.items()}

def replace_text_range(p, start, end, text):
    offset = 0
    spans = []
    for run in p.runs:
        spans.append((run, offset, offset + len(run.text)))
        offset += len(run.text)
    touched = [(run, a, b) for run, a, b in spans if b > start and a < end]
    assert touched
    first, a, b = touched[0]
    last, la, lb = touched[-1]
    if first is last:
        first.text = first.text[:start-a] + text + first.text[end-a:]
    else:
        prefix = first.text[:start-a]
        suffix = last.text[end-la:]
        first.text = prefix + text
        for run, _, _ in touched[1:-1]:
            run.text = ''
        last.text = suffix

def replace_panel(p):
    for m in reversed(list(re.finditer(r'\bpanels?\b', p.text, re.I))):
        replacement = 'figures' if m.group().lower().endswith('s') else 'figure'
        if m.group()[0].isupper():
            replacement = replacement.capitalize()
        replace_text_range(p, m.start(), m.end(), replacement)

def rewrite_section(number, title, paragraphs):
    ps = sections(doc)[number]
    header = ps[0]
    replace_text_range(header, 0, len(header.text), f'Slide {number} {title}')
    template = next(p for p in ps[1:] if p.style.name == 'Normal')
    template_ppr = deepcopy(template._p.pPr) if template._p.pPr is not None else None
    template_rpr = deepcopy(template.runs[0]._r.rPr) if template.runs and template.runs[0]._r.rPr is not None else None
    for p in ps[1:]:
        p._p.getparent().remove(p._p)
    anchor = header._p
    for text, bold in paragraphs:
        element = OxmlElement('w:p')
        if template_ppr is not None:
            element.append(deepcopy(template_ppr))
        anchor.addnext(element)
        paragraph = Paragraph(element, header._parent)
        run = paragraph.add_run(text)
        if template_rpr is not None:
            run._r.insert(0, deepcopy(template_rpr))
        if bold:
            run.bold = True
        anchor = element

rewrite_section(13, 'Revision Quality and Final Answer Accuracy', [
    ("Let's start with the left figure. For one question, the model runs four separate chains. Each chain contains sixty-four answers. To measure accuracy at round ten, we check the tenth answer in each chain. We repeat this for all 500 test questions and average the results.", False),
    ("So this figure checks the answer at a particular round. It does not select the best answer from earlier rounds. Most improvement happens in early rounds. Later, accuracy changes only a little.", False),
    ("Now look at the right figure. Suppose N is eight. For each question, parallel generation produces eight independent complete answers. Sequential generation produces eight answers in one chain, using earlier answers to write the next one. Both use the same revision model.", False),
    ("Next, we select one answer from the eight, using either weighted best-of-N or majority voting. We check that selected answer. Repeat this for all 500 questions. The vertical axis shows the percentage of questions for which the selected answer is correct.", False),
    ("There are four lines because we have two generation styles and two selection rules. First compare the two weighted best-of-N lines. Sequential is slightly higher. Then compare the two majority lines. Sequential is again slightly higher. This is the comparison we want to make.", False),
    ("Conclusions shown on the slide", True),
    ("Most improvement happens in early rounds.", False),
    ("Sequential is slightly better with either selector.", False),
])

rewrite_section(17, 'Expected Use Determines the Extra Inference Budget', [
    ("R compares the tokens we expect to generate after training with the tokens used during pretraining. It covers all planned use of the model. It is not just the length of one answer.", False),
    ("The previous slide gives the equal-cost equation. We solve it for a, which tells us how many times the usual inference compute the small model can use. Then we replace X and Y with their cost formulas. Six divided by two gives three, and the parameter count cancels. The training-to-inference token ratio is one divided by R. This gives the final formula.", False),
    ("Low R means relatively little planned use. For example, we may only generate a small batch of data to improve the model. The training savings can support much more compute for each answer.", False),
    ("High R means heavy planned use, such as a public chatbot serving many users over time. The same savings must support many answers, so there is less extra compute for each one.", False),
])

for p in doc.paragraphs:
    replace_panel(p)

after_sections = sections(doc)
for n, ps in after_sections.items():
    if n in (13, 17):
        continue
    if n in (14, 18):
        expected = [re.sub(r'\bpanel\b', 'figure', t) for t in before_text[n]]
        assert [p.text for p in ps] == expected, n
    else:
        assert [p._p.xml for p in ps] == before_xml[n], f'Unrequested change in Slide {n}'

assert not any(re.search(r'\bpanels?\b', p.text, re.I) for p in doc.paragraphs)
assert not any('gains level off' in p.text for p in doc.paragraphs)
doc.save(target)

source = root / 'presentation/presentation paper/test-time-compute-25min.tex'
text = source.read_text(encoding='utf-8')
text = re.sub(r'\bpanels\b', 'figures', text)
text = re.sub(r'\bpanel\b', 'figure', text)
source.write_text(text, encoding='utf-8')
print('Rewrote only Slides 13 and 17 in the user document.')
print('Changed panel to figure in Slides 14 and 18 without changing other text.')
print('All other slide sections, including Pass and the empty Slide 12, preserved exactly.')
