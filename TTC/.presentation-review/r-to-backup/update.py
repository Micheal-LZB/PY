from pathlib import Path
from copy import deepcopy
import re
from docx import Document
from docx.text.paragraph import Paragraph

folder=Path('E:/PY/TTC/presentation/presentation paper')
review=Path('E:/PY/TTC/.presentation-review/r-to-backup')
source=folder/'test-time-compute-25min.tex'
before=(review/'slides-before.tex').read_bytes()
assert source.read_bytes()==before
text=before.decode('utf-8')
frames=list(re.finditer(r'\\begin\{frame\}.*?\\end\{frame\}',text,re.S))
assert len(frames)==25
old=[m.group() for m in frames]

main16=r'''\begin{frame}{Comparing Two Uses of the Same Compute}
  Compare the same total FLOPs, counting \textbf{pretraining and inference}.
  \par\bigskip
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
  \par\bigskip
  The smaller model can use its pretraining savings for extra inference.
  \par\medskip
  \keyterm{Which option gives higher accuracy at the same total cost?}
  \note{Time 17:45--19:00. Compare the two options in Section 7, paper pages 14--15. Count pretraining plus inference FLOPs for the same planned workload. The larger model has about 14 times as many parameters, uses the same pretraining token count, and generates greedy answers. The smaller model can use the pretraining savings for additional search or revisions. Ask which option gives higher accuracy at the same total cost, then move to Figure 9. Details of the token-workload ratio, numerical budget matching, and algebra are in backup slide 25.}
\end{frame}'''

backup25=r'''\begin{frame}{Backup: Using R to Compare Total Compute}
  \small
  $R$ is baseline inference tokens divided by pretraining tokens:
  \[
    R=\frac{D_{\mathrm{inference}}}{D_{\mathrm{pretrain}}}.
  \]
  From $X+aY=M(X+Y)$, the small model's inference multiplier is
  \[
    \begin{aligned}
      a &= M+(M-1)\frac{X}{Y}
       = M+(M-1)\frac{6P D_{\mathrm{pretrain}}}{2P D_{\mathrm{inference}}}\\
        &= M+3(M-1)\frac{D_{\mathrm{pretrain}}}{D_{\mathrm{inference}}}
         = M+\frac{3(M-1)}{R}.
    \end{aligned}
  \]
  \begin{center}
  \renewcommand{\arraystretch}{1.15}
  \begin{tabular}{@{}lccc@{}}
    \textbf{$R$} & 22 & 0.79 & 0.16\\
    \textbf{Small-model inference budget} & $\sim16\times$ & $\sim64\times$ & $\sim256\times$
  \end{tabular}
  \end{center}
  {\footnotesize Approximate multipliers for $M\approx14$, relative to baseline inference.}
  \par\smallskip
  \keyterm{These budgets set the stars' horizontal positions in Figure 9.}
  \note{Optional backup. Section 7, paper pages 14--15. This slide combines the full derivation with the budget examples moved out of main slide 16. R is the dimensionless ratio of total baseline inference tokens to pretraining tokens. Fix this baseline workload before adding extra inference; R is not itself a FLOPs cost or an inference multiplier. Solve X+aY=M(X+Y) for a, substitute the FLOPs approximations, cancel the parameter count, and use Dpretrain/Dinference=1/R. For M approximately 14, the paper's rounded R values 22, 0.79, and 0.16 correspond approximately to multipliers 16, 64, and 256. These budgets identify equal-total-cost positions on the x-axis of Figure 9. The large model still uses greedy decoding, so each color's star stays at the same accuracy across positions. At a fixed R, giving the small model more compute than the matched budget increases its total cost above the large model's.}
\end{frame}'''

text=text.replace(old[15],main16,1)
text=text.replace(old[24],backup25,1)
text=text.replace('Read Figure 9. Use the three matched budgets introduced on the previous slide.','Read Figure 9. Apply the equal-total-cost comparison introduced on the previous slide. Each vertical comparison line represents a different planned inference workload and its matched budget. Numerical workload ratios and their derivation remain in backup slide 25.')
new=re.findall(r'\\begin\{frame\}.*?\\end\{frame\}',text,re.S)
assert len(new)==25
assert [i for i,(a,b) in enumerate(zip(old,new),1) if a!=b]==[16,17,25]
assert re.search(r'\bR\b',new[15]) is None
assert new[16].split(r'\note{')[0]==old[16].split(r'\note{')[0]
source.write_bytes(text.encode('utf-8'))

def set_text(p,text):
    rpr=deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    p.clear()
    r=p.add_run(text)
    if rpr is not None:r._r.insert(0,rpr)

main_path=folder/'test-time-compute-main-script.docx'
backup_path=folder/'test-time-compute-backup-script.docx'
assert main_path.read_bytes()==(review/'main-before.docx').read_bytes()
assert backup_path.read_bytes()==(review/'backup-before.docx').read_bytes()
doc=Document(main_path)
ps=list(doc.paragraphs)
before=[p.text for p in ps]
s=next(i for i,t in enumerate(before) if t.startswith('Slide 16 '))
e=next(i for i,t in enumerate(before) if t.startswith('Slide 17 '))
assert e-s==6
moved_numbers=before[s+4]
moved_positions=before[s+5].replace('in the next figure','in Figure 9')
replacement="The question is which option gives higher accuracy at the same total cost. The next figure compares the larger model's greedy answers with the smaller model using extra inference."
set_text(ps[s+3],replacement)
for p in ps[s+4:e]:p._element.getparent().remove(p._element)
old_reference='Each vertical line marks one of the equal-total-cost budgets from the previous slide.'
new_reference='Each vertical line marks a setting where the two options have the same total cost.'
for p in doc.paragraphs:
    if old_reference in p.text:set_text(p,p.text.replace(old_reference,new_reference))
expected=before[:s+3]+[replacement]+before[e:]
expected=[t.replace(old_reference,new_reference) for t in expected]
assert [p.text for p in doc.paragraphs]==expected
main16_text=' '.join(expected[s:s+4])
assert re.search(r'\bR\b',main16_text) is None
tmp=review/'main-updated.docx'
doc.save(tmp)
assert [p.text for p in Document(tmp).paragraphs]==expected
tmp.replace(main_path)

doc=Document(backup_path)
before=[p.text for p in doc.paragraphs]
s=next(i for i,t in enumerate(before) if t.startswith('Slide 25 '))
assert len(before)-s==5
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
tmp=review/'backup-updated.docx'
doc.save(tmp)
assert [p.text for p in Document(tmp).paragraphs]==expected
tmp.replace(backup_path)
print('Removed the R definition and budget table from main slide 16; merged them into existing backup slide 25.')
print('Updated both scripts and removed the result-script reference to budgets on the previous slide.')
print('Slide count and numbering remain unchanged: 25 slides.')
