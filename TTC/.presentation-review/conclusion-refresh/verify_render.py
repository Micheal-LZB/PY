from pathlib import Path
import re
import importlib.util
import tempfile
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image, ImageDraw

root = Path('E:/PY/TTC')
review = root / '.presentation-review/conclusion-refresh'
source = root / 'presentation/presentation paper/test-time-compute-25min.tex'
before = (review / 'slides-before.tex').read_text(encoding='utf-8')
after = source.read_text(encoding='utf-8')
frames = lambda t: re.findall(r'\\begin\{frame\}.*?\\end\{frame\}',t,flags=re.S)
old,new = frames(before),frames(after)
assert len(old) == 29 and len(new) == 27
assert old[:17] == new[:17]
assert old[22:] == new[20:], 'Backup slide contents changed.'
assert 'Example: Choosing a Model to Check Answers' not in after
assert 'Limits of the Comparison' not in after
assert r'\begin{frame}{Conclusions}' in new[18]
assert r'\begin{frame}{Questions}' in new[19]
print('27 frames: conclusion 19, questions 20, backup 21--27; backup contents unchanged.')
pdf = root / '.presentation-review/build/ttc-conclusion-review.pdf'
pages = PdfReader(pdf).pages
assert len(pages) == 27
assert '19 / 27' in pages[18].extract_text()
log = pdf.with_suffix('.log').read_text(errors='replace')
warnings = [line for line in log.splitlines() if 'Overfull' in line or 'LaTeX Error' in line]
assert not warnings,warnings
print('Compilation: no overfull boxes or LaTeX errors.')
for number in (18,19,20,21):
    convert_from_path(str(pdf),dpi=175,first_page=number,last_page=number)[0].save(review / f'slide-{number}.jpg',quality=90)
tiles = []
for number,im in enumerate(convert_from_path(str(pdf),dpi=65),1):
    im.thumbnail((260,162))
    tile = Image.new('RGB',(280,190),'white')
    tile.paste(im,((280-im.width)//2,5))
    ImageDraw.Draw(tile).text((10,172),str(number),fill='black')
    tiles.append(tile)
contact = Image.new('RGB',(1120,190*7),'#cccccc')
for i,tile in enumerate(tiles):
    contact.paste(tile,((i%4)*280,(i//4)*190))
contact.save(review / 'slide-order.jpg',quality=85)

tempfile.tempdir = str(root / '.presentation-review/render-temp')
skill = Path('C:/Users/lzb/.codex/plugins/cache/openai-primary-runtime/documents/26.1105.12137/skills/documents/render_docx.py')
spec = importlib.util.spec_from_file_location('render_docx',skill)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
for part in ('main','backup'):
    word_pdf = review / f'{part}-word.pdf'
    renderer.convert_to_pdf = lambda *args,p=word_pdf,**kwargs: (str(p),'Native Microsoft Word PDF export')
    rendered = renderer.rasterize(str(root / f'presentation/presentation paper/test-time-compute-{part}-script.docx'),str(review / f'{part}-render'),140,False,False)
    for i,path in enumerate(rendered,1):
        im = Image.open(path).convert('RGB')
        im.thumbnail((1000,1500))
        im.save(review / f'{part}-{i}.jpg',quality=78)
    print(part,'script:',len(rendered),'pages rendered.')
