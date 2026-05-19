import os
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.converters.docx_to_md import convert as docx_to_md
from app.converters.pdf_to_md import convert as pdf_to_md
from app.converters.md_to_docx import convert as md_to_docx


SUPPORTED_TO_MD = ('.docx', '.pdf')
SUPPORTED_TO_DOCX = ('.md',)
SUPPORTED_FORMATS = SUPPORTED_TO_MD + SUPPORTED_TO_DOCX


class ConversionWorker:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 2)
        self.futures = {}
        self.progress_queue = queue.Queue()
        self._running = False

    def start_conversion(self, files, mode, output_dir, file_status_callback, done_callback):
        self._running = True
        
        # Expand folders to individual files
        expanded_files = []
        folder_mapping = {}  # Maps file path to original folder path
        
        # Define supported extensions based on mode
        if mode == 'to_md':
            supported_exts = SUPPORTED_TO_MD
        else:  # to_docx
            supported_exts = SUPPORTED_TO_DOCX
        
        for item in files:
            if os.path.isdir(item):
                # Find all supported files in folder
                for root, dirs, filenames in os.walk(item):
                    for filename in filenames:
                        if filename.lower().endswith(supported_exts):
                            file_path = os.path.join(root, filename)
                            expanded_files.append(file_path)
                            folder_mapping[file_path] = item
            else:
                expanded_files.append(item)
                folder_mapping[item] = None
        
        total = len(expanded_files)
        if total == 0:
            done_callback(0, 0, 0)
            self._running = False
            return

        def _run():
            self.futures = {}
            for file_path in expanded_files:
                folder_source = folder_mapping.get(file_path)
                future = self.executor.submit(
                    self._convert_single, file_path, mode, output_dir, folder_source
                )
                self.futures[future] = file_path

            completed = 0
            errors = 0
            for future in as_completed(self.futures):
                file_path = self.futures[future]
                try:
                    success, message = future.result()
                    if success:
                        completed += 1
                    else:
                        errors += 1
                except Exception as e:
                    success = False
                    message = str(e)
                    errors += 1

                file_status_callback(
                    file_path, 'done' if success else 'error',
                    message, completed + errors, total
                )

            done_callback(completed, errors, total)
            self._running = False

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread

    def _convert_single(self, file_path, mode, output_dir, folder_source=None):
        ext = Path(file_path).suffix.lower()
        base_name = Path(file_path).stem

        if mode == 'to_md':
            # Calculate relative path if file came from a folder
            if folder_source:
                rel_path = os.path.relpath(file_path, folder_source)
                rel_dir = os.path.dirname(rel_path)
                
                # Create output folder structure
                if rel_dir:
                    output_folder = os.path.join(output_dir, os.path.splitext(os.path.basename(folder_source))[0], rel_dir)
                else:
                    output_folder = os.path.join(output_dir, os.path.splitext(os.path.basename(folder_source))[0])
                
                os.makedirs(output_folder, exist_ok=True)
                md_path = os.path.join(output_folder, f'{base_name}.md')
                images_dir = os.path.join(output_folder, f'{base_name}_images')
            else:
                # Original behavior for individual files
                output_folder = output_dir
                os.makedirs(output_folder, exist_ok=True)
                md_path = os.path.join(output_folder, f'{base_name}.md')
                images_dir = os.path.join(output_folder, f'{base_name}_images')

            if ext == '.docx':
                return docx_to_md(file_path, md_path, images_dir)
            elif ext == '.pdf':
                return pdf_to_md(file_path, md_path, images_dir)
            else:
                return False, f'Formato no soportado: {ext}'

        elif mode == 'to_docx':
            if ext == '.md':
                # Calculate relative path if file came from a folder
                if folder_source:
                    rel_path = os.path.relpath(file_path, folder_source)
                    rel_dir = os.path.dirname(rel_path)
                    
                    # Create output folder structure
                    if rel_dir:
                        output_folder = os.path.join(output_dir, os.path.splitext(os.path.basename(folder_source))[0], rel_dir)
                    else:
                        output_folder = os.path.join(output_dir, os.path.splitext(os.path.basename(folder_source))[0])
                    
                    os.makedirs(output_folder, exist_ok=True)
                    docx_path = os.path.join(output_folder, f'{base_name}.docx')
                else:
                    # Original behavior for individual files
                    output_folder = output_dir
                    os.makedirs(output_folder, exist_ok=True)
                    docx_path = os.path.join(output_folder, f'{base_name}.docx')
                
                return md_to_docx(file_path, docx_path)
            else:
                return False, f'Formato no soportado: {ext}'

        return False, 'Modo desconocido'

    def cancel(self):
        self._running = False
        for future in self.futures:
            future.cancel()
        self.executor.shutdown(wait=False)
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 2)

    @property
    def is_running(self):
        return self._running
