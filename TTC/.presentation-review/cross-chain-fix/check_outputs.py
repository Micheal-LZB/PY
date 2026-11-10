from pathlib import Path
import re
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image

root = Path('E:/PY/TTC')
review = root / '.presentation-review'
qa = review / 'cross-chain-fix'
source = root / 'presentation/presentation paper/test-time-compute-25min.tex'
before = (qa / 'slides-before.tex').read_text(encoding='utf-8')
after = source.read_text(encoding='utf-8')
frames = lambda text: re.findall(r'\\begin\{frame\}.*?\\end\{frame\}', text, flags=re.S)
old_frames, new_frames = frames(before), frames(after)
assert len(old_frames) == len(new_frames) == 29
changed = [i for i, (a, b) in enumerate(zip(old_frames, new_frames), 1) if a != b]
assert set(changed).issubset({12, 14, 15}), changed
assert old_frames[12] == new_frames[12]
assert old_frames[22:] == new_frames[22:]
print('Changed frames:', changed, '; frame 13 and all backup frames unchanged.')

pdf = review / 'build/test-time-compute-25min.pdf'
assert len(PdfReader(pdf).pages) == 29
convert_from_path(str(pdf), dpi=175, first_page=14, last_page=14)[0].save(qa / 'slide-14-final.jpg', quality=90)
log = (review / 'build/test-time-compute-25min.log').read_text(errors='replace')
warnings = [line for line in log.splitlines() if 'Overfull' in line or 'LaTeX Error' in line]
print('Layout/error warnings:', warnings)

count = len(PdfReader(review / 'main-word.pdf').pages)
print('Main Word script:', count, 'pages.')
for i in range(1, count + 1):
    image = Image.open(review / f'main-render/page-{i}.png').convert('RGB')
    image.thumbnail((1000, 1500))
    image.save(qa / f'word-page-{i}.jpg', quality=78)

paper = PdfReader(root / 'presentation/2408.03314v1.pdf')
text = paper.pages[25].extract_text()
print('Paper appendix selection excerpt:')
start = text.find('I. ')
print(text[max(0, start):][:6500])
