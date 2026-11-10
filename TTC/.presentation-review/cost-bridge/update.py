from pathlib import Path
from copy import deepcopy
import re
from docx import Document
from docx.text.paragraph import Paragraph

folder = Path('E:/PY/TTC/presentation/presentation paper')
review = Path('E:/PY/TTC/.presentation-review/cost-bridge')
source = folder/'test-time-compute-25min.tex'
raw = (review/'slides-before.tex').read_bytes()
assert source.read_bytes() == raw, 'Source changed since reading.'
text = raw.decode('utf-8')
frames = list(re.finditer(r'\\begin\{frame\}.*?\\end\{frame\}',text,re.S))
assert len(frames) == 24
old = [m.group() for m in frames]
assert old[15].startswith(r'\begin{frame}{Pretraining and Inference at Equal Total FLOPs}')
assert old[16].startswith(r'\begin{frame}{Using R to Compare Total Compute}')

bridge = r'''\begin{frame}{Comparing Two Uses of the Same Compute}
  \small
  Compare the same total FLOPs, counting \textbf{pretraining and inference}.
  \par\medskip
  \begin{columns}[T,onlytextwidth]
    \begin{column}{.48\textwidth}
      \keyterm{Train a larger model}
      \par\smallskip
      About 14$\times$ as many parameters.
      \par\smallskip
      Generate one greedy answer per question.
    \end{column}
    \begin{column}{.48\textwidth}
      \keyterm{Use more inference}
      \par\smallskip
      Keep the smaller model.
      \par\smallskip
      Spend extra compute on search or revisions.
    \end{column}
  \end{columns}
  \par\medskip
  $R$ is baseline inference tokens divided by pretraining tokens.
  \par\smallskip
  For each $R$, find the small-model budget with the same total cost.
  \begin{center}
  \renewcommand{\arraystretch}{1.35}
  \begin{tabular}{@{}lccc@{}}
    \textbf{$R$} & 22 & 0.79 & 0.16\\
    \textbf{Small-model inference budget} & $\sim16\times$ & $\sim64\times$ & $\sim256\times$
  \end{tabular}
  \end{center}
  {\footnotesize Multipliers are relative to the small model's baseline inference.}
  \par\medskip
  \keyterm{These budgets locate the three stars in the next figure.}
  \note{Time 17:45--19:00. Explain the comparison in Section 7, paper pages 14--15, without deriving the FLOPs equations. Count total pretraining plus inference FLOPs for the same baseline inference workload. One option scales model parameters by about 14 while holding pretraining tokens fixed and uses greedy decoding. The other keeps the small model and uses the training savings for extra inference. R is the ratio of total baseline inference tokens to pretraining tokens; it is not itself a FLOPs cost or an inference multiplier. At each R the paper determines the small-model inference budget with the same total cost as the larger model. For R values 22, 0.79, and 0.16, these multipliers are approximately 16, 64, and 256, respectively. The R values are rounded, so the correspondence is approximate. These are the three x-axis locations used for the large-model stars in Figure 9. Each color's large-model greedy accuracy stays fixed; the stars' positions show where the cost comparison is equal. The formulas and algebra are available in the two new backup slides.}
\end{frame}'''

text = text[:frames[15].start()] + bridge + text[frames[16].end():]
text = text.replace('Time 20:30--22:15. Read Figure 9.', 'Time 19:00--21:30. Read Figure 9. Use the three matched budgets introduced on the previous slide.')
text = text.replace('Time 22:15--24:00. Summarize all three experimental parts,','Time 21:30--23:30. Summarize all three experimental parts,')
text = text.replace('Backup slides cover revision training, revision failures, beam search, and difficulty estimation.','Backup slides cover revision training, revision failures, beam search, difficulty estimation, and the full cost equations.')

moved16 = old[15].replace(r'\begin{frame}{Pretraining and Inference at Equal Total FLOPs}',r'\begin{frame}{Backup: Pretraining and Inference at Equal Total FLOPs}',1)
moved16 = moved16.replace('Time 17:45--19:15.', 'Optional backup. Section 7, paper page 14.')
moved17 = old[16].replace(r'\begin{frame}{Using R to Compare Total Compute}',r'\begin{frame}{Backup: Using R to Compare Total Compute}',1)
moved17 = moved17.replace('Time 19:15--20:30.', 'Optional backup. Section 7, paper pages 14--15.')
moved17 = moved17.replace('The next figure compares model accuracy at the matched positions.','These equations identify the equal-cost positions in the main result figure.')
assert text.count(r'\end{document}') == 1
text = text.replace(r'\end{document}', moved16+'\n\n'+moved17+'\n\n'+r'\end{document}')
new = re.findall(r'\\begin\{frame\}.*?\\end\{frame\}',text,re.S)
assert len(new) == 25
assert new[:15] == old[:15]
assert new[19:23] == old[20:24], 'Existing backup content changed.'
assert new[16].split(r'\note{')[0] == old[17].split(r'\note{')[0]
assert new[17].split(r'\note{')[0] == old[18].split(r'\note{')[0]
source.write_bytes(text.encode('utf-8'))

def set_text(p,text):
    rpr = deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    p.clear()
    r = p.add_run(text)
    if rpr is not None:
        r._r.insert(0,rpr)

main_path = folder/'test-time-compute-main-script.docx'
backup_path = folder/'test-time-compute-backup-script.docx'
assert main_path.read_bytes() == (review/'main-before.docx').read_bytes()
assert backup_path.read_bytes() == (review/'backup-before.docx').read_bytes()
main = Document(main_path)
before = [p.text for p in main.paragraphs]
start16 = next(i for i,t in enumerate(before) if t.startswith('Slide 16 '))
start17 = next(i for i,t in enumerate(before) if t.startswith('Slide 17 '))
start18 = next(i for i,t in enumerate(before) if t.startswith('Slide 18 '))
section16 = before[start16:start17]
section17 = before[start17:start18]
assert len(section16) == len(section17) == 5

body = [
    'We now compare two ways to spend the same total compute. We count pretraining and inference for the same planned workload.',
    'One option is to train a larger model and generate one greedy answer per question. The other is to keep the smaller model and spend more compute on search or revisions. The larger model has about fourteen times as many parameters. For this cost comparison, both models use the same number of pretraining tokens.',
    'We need one more quantity, R. It is the total baseline inference tokens divided by pretraining tokens. This ratio helps determine how much extra inference the small model can use at equal total cost.',
    "The paper considers three R values. R of twenty-two gives roughly sixteen times the small model's baseline inference budget. R of zero point seven nine gives about sixty-four times. R of zero point one six gives about two hundred and fifty-six times.",
    'These three budgets give the three equal-cost positions in the next figure. The larger model still gives a greedy answer. We compare its accuracy with the small-model curve at each position.'
]
ps = list(main.paragraphs)
heading_template = deepcopy(ps[start16]._element)
body_template = deepcopy(ps[start16+1]._element)
anchor = ps[start16]._element
new_section = ['Slide 16 Comparing Two Uses of the Same Compute']+body
for i,t in enumerate(new_section):
    element = deepcopy(heading_template if i == 0 else body_template)
    anchor.addprevious(element)
    set_text(Paragraph(element,main._body),t)
for p in ps[start16:start18]:
    p._element.getparent().remove(p._element)
for p in main.paragraphs:
    match = re.match(r'^Slide (18|19|20)\b',p.text)
    if match:
        set_text(p,p.text.replace('Slide '+match.group(1),'Slide '+str(int(match.group(1))-1),1))
    if p.text == '22:15 to 24:00':
        set_text(p,'21:30 to 23:30')
    if 'Each vertical line is a matched-total-cost point for one R value.' in p.text:
        set_text(p,p.text.replace('Each vertical line is a matched-total-cost point for one R value.','Each vertical line marks one of the equal-total-cost budgets from the previous slide.'))

expected = before[:start16]+new_section+before[start18:]
expected = [re.sub(r'^Slide (18|19|20)\b',lambda m:'Slide '+str(int(m.group(1))-1),t) for t in expected]
expected = [t.replace('Each vertical line is a matched-total-cost point for one R value.','Each vertical line marks one of the equal-total-cost budgets from the previous slide.') for t in expected]
expected = ['21:30 to 23:30' if t == '22:15 to 24:00' else t for t in expected]
assert [p.text for p in main.paragraphs] == expected
tmp = review/'main-updated.docx'
main.save(tmp)
assert [p.text for p in Document(tmp).paragraphs] == expected
tmp.replace(main_path)

backup = Document(backup_path)
before_backup = [p.text for p in backup.paragraphs]
heading_template = deepcopy(backup.paragraphs[2]._element)
body_template = deepcopy(backup.paragraphs[3]._element)
expected_backup = []
for p in backup.paragraphs:
    match = re.match(r'^Slide (21|22|23|24)\b',p.text)
    if match:
        set_text(p,p.text.replace('Slide '+match.group(1),'Slide '+str(int(match.group(1))-1),1))
    expected_backup.append(p.text)

for number,section in ((24,section16),(25,section17)):
    title = re.sub(r'^Slide \d+',f'Slide {number}',section[0])
    extra = [title]+section[1:]
    extra[-1] = extra[-1].replace('We can now compare accuracy at the matched positions in the next figure.','These equations give the equal-cost comparison points in the main result figure.')
    for i,t in enumerate(extra):
        element = deepcopy(heading_template if i == 0 else body_template)
        backup._body._body.insert_element_before(element,'w:sectPr')
        set_text(Paragraph(element,backup._body),t)
    expected_backup.extend(extra)
assert [p.text for p in backup.paragraphs] == expected_backup
tmp = review/'backup-updated.docx'
backup.save(tmp)
assert [p.text for p in Document(tmp).paragraphs] == expected_backup
tmp.replace(backup_path)
print('Main: one cost-comparison bridge at 16; result figure 17; conclusions 18; questions 19.')
print('Backup: existing content at 20--23; former main formulas moved to 24--25.')
print('Both speaking scripts updated; other text preserved.')
