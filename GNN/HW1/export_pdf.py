"""Export the complete executed notebook, including code and all outputs."""
from pathlib import Path
import sys, re, io, base64, textwrap, html, json
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'.packages'))
import nbformat
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Preformatted, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT

pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold',
                            italic='Arial', boldItalic='Arial-Bold')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCustom', fontName='Arial', fontSize=10,
    leading=14, spaceAfter=8, textColor=colors.HexColor('#243247')))
styles.add(ParagraphStyle(name='TitleCustom', fontName='Arial-Bold', fontSize=22,
    leading=28, spaceAfter=18, textColor=colors.HexColor('#14324f')))
styles.add(ParagraphStyle(name='HeadingCustom', fontName='Arial-Bold', fontSize=15,
    leading=20, spaceBefore=16, spaceAfter=10, keepWithNext=True,
    textColor=colors.HexColor('#14324f')))
styles.add(ParagraphStyle(name='SmallHeading', fontName='Arial-Bold', fontSize=12,
    leading=16, spaceBefore=12, spaceAfter=8, keepWithNext=True))
styles.add(ParagraphStyle(name='CodeCustom', fontName='Consolas', fontSize=7.2,
    leading=9.4, leftIndent=6, rightIndent=6, spaceAfter=8,
    textColor=colors.HexColor('#263445'), backColor=colors.HexColor('#f3f5f8')))
styles.add(ParagraphStyle(name='OutputCustom', fontName='Consolas', fontSize=7.4,
    leading=9.5, spaceAfter=10, textColor=colors.HexColor('#1b4f56')))

def inline(s):
    s = html.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`([^`]+)`', r'<font name="Consolas">\1</font>', s)
    return s

story = []
def markdown(s):
    for block in re.split(r'\n\s*\n', s.strip()):
        if not block: continue
        if block.startswith('# '):
            story.append(Paragraph(inline(block[2:]), styles['TitleCustom']))
        elif block.startswith('## '):
            story.append(Paragraph(inline(block[3:]), styles['HeadingCustom']))
        elif block.startswith('### '):
            story.append(Paragraph(inline(block[4:]), styles['SmallHeading']))
        elif block.startswith('- '):
            for line in re.split(r'\n(?=- )', block):
                story.append(Paragraph('• '+inline(line.lstrip('- ').replace('\n',' ')),
                                       styles['BodyCustom']))
        else:
            story.append(Paragraph(inline(block.replace('\n',' ')), styles['BodyCustom']))

def pre(s, style, width):
    lines=[]
    for line in s.replace('\t','    ').splitlines():
        lines.extend(textwrap.wrap(line, width=width, replace_whitespace=False,
            drop_whitespace=False, subsequent_indent='    ') or [''])
    # Small splittable chunks prevent a long code block from forcing an
    # almost-empty page when a preceding heading requests keep-with-next.
    for start in range(0,len(lines),24):
        story.append(Preformatted('\n'.join(lines[start:start+24]), styles[style]))

nb = nbformat.read(ROOT/'generative-baselines.ipynb', as_version=4)
for cell in nb.cells:
    if cell.cell_type == 'markdown': markdown(cell.source)
    elif cell.cell_type == 'code':
        story.append(Paragraph(f'Code cell [{cell.execution_count}]', styles['SmallHeading']))
        pre(cell.source, 'CodeCustom', 108)
        for output in cell.get('outputs', []):
            typ = output.output_type
            if typ == 'error': raise RuntimeError('Notebook contains an error')
            if typ == 'stream':
                pre(output.text, 'OutputCustom', 105)
            elif typ in ('display_data','execute_result'):
                data=output.data
                if 'image/png' in data:
                    stream=io.BytesIO(base64.b64decode(data['image/png']))
                    picture=Image(stream)
                    factor=min(490/picture.imageWidth, 650/picture.imageHeight)
                    picture.drawWidth=picture.imageWidth*factor
                    picture.drawHeight=picture.imageHeight*factor
                    picture.hAlign='CENTER'
                    story.extend([picture, Spacer(1,12)])
                elif 'text/markdown' in data: markdown(data['text/markdown'])
                elif 'text/plain' in data: pre(data['text/plain'], 'OutputCustom',105)

def header(canvas, doc):
    canvas.saveState()
    canvas.setFont('Arial', 8)
    canvas.setFillColor(colors.HexColor('#607286'))
    canvas.drawString(42, 815, 'GENERATIVE NEURAL NETWORKS  /  EXERCISE 1')
    canvas.drawRightString(553, 25, f'{doc.page}')
    canvas.setStrokeColor(colors.HexColor('#dce3eb'))
    canvas.line(42,806,553,806)
    canvas.restoreState()

doc=SimpleDocTemplate(str(ROOT/'generative-baselines.pdf'), pagesize=(595.28,841.89),
    rightMargin=42,leftMargin=42,topMargin=48,bottomMargin=42,
    title='Exercise 1 - Classical generative models',author='')
doc.build(story,onFirstPage=header,onLaterPages=header)
print('Exported PDF:', ROOT/'generative-baselines.pdf')
