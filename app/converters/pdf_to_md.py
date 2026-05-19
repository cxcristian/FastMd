import os
import fitz
from PIL import Image as PILImage
import io


class PdfToMdConverter:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.lines = []
        self.images_dir = None
        self.image_counter = 0
        self.body_font_sizes = []

    def convert(self, output_path, images_dir):
        os.makedirs(images_dir, exist_ok=True)
        self.images_dir = images_dir
        self.lines = []
        self.image_counter = 0
        self._estimate_body_font_size()

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            self._process_page(page, page_num)

        content = '\n'.join(self.lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.doc.close()
        return True, 'Conversión exitosa'

    def _estimate_body_font_size(self):
        sizes = []
        for page_num in range(min(3, len(self.doc))):
            page = self.doc[page_num]
            blocks = page.get_text('dict', flags=fitz.TEXT_PRESERVE_WHITESPACE)['blocks']
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        for span in line['spans']:
                            sizes.append(span['size'])
        if sizes:
            from statistics import median
            self.body_font_size = median(sizes)
        else:
            self.body_font_size = 11

    def _process_page(self, page, page_num):
        blocks = page.get_text('dict', flags=fitz.TEXT_PRESERVE_WHITESPACE)['blocks']
        page_links = page.get_links()

        for block in blocks:
            if block['type'] == 0:
                self._process_text_block(block, page_links)
            elif block['type'] == 1:
                self._process_image_block(block, page_num)

    def _process_text_block(self, block, page_links):
        full_text = ''
        has_bold = False
        has_italic = False
        font_sizes = []
        spans_info = []

        for line in block['lines']:
            for span in line['spans']:
                text = span['text'].strip()
                if not text:
                    continue
                font_sizes.append(span['size'])
                spans_info.append({
                    'text': text,
                    'size': span['size'],
                    'bold': (span['flags'] & 2) != 0,
                    'italic': (span['flags'] & 1) != 0,
                    'font': span['font'],
                })
                full_text += text + ' '
                if (span['flags'] & 2) != 0:
                    has_bold = True
                if (span['flags'] & 1) != 0:
                    has_italic = True

        full_text = full_text.strip()
        if not full_text:
            return

        avg_size = sum(font_sizes) / len(font_sizes) if font_sizes else self.body_font_size
        size_ratio = avg_size / self.body_font_size if self.body_font_size > 0 else 1

        is_heading = False
        heading_level = 0
        if size_ratio >= 1.4:
            heading_level = 1
            is_heading = True
        elif size_ratio >= 1.2:
            heading_level = 2
            is_heading = True
        elif size_ratio >= 1.1 and (has_bold or 'bold' in spans_info[0]['font'].lower() if spans_info else False):
            heading_level = 3
            is_heading = True

        if is_heading:
            self.lines.append('')
            self.lines.append(f"{'#' * heading_level} {full_text}")
            self.lines.append('')
            return

        bbox = block['bbox']
        x0 = bbox[0]
        page_rect = self.doc[0].rect if len(self.doc) > 0 else fitz.Rect(0, 0, 612, 792)

        link_texts = self._get_links_in_bbox(bbox, page_links)
        md_text = self._apply_inline_formatting(spans_info, link_texts)

        self.lines.append(md_text)
        self.lines.append('')

    def _apply_inline_formatting(self, spans_info, link_texts):
        result = []
        for span in spans_info:
            text = span['text']
            for link_text, link_url in link_texts:
                if link_text in text:
                    text = text.replace(link_text, f"[{link_text}]({link_url})")
            if span['bold'] and span['italic']:
                result.append(f"***{text}***")
            elif span['bold']:
                result.append(f"**{text}**")
            elif span['italic']:
                result.append(f"*{text}*")
            else:
                result.append(text)
        return ''.join(result)

    def _get_links_in_bbox(self, bbox, links):
        result = []
        for link in links:
            if 'from' in link:
                l_rect = link['from']
                if self._rects_overlap(bbox, l_rect):
                    uri = link.get('uri', '')
                    result.append((link.get('text', ''), uri))
        return result

    def _rects_overlap(self, r1, r2):
        return not (r1[2] < r2[0] or r1[0] > r2[2] or r1[3] < r2[1] or r1[1] > r2[3])

    def _process_image_block(self, block, page_num):
        try:
            img = block['image']
            if not img:
                return
            ext_map = block.get('ext', 'png')
            self.image_counter += 1
            filename = f"pdf_img_{page_num + 1}_{self.image_counter:03d}.{ext_map}"
            filepath = os.path.join(self.images_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(img)
            rel_path = os.path.relpath(filepath, os.path.dirname(self.pdf_path))
            alt_text = f"Image {self.image_counter}"
            self.lines.append('')
            self.lines.append(f"![{alt_text}]({rel_path})")
            self.lines.append('')
        except Exception:
            pass


def convert(pdf_path, output_path, images_dir):
    converter = PdfToMdConverter(pdf_path)
    return converter.convert(output_path, images_dir)
