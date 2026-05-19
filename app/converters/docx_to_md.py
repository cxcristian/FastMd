import os
import re
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import parse_xml
from PIL import Image as PILImage
import io


class DocxToMdConverter:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.doc = Document(docx_path)
        self.lines = []
        self.images_dir = None
        self.image_counter = 0
        self.in_list = False
        self.list_type = None

    def convert(self, output_path, images_dir):
        os.makedirs(images_dir, exist_ok=True)
        self.images_dir = images_dir
        self.lines = []
        self.image_counter = 0

        body = self.doc.element.body
        for child in body:
            tag = child.tag
            if tag == qn('w:p'):
                self._process_paragraph(child)
            elif tag == qn('w:tbl'):
                self._process_table(child)

        content = '\n'.join(self.lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True, 'Conversión exitosa'

    def _process_paragraph(self, p_element):
        style = self._get_paragraph_style(p_element)
        text = self._get_paragraph_text(p_element)

        if not text.strip():
            self._close_list()
            return

        heading_level = self._get_heading_level(style)
        if heading_level:
            self._close_list()
            self.lines.append(f"{'#' * heading_level} {text.strip()}")
            self.lines.append('')
            return

        if 'List' in style or style.startswith('List'):
            self._handle_list_item(p_element, text, style)
            return

        self._close_list()
        formatted = self._format_runs(p_element)
        self.lines.append(formatted)
        self.lines.append('')

    def _get_paragraph_style(self, p_element):
        pPr = p_element.find(qn('w:pPr'))
        if pPr is not None:
            pStyle = pPr.find(qn('w:pStyle'))
            if pStyle is not None:
                return pStyle.get(qn('w:val')) or ''
        return ''

    def _get_paragraph_text(self, p_element):
        texts = []
        for t in p_element.iter(qn('w:t')):
            if t.text:
                texts.append(t.text)
        return ''.join(texts)

    def _get_heading_level(self, style):
        match = re.match(r'heading\s*(\d)', style, re.IGNORECASE)
        if match:
            level = int(match.group(1))
            if 1 <= level <= 6:
                return level
        if style in ('Title', 'Subtitle'):
            return 1 if style == 'Title' else 2
        return None

    def _handle_list_item(self, p_element, text, style):
        numPr = p_element.find(qn('w:pPr'))
        is_ordered = False
        if numPr is not None:
            numPrElem = numPr.find(qn('w:numPr'))
            if numPrElem is not None:
                ilvl = numPrElem.find(qn('w:ilvl'))
                if ilvl is not None:
                    level = int(ilvl.get(qn('w:val'), 0))
                    prefix = '    ' * level
                    if self._is_ordered_list(p_element):
                        self._ensure_list('ordered', level)
                        self.lines.append(f"{prefix}1. {text.strip()}")
                    else:
                        self._ensure_list('unordered', level)
                        self.lines.append(f"{prefix}- {text.strip()}")
                    return

        if re.match(r'^[-•○§]', text.strip()):
            self._ensure_list('unordered', 0)
            self.lines.append(f"- {text.strip().lstrip('-•○§ ')}")
        else:
            self._ensure_list('unordered', 0)
            self.lines.append(f"- {text.strip()}")

    def _is_ordered_list(self, p_element):
        pPr = p_element.find(qn('w:pPr'))
        if pPr is not None:
            numPr = pPr.find(qn('w:numPr'))
            if numPr is not None:
                numId = numPr.find(qn('w:numId'))
                if numId is not None:
                    val = numId.get(qn('w:val'))
                    if val:
                        try:
                            abstract_num = self._get_abstract_num(val)
                            if abstract_num:
                                lvl = abstract_num.find(qn('w:lvl'))
                                if lvl is not None:
                                    numFmt = lvl.find(qn('w:numFmt'))
                                    if numFmt is not None:
                                        fmt = numFmt.get(qn('w:val'), '')
                                        return fmt == 'decimal'
                        except Exception:
                            pass
        return False

    def _get_abstract_num(self, num_id):
        numbering = self.doc.element.find(qn('w:numbering'))
        if numbering is not None:
            for num in numbering.iter(qn('w:num')):
                if num.get(qn('w:numId')) == num_id:
                    abstractNumId = num.find(qn('w:abstractNumId'))
                    if abstractNumId is not None:
                        a_id = abstractNumId.get(qn('w:val'))
                        for an in numbering.iter(qn('w:abstractNum')):
                            if an.get(qn('w:abstractNumId')) == a_id:
                                return an
        return None

    def _ensure_list(self, list_type, level):
        if not self.in_list or self.list_type != list_type:
            self._close_list()
            self.in_list = True
            self.list_type = list_type
            if level == 0:
                self.lines.append('')

    def _close_list(self):
        if self.in_list:
            self.in_list = False
            self.list_type = None
            self.lines.append('')

    def _format_runs(self, p_element):
        parts = []
        for child in p_element.iter():
            if child.tag == qn('w:r'):
                text = ''.join(t.text or '' for t in child.iter(qn('w:t')))
                if not text:
                    continue
                rPr = child.find(qn('w:rPr'))
                bold = False
                italic = False
                if rPr is not None:
                    bold = rPr.find(qn('w:b')) is not None
                    italic = rPr.find(qn('w:i')) is not None
                if bold and italic:
                    parts.append(f"***{text}***")
                elif bold:
                    parts.append(f"**{text}**")
                elif italic:
                    parts.append(f"*{text}*")
                else:
                    parts.append(text)
            elif child.tag == qn('w:hyperlink'):
                link_text = ''.join(t.text or '' for t in child.iter(qn('w:t')))
                rId = child.get(qn('r:id'))
                url = ''
                if rId:
                    url = self._get_hyperlink_url(rId)
                if url:
                    parts.append(f"[{link_text}]({url})")
                else:
                    parts.append(link_text)
            elif child.tag == qn('w:drawing'):
                img_md = self._extract_image(child)
                if img_md:
                    parts.append(f"\n\n{img_md}\n\n")
            elif child.tag == qn('w:pict'):
                img_md = self._extract_ole_image(child)
                if img_md:
                    parts.append(f"\n\n{img_md}\n\n")

        return ''.join(parts)

    def _get_hyperlink_url(self, rId):
        rels = self.doc.part.rels
        if rId in rels:
            return rels[rId].target_ref
        return ''

    def _extract_image(self, drawing_element):
        blip = drawing_element.find('.//' + qn('a:blip'))
        if blip is not None:
            rId = blip.get(qn('r:embed')) or blip.get(qn('r:link'))
            if rId:
                return self._save_image_from_rId(rId)
        return None

    def _extract_ole_image(self, pict_element):
        imagedata = pict_element.find(qn('w:imagedata'))
        if imagedata is not None:
            rId = imagedata.get(qn('r:id')) or imagedata.get(qn('r:link'))
            if rId:
                return self._save_image_from_rId(rId)
        return None

    def _save_image_from_rId(self, rId):
        try:
            rel = self.doc.part.rels[rId]
            image_blob = rel.target_part.blob
            self.image_counter += 1
            ext = 'png'
            try:
                img = PILImage.open(io.BytesIO(image_blob))
                ext = img.format.lower() if img.format else 'png'
            except Exception:
                pass
            filename = f"img_{self.image_counter:04d}.{ext}"
            filepath = os.path.join(self.images_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(image_blob)
            rel_path = os.path.relpath(filepath, os.path.dirname(self.docx_path))
            alt_text = f"Image {self.image_counter}"
            return f"![{alt_text}]({rel_path})"
        except Exception:
            return None

    def _process_table(self, tbl_element):
        self._close_list()
        table = None
        for t in self.doc.tables:
            if t._element is tbl_element:
                table = t
                break
        if table is None:
            return

        md_rows = []
        for i, row in enumerate(table.rows):
            cells = [cell.text.replace('\n', ' ').strip() for cell in row.cells]
            md_rows.append('| ' + ' | '.join(cells) + ' |')
            if i == 0:
                sep = '| ' + ' | '.join('---' for _ in cells) + ' |'
                md_rows.append(sep)
        self.lines.append('')
        self.lines.extend(md_rows)
        self.lines.append('')


def convert(docx_path, output_path, images_dir):
    converter = DocxToMdConverter(docx_path)
    return converter.convert(output_path, images_dir)
