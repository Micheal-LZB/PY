from pathlib import Path
import tempfile
import importlib.util
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image

root = Path('E:/PY/TTC')
review = root/'.presentation-review/remove-last-three'
pdf = root/'.presentation-review/build/ttc-trim-review.pdf'
reader = PdfReader(pdf)
assert len(reader.pages) == 24
assert '24 / 24' in reader.pages[-1].extract_text()
assert 'Difficulty Estimation and Policy Selection' in reader.pages[-1].extract_text()
warnings = [s for s in pdf.with_suffix('.log').read_text(errors='replace').splitlines() if 'Overfull' in s or 'LaTeX Error' in s]
assert not warnings,warnings
convert_from_path(str(pdf),dpi=150,first_page=24,last_page=24)[0].save(review/'last-slide.jpg',quality=85)
tempfile.tempdir = str(root/'.presentation-review/render-temp')
skill = Path('C:/Users/lzb/.codex/plugins/cache/openai-primary-runtime/documents/26.1105.12137/skills/documents/render_docx.py')
spec = importlib.util.spec_from_file_location('render_docx',skill)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
renderer.convert_to_pdf = lambda *args,**kwargs: (str(review/'backup-word.pdf'),'Native Microsoft Word PDF export')
pages = renderer.rasterize(str(root/'presentation/presentation paper/test-time-compute-backup-script.docx'),str(review/'backup-render'),140,False,False)
for i,p in enumerate(pages,1):
    im = Image.open(p).convert('RGB')
    im.thumbnail((1000,1500))
    im.save(review/f'backup-{i}.jpg',quality=78)
print('24 presentation pages verified;',len(pages),'backup script pages rendered.')
