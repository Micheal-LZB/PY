from pathlib import Path
import re
import tempfile
import importlib.util
from pypdf import PdfReader
from pdf2image import convert_from_path
from docx import Document
from PIL import Image

root=Path('E:/PY/TTC')
review=root/'.presentation-review/r-to-backup'
folder=root/'presentation/presentation paper'
frames=lambda t:re.findall(r'\\begin\{frame\}.*?\\end\{frame\}',t,re.S)
old=frames((review/'slides-before.tex').read_text(encoding='utf-8'))
new=frames((folder/'test-time-compute-25min.tex').read_text(encoding='utf-8'))
assert len(old)==len(new)==25
assert [i for i,(a,b) in enumerate(zip(old,new),1) if a!=b]==[16,17,25]
assert re.search(r'\bR\b',new[15]) is None
assert 'Small-model inference budget' in new[24]
assert new[16].split(r'\note{')[0]==old[16].split(r'\note{')[0]
main=Document(folder/'test-time-compute-main-script.docx')
ps=[p.text for p in main.paragraphs]
s=next(i for i,t in enumerate(ps) if t.startswith('Slide 16 '))
e=next(i for i,t in enumerate(ps) if t.startswith('Slide 17 '))
assert e-s==4
assert re.search(r'\bR\b',' '.join(ps[s:e])) is None
assert not any('budgets from the previous slide' in t for t in ps)
backup=Document(folder/'test-time-compute-backup-script.docx')
assert any('R of twenty-two' in p.text for p in backup.paragraphs)
print('R removed from main slide and script; retained with numerical budgets in backup 25. Total remains 25 slides.')
pdf=root/'.presentation-review/build/ttc-r-backup-review.pdf'
reader=PdfReader(pdf)
assert len(reader.pages)==25
assert '25 / 25' in reader.pages[-1].extract_text()
warnings=[s for s in pdf.with_suffix('.log').read_text(errors='replace').splitlines() if 'Overfull' in s or 'LaTeX Error' in s]
print('Layout/error warnings:',warnings)
for n in (16,25):
    convert_from_path(str(pdf),dpi=175,first_page=n,last_page=n)[0].save(review/f'after-{n}.jpg',quality=90)

tempfile.tempdir=str(root/'.presentation-review/render-temp')
skill=Path('C:/Users/lzb/.codex/plugins/cache/openai-primary-runtime/documents/26.1105.12137/skills/documents/render_docx.py')
spec=importlib.util.spec_from_file_location('render_docx',skill)
renderer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
for part in ('main','backup'):
    path=review/f'{part}-word.pdf'
    renderer.convert_to_pdf=lambda *args,p=path,**kwargs:(str(p),'Native Microsoft Word PDF export')
    rendered=renderer.rasterize(str(folder/f'test-time-compute-{part}-script.docx'),str(review/f'{part}-render'),140,False,False)
    for i,p in enumerate(rendered,1):
        im=Image.open(p).convert('RGB')
        im.thumbnail((1000,1500))
        im.save(review/f'{part}-{i}.jpg',quality=78)
    print(part,'script:',len(rendered),'pages rendered.')
