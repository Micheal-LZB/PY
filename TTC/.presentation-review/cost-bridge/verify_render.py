from pathlib import Path
import re
import tempfile
import importlib.util
from pypdf import PdfReader
from pdf2image import convert_from_path
from docx import Document
from PIL import Image, ImageDraw

root = Path('E:/PY/TTC')
review = root/'.presentation-review/cost-bridge'
source = root/'presentation/presentation paper/test-time-compute-25min.tex'
frames = lambda t: re.findall(r'\\begin\{frame\}.*?\\end\{frame\}',t,re.S)
old = frames((review/'slides-before.tex').read_text(encoding='utf-8'))
new = frames(source.read_text(encoding='utf-8'))
assert len(old) == 24 and len(new) == 25
assert new[:15] == old[:15]
assert new[19:23] == old[20:24]
assert new[16].split(r'\note{')[0] == old[17].split(r'\note{')[0]
assert new[17].split(r'\note{')[0] == old[18].split(r'\note{')[0]
assert 'Comparing Two Uses' in new[15]
assert 'Backup: Pretraining' in new[23]
assert 'Backup: Using R' in new[24]
assert r'\begin{aligned}' not in ''.join(new[:19])
print('25 slides: 19 main, 6 backup; former formula pages now backup 24--25.')

folder = root/'presentation/presentation paper'
for part,expected in [('main',list(range(1,20))),('backup',list(range(20,26)))]:
    d = Document(folder/f'test-time-compute-{part}-script.docx')
    numbers = [int(m.group(1)) for p in d.paragraphs for m in [re.match(r'^Slide (\d+)\b',p.text)] if m]
    assert numbers == expected,(part,numbers)
print('Both Word scripts match the new slide numbering.')

pdf = root/'.presentation-review/build/ttc-cost-bridge-review.pdf'
reader = PdfReader(pdf)
assert len(reader.pages) == 25
assert '16 / 25' in reader.pages[15].extract_text()
assert '25 / 25' in reader.pages[24].extract_text()
warnings = [s for s in pdf.with_suffix('.log').read_text(errors='replace').splitlines() if 'Overfull' in s or 'LaTeX Error' in s]
print('Layout/error warnings:',warnings)
for number in (16,17,24,25):
    convert_from_path(str(pdf),dpi=175,first_page=number,last_page=number)[0].save(review/f'after-{number}.jpg',quality=90)
tiles=[]
for i,im in enumerate(convert_from_path(str(pdf),dpi=65),1):
    im.thumbnail((260,162))
    tile=Image.new('RGB',(280,190),'white')
    tile.paste(im,((280-im.width)//2,5))
    ImageDraw.Draw(tile).text((10,172),str(i),fill='black')
    tiles.append(tile)
sheet=Image.new('RGB',(1120,1330),'#cccccc')
for i,tile in enumerate(tiles):
    sheet.paste(tile,((i%4)*280,(i//4)*190))
sheet.save(review/'slide-order.jpg',quality=85)

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
    print(part,'script pages:',len(rendered))
