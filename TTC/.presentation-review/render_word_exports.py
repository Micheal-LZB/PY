from pathlib import Path
import importlib.util
import tempfile
from PIL import Image, ImageOps, ImageDraw

ROOT = Path('E:/PY/TTC/.presentation-review')
tmp = ROOT / 'render-temp'
tmp.mkdir(exist_ok=True)
tempfile.tempdir = str(tmp)
skill = Path('C:/Users/lzb/.codex/plugins/cache/openai-primary-runtime/documents/26.1105.12137/skills/documents/render_docx.py')
spec = importlib.util.spec_from_file_location('render_docx', skill)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

for name in ('main', 'backup'):
    pdf = ROOT / f'{name}-word.pdf'
    # Native Word produced this PDF from the actual DOCX. Keep the skill's
    # canonical page rasterization while substituting the native exporter.
    renderer.convert_to_pdf = lambda *args, p=pdf, **kwargs: (str(p), 'Native Microsoft Word PDF export')
    paths = renderer.rasterize(
        str(Path('E:/PY/TTC/presentation/presentation paper') / f'test-time-compute-{name}-script.docx'),
        str(ROOT / f'{name}-render'), 140, False, False)
    thumbs = []
    for i, p in enumerate(paths, 1):
        img = Image.open(p).convert('RGB')
        img.save(Path(p).with_suffix('.jpg'), quality=88)
        img.thumbnail((410, 580))
        tile = Image.new('RGB', (430, 615), 'white')
        tile.paste(img, ((430-img.width)//2, 20))
        ImageDraw.Draw(tile).text((15, 590), f'{name} page {i}', fill='black')
        thumbs.append(tile)
    sheet = Image.new('RGB', (430 * min(3, len(thumbs)), 615 * ((len(thumbs)+2)//3)), '#cccccc')
    for i, tile in enumerate(thumbs):
        sheet.paste(tile, ((i%3)*430, (i//3)*615))
    sheet.save(ROOT / f'{name}-contact.jpg', quality=90)
    print(name, len(paths), 'pages rendered')

