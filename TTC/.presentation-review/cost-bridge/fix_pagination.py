from pathlib import Path
from docx import Document
from PIL import Image
import tempfile
import importlib.util

folder=Path('E:/PY/TTC/presentation/presentation paper')
review=Path('E:/PY/TTC/.presentation-review/cost-bridge')
for part,heading in [('main','Slide 18 Conclusions'),('backup','Slide 25 Using R to Compare Total Compute')]:
    path=folder/f'test-time-compute-{part}-script.docx'
    doc=Document(path)
    before=[p.text for p in doc.paragraphs]
    p=next(p for p in doc.paragraphs if p.text==heading)
    p.paragraph_format.page_break_before=True
    assert [p.text for p in doc.paragraphs]==before
    doc.save(path)
print('Kept the conclusion and the final backup explanation together on their own pages.')
