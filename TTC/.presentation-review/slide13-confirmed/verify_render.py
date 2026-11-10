from pathlib import Path
import re
import tempfile
import importlib.util
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image

root = Path('E:/PY/TTC')
review = root / '.presentation-review/slide13-confirmed'
before = (review / 'slides-before.tex').read_text(encoding='utf-8')
after = (root / 'presentation/presentation paper/test-time-compute-25min.tex').read_text(encoding='utf-8')
frames = lambda s: re.findall(r'\\begin\{frame\}.*?\\end\{frame\}', s, flags=re.S)
old_frames, new_frames = frames(before), frames(after)
assert len(old_frames) == len(new_frames) == 29
changed = [i for i,(a,b) in enumerate(zip(old_frames,new_frames),1) if a != b]
assert changed == [13], changed
print('Only frame 13 changed; frame count remains 29.')
pdf = root / '.presentation-review/build/test-time-compute-25min.pdf'
assert len(PdfReader(pdf).pages) == 29
convert_from_path(str(pdf), dpi=175, first_page=13, last_page=13)[0].save(review / 'slide13-after.jpg', quality=90)
warnings = [s for s in (pdf.with_suffix('.log')).read_text(errors='replace').splitlines() if 'Overfull' in s or 'LaTeX Error' in s]
print('Layout/error warnings:', warnings)

tempfile.tempdir = str(root / '.presentation-review/render-temp')
skill = Path('C:/Users/lzb/.codex/plugins/cache/openai-primary-runtime/documents/26.1105.12137/skills/documents/render_docx.py')
spec = importlib.util.spec_from_file_location('render_docx', skill)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
renderer.convert_to_pdf = lambda *args, **kwargs: (str(review / 'main-word.pdf'), 'Native Microsoft Word PDF export')
pages = renderer.rasterize(str(root / 'presentation/presentation paper/test-time-compute-main-script.docx'), str(review / 'word-render'), 140, False, False)
for i, path in enumerate(pages,1):
    im = Image.open(path).convert('RGB')
    im.thumbnail((1000,1500))
    im.save(review / f'word-{i}.jpg', quality=78)
print('Main script pages rendered:', len(pages))
