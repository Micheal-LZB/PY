from pathlib import Path
import sys, json, re
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.packages'))
import nbformat
import pymupdf
from PIL import Image, ImageDraw
nb=nbformat.read(ROOT/'generative-baselines.ipynb',as_version=4)
nbformat.validate(nb)
codes=[c for c in nb.cells if c.cell_type=='code']
assert all(c.execution_count is not None for c in codes)
assert not any(o.output_type=='error' for c in codes for o in c.outputs)
images=sum('image/png' in o.get('data',{}) for c in codes for o in c.outputs)
assert images >= 10, images
doc=pymupdf.open(ROOT/'generative-baselines.pdf')
text='\n'.join(p.get_text() for p in doc)
assert len(doc)>5
assert 'Digit observations' in text and 'Moon observations' in text
assert 'PASS: Gaussian' in text
preview=ROOT/'qa'
preview.mkdir(exist_ok=True)
thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=pymupdf.Matrix(.45,.45),alpha=False)
    image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    tile=Image.new('RGB',(290,410),'#dce3eb')
    tile.paste(image,((290-image.width)//2,8))
    ImageDraw.Draw(tile).text((10,390),f'Page {i+1}',fill='black')
    thumbs.append(tile)
for start in range(0,len(thumbs),12):
    group=thumbs[start:start+12]
    sheet=Image.new('RGB',(290*4,410*((len(group)+3)//4)),'white')
    for j,tile in enumerate(group): sheet.paste(tile,((j%4)*290,(j//4)*410))
    sheet.save(preview/f'contact_{start//12+1}.png')
print(json.dumps({'executed_cells':len(codes),'plots':images,'pdf_pages':len(doc),
                  'pdf_bytes':(ROOT/'generative-baselines.pdf').stat().st_size},indent=2))
