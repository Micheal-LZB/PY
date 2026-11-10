from pathlib import Path
from PIL import Image
import tempfile
import importlib.util
import hashlib

root=Path('E:/PY/TTC')
review=root/'.presentation-review/cost-bridge'
tempfile.tempdir=str(root/'.presentation-review/render-temp')
skill=Path('C:/Users/lzb/.codex/plugins/cache/openai-primary-runtime/documents/26.1105.12137/skills/documents/render_docx.py')
spec=importlib.util.spec_from_file_location('render_docx',skill)
renderer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
for part in ('main','backup'):
    path=review/f'{part}-word.pdf'
    renderer.convert_to_pdf=lambda *args,p=path,**kwargs:(str(p),'Native Microsoft Word PDF export')
    old={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (review/f'{part}-render').glob('page-*.png')}
    pages=renderer.rasterize(str(root/f'presentation/presentation paper/test-time-compute-{part}-script.docx'),str(review/f'{part}-render'),140,False,False)
    changed=[]
    for i,p in enumerate(pages,1):
        p=Path(p)
        if old.get(p.name)!=hashlib.sha256(p.read_bytes()).hexdigest(): changed.append(i)
        im=Image.open(p).convert('RGB')
        im.thumbnail((1000,1500))
        im.save(review/f'{part}-{i}.jpg',quality=78)
    print(part,':',len(pages),'pages; changed pages',changed,'; other pages pixel-identical to reviewed version.')
