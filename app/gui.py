import os
import customtkinter as ctk
import tkinterdnd2
from tkinterdnd2 import DND_FILES
from pathlib import Path
from tkinter import filedialog, messagebox

from app.i18n import t
from app.ai_prompt import save_prompt_to_file
from app.worker import ConversionWorker


class FastMdApp:
    def __init__(self):
        self.root = tkinterdnd2.TkinterDnD.Tk()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.lang = 'es'
        self.lang_var = ctk.StringVar(value='es')

        self.files = []
        self.file_widgets = {}
        self.output_dir = os.path.join(os.path.expanduser('~/Desktop'), 'fastMd', 'output')
        self.mode_var = ctk.StringVar(value='to_md')
        self.cover_var = ctk.BooleanVar(value=True)
        self.pages_var = ctk.BooleanVar(value=True)

        self.worker = ConversionWorker()

        self._build_ui()
        self._setup_drag_drop()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _build_ui(self):
        self.root.title("fastMd v1.0")
        self.root.geometry("800x680")
        self.root.minsize(650, 500)

        self.main = ctk.CTkFrame(self.root)
        self.main.pack(fill="both", expand=True, padx=12, pady=12)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_toolbar()
        self._build_file_list()
        self._build_mode_selector()
        self._build_action_buttons()
        self._build_progress()
        self._build_apa_settings()

    def _build_header(self):
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="fastMd v1.0",
            font=ctk.CTkFont(size=26, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        self.lang_switch = ctk.CTkSegmentedButton(
            frame, values=['🇪🇸 ES', '🇺🇸 EN'],
            command=self._switch_language,
            font=ctk.CTkFont(size=12)
        )
        self.lang_switch.grid(row=0, column=1, sticky="e")
        self.lang_switch.set('🇪🇸 ES')

    def _build_toolbar(self):
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.add_btn = ctk.CTkButton(frame, text=t('add_files', self.lang),
                                     command=self._add_files, width=140)
        self.add_btn.pack(side="left", padx=(0, 5))

        self.add_folder_btn = ctk.CTkButton(frame, text=t('add_folder', self.lang),
                                            command=self._add_folder_dialog, width=140)
        self.add_folder_btn.pack(side="left", padx=5)

        self.output_btn = ctk.CTkButton(frame, text=t('output_folder', self.lang),
                                        command=self._select_output, width=140)
        self.output_btn.pack(side="left", padx=5)

        self.ai_btn = ctk.CTkButton(frame, text=t('ai_prompt', self.lang),
                                    command=self._generate_ai_prompt, width=140)
        self.ai_btn.pack(side="left", padx=5)

        self.help_btn = ctk.CTkButton(frame, text=t('help', self.lang),
                                      command=self._show_help, width=30,
                                      fg_color='transparent', font=ctk.CTkFont(size=18))
        self.help_btn.pack(side="left", padx=(5, 0))

        self.output_label = ctk.CTkLabel(
            frame, text=os.path.basename(self.output_dir) or 'output',
            fg_color=("gray85", "gray25"), corner_radius=5, padx=10
        )
        self.output_label.pack(side="right", padx=5)

    def _build_file_list(self):
        container = ctk.CTkFrame(self.main)
        container.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.file_scroll = ctk.CTkScrollableFrame(container)
        self.file_scroll.grid(row=0, column=0, sticky="nsew")

        self.drop_label = ctk.CTkLabel(
            self.file_scroll, text=t('drop_here', self.lang),
            font=ctk.CTkFont(size=14)
        )
        self.drop_label.pack(expand=True, fill="both", pady=50)

    def _build_mode_selector(self):
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))

        self.to_md_radio = ctk.CTkRadioButton(
            frame, text=t('mode_to_md', self.lang),
            variable=self.mode_var, value='to_md',
            command=self._on_mode_change
        )
        self.to_md_radio.pack(side="left", padx=(0, 20))

        self.to_docx_radio = ctk.CTkRadioButton(
            frame, text=t('mode_to_docx', self.lang),
            variable=self.mode_var, value='to_docx',
            command=self._on_mode_change
        )
        self.to_docx_radio.pack(side="left")

        self.auto_radio = ctk.CTkRadioButton(
            frame, text=t('mode_auto', self.lang),
            variable=self.mode_var, value='auto',
            command=self._on_mode_change
        )
        self.auto_radio.pack(side="left", padx=(20, 0))

    def _build_action_buttons(self):
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        frame.grid(row=4, column=0, sticky="ew", pady=(0, 8))

        self.convert_btn = ctk.CTkButton(
            frame, text=t('convert_all', self.lang),
            command=self._convert_all, width=200,
            height=40, font=ctk.CTkFont(size=14, weight="bold")
        )
        self.convert_btn.pack(side="left", padx=(0, 10))

        self.clear_btn = ctk.CTkButton(
            frame, text=t('clear_list', self.lang),
            command=self._clear_list, width=120
        )
        self.clear_btn.pack(side="left")

    def _build_progress(self):
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        frame.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(frame, height=10)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(frame, text="", anchor="w",
                                         font=ctk.CTkFont(size=12))
        self.status_label.grid(row=1, column=0, sticky="ew")

    def _build_apa_settings(self):
        self.apa_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.apa_frame.grid(row=6, column=0, sticky="ew")

        self.apa_title = ctk.CTkLabel(
            self.apa_frame, text=t('apa_settings', self.lang),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.apa_title.pack(anchor="w")

        self.apa_font_lbl = ctk.CTkLabel(
            self.apa_frame, text=t('font', self.lang)
        )
        self.apa_font_lbl.pack(anchor="w", padx=(10, 0))

        self.apa_spacing_lbl = ctk.CTkLabel(
            self.apa_frame, text=t('spacing', self.lang)
        )
        self.apa_spacing_lbl.pack(anchor="w", padx=(10, 0))

        self.cover_check = ctk.CTkCheckBox(
            self.apa_frame, text=t('cover_page', self.lang),
            variable=self.cover_var
        )
        self.cover_check.pack(anchor="w", padx=(10, 0))

        self.pages_check = ctk.CTkCheckBox(
            self.apa_frame, text=t('page_numbers', self.lang),
            variable=self.pages_var
        )
        self.pages_check.pack(anchor="w", padx=(10, 0))

    def _setup_drag_drop(self):
        try:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
            self.file_scroll.drop_target_register(DND_FILES)
            self.file_scroll.dnd_bind('<<Drop>>', self._on_drop)
        except Exception:
            pass

    def _on_drop(self, event):
        raw = event.data.strip()
        paths = []
        if raw.startswith('{'):
            import re
            paths = re.findall(r'\{([^}]+)\}', raw)
        elif raw.startswith('\"') or raw.startswith("'"):
            import shlex
            paths = shlex.split(raw)
        else:
            paths = raw.split()
        for fp in paths:
            fp = fp.strip('{}\'" ')
            if os.path.isfile(fp):
                self._add_single_file(fp)
            elif os.path.isdir(fp):
                self._add_folder(fp)
    def _add_files(self):
        mode = self.mode_var.get()
        if mode == 'to_md':
            exts = [('Word/PDF files', '*.docx *.pdf'), ('All files', '*.*')]
        elif mode == 'to_docx':
            exts = [('Markdown files', '*.md'), ('All files', '*.*')]
        else:
            exts = [('Markdown/Word/PDF files', '*.md *.docx *.pdf'), ('All files', '*.*')]

        paths = filedialog.askopenfilenames(
            title=t('select_files', self.lang),
            filetypes=exts
        )
        for p in paths:
            self._add_single_file(p)

    def _add_folder_dialog(self):
        folder = filedialog.askdirectory(title=t('select_folder', self.lang))
        if folder:
            self._add_folder(folder)

    def _add_single_file(self, file_path):
        if file_path in self.files:
            return
        ext = Path(file_path).suffix.lower()
        mode = self.mode_var.get()
        valid = (mode == 'to_md' and ext in ('.docx', '.pdf')) or \
                (mode == 'to_docx' and ext == '.md') or \
                (mode == 'auto' and ext in ('.md', '.docx', '.pdf'))
        if not valid:
            return
        self.files.append(file_path)
        self._refresh_file_list()

    def _add_folder(self, folder_path):
        if folder_path in self.files:
            return
        mode = self.mode_var.get()
        
        # Verify folder exists and contains supported files
        has_files = False
        if mode == 'to_md':
            file_exts = ('.docx', '.pdf')
            error_msg = 'No se encontraron archivos Word (.docx) o PDF en:'
        elif mode == 'to_docx':
            file_exts = ('.md',)
            error_msg = 'No se encontraron archivos Markdown (.md) en:'
        else:
            file_exts = ('.md', '.docx', '.pdf')
            error_msg = 'No se encontraron archivos Markdown (.md), Word (.docx) o PDF en:'
        
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if f.lower().endswith(file_exts):
                    has_files = True
                    break
            if has_files:
                break
        
        if not has_files:
            messagebox.showwarning(
                'Sin archivos',
                f'{error_msg} {folder_path}'
            )
            return
        
        self.files.append(folder_path)
        self._refresh_file_list()

    def _remove_file(self, file_path):
        if file_path in self.files:
            self.files.remove(file_path)
        if file_path in self.file_widgets:
            self.file_widgets[file_path].destroy()
            del self.file_widgets[file_path]
        self._refresh_file_list()

    def _clear_list(self):
        self.files.clear()
        for w in self.file_widgets.values():
            w.destroy()
        self.file_widgets.clear()
        self._refresh_file_list()

    def _refresh_file_list(self):
        for w in self.file_widgets.values():
            w.destroy()
        self.file_widgets.clear()

        if not self.files:
            if not hasattr(self, 'drop_label') or not self.drop_label.winfo_exists():
                self.drop_label = ctk.CTkLabel(
                    self.file_scroll, text=t('drop_here', self.lang),
                    font=ctk.CTkFont(size=14)
                )
            self.drop_label.pack(expand=True, fill="both", pady=50)
            return
        else:
            if hasattr(self, 'drop_label'):
                try:
                    self.drop_label.pack_forget()
                except Exception:
                    pass

        for fp in self.files:
            name = os.path.basename(fp)
            ext = Path(fp).suffix.lower()
            is_folder = os.path.isdir(fp)
            icon_map = {'.docx': '📄', '.pdf': '📕', '.md': '📝'}
            icon = '📁' if is_folder else icon_map.get(ext, '❓')

            frame = ctk.CTkFrame(self.file_scroll)
            frame.pack(fill="x", padx=4, pady=2)
            frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(frame, text=icon, width=30,
                         font=ctk.CTkFont(size=18)).grid(
                row=0, column=0, padx=(10, 4), pady=8, sticky='w')

            fname_lbl = ctk.CTkLabel(frame, text=name, anchor='w',
                                     font=ctk.CTkFont(size=13))
            fname_lbl.grid(row=0, column=1, padx=4, pady=8, sticky='ew')

            status_lbl = ctk.CTkLabel(frame, text=f'⏳ {t("status_pending", self.lang)}',
                                      width=140, font=ctk.CTkFont(size=12))
            status_lbl.grid(row=0, column=2, padx=4, pady=8, sticky='e')

            rm_btn = ctk.CTkButton(frame, text='✕', width=28, height=28,
                                   fg_color='transparent',
                                   command=lambda f=fp: self._remove_file(f))
            rm_btn.grid(row=0, column=3, padx=(4, 10), pady=8)

            self.file_widgets[fp] = frame

    def _update_file_status_in_list(self, file_path, status):
        frame = self.file_widgets.get(file_path)
        if not frame:
            return
        children = frame.winfo_children()
        if len(children) >= 3:
            status_lbl = children[2]
            if status == 'pending':
                status_lbl.configure(text=f'⏳ {t("status_pending", self.lang)}',
                                     text_color=('gray30', 'gray60'))
            elif status == 'processing':
                status_lbl.configure(text=f'⏳ {t("status_processing", self.lang)}',
                                     text_color='yellow')
            elif status == 'done':
                status_lbl.configure(text=f'✅ {t("status_done", self.lang)}',
                                     text_color='green')
            elif status == 'error':
                status_lbl.configure(text=f'❌ {t("status_error", self.lang)}',
                                     text_color='red')

    def _select_output(self):
        path = filedialog.askdirectory(
            title=t('select_output', self.lang),
            initialdir=self.output_dir
        )
        if path:
            self.output_dir = path
            self.output_label.configure(text=os.path.basename(path) or path)

    def _generate_ai_prompt(self):
        desktop = os.path.expanduser('~/Desktop')
        fname = 'fastMd_AI_Prompt.md' if self.lang == 'en' else 'fastMd_Prompt_IA.md'
        path = os.path.join(desktop, fname)
        save_prompt_to_file(path, self.lang)
        messagebox.showinfo(
            title=t('ai_prompt_title', self.lang),
            message=f"{t('ai_prompt_msg', self.lang)}\n{path}"
        )

    def _show_help(self):
        win = ctk.CTkToplevel(self.root)
        win.title(t('help_title', self.lang))
        win.geometry('580x460')
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        frame = ctk.CTkScrollableFrame(win, fg_color='transparent')
        frame.pack(fill='both', expand=True, padx=15, pady=15)

        if self.lang == 'es':
            lines = [
                ('🚀 fastMd v1.0', 20, True),
                ('', 4, False),
                ('Conversor bidireccional de documentos con normas APA 7ª edición.', 13, False),
                ('', 8, False),
                ('📋 CÓMO USAR', 16, True),
                ('', 4, False),
                ('1️⃣  Agrega archivos con el botón "➕ Agregar archivos" o arrástralos directamente a la ventana.', 13, False),
                ('2️⃣  Elige el modo de conversión:', 13, False),
                ('     • Word/PDF → Markdown  —  convierte .docx o .pdf a .md', 13, False),
                ('     • Markdown → Word (APA 7)  —  convierte .md a .docx con formato APA 7', 13, False),
                ('3️⃣  Selecciona la carpeta de salida con "📂 Carpeta salida".', 13, False),
                ('4️⃣  Presiona "🚀 Convertir todo" y espera a que se procesen.', 13, False),
                ('', 8, False),
                ('🎯 APA 7 automático', 16, True),
                ('', 4, False),
                ('• Portada completa: título, autor, institución, curso, profesor, fecha', 13, False),
                ('• Times New Roman 12pt · Interlineado doble · Márgenes 1"', 13, False),
                ('• Sangría primera línea 0.5" · Niveles de heading APA 7', 13, False),
                ('• Referencias con sangría francesa · Números de página', 13, False),
                ('', 8, False),
                ('🤖 Botón "Prompt IA"', 16, True),
                ('', 4, False),
                ('Genera un archivo .md con instrucciones detalladas para que ChatGPT,', 13, False),
                ('Claude o Gemini estructuren su respuesta en el formato exacto que', 13, False),
                ('fastMd necesita para producir un documento Word APA 7 perfecto.', 13, False),
                ('', 8, False),
                ('📁 Formatos soportados', 16, True),
                ('', 4, False),
                ('• Entrada: .docx, .pdf, .md', 13, False),
                ('• Salida: .md o .docx (según el modo)', 13, False),
                ('• Procesamiento en paralelo: varios archivos a la vez', 13, False),
            ]
        else:
            lines = [
                ('🚀 fastMd v1.0', 20, True),
                ('', 4, False),
                ('Bidirectional document converter with APA 7th edition formatting.', 13, False),
                ('', 8, False),
                ('📋 HOW TO USE', 16, True),
                ('', 4, False),
                ('1️⃣  Add files with "➕ Add Files" button or drag & drop them onto the window.', 13, False),
                ('2️⃣  Choose conversion mode:', 13, False),
                ('     • Word/PDF → Markdown  —  converts .docx or .pdf to .md', 13, False),
                ('     • Markdown → Word (APA 7)  —  converts .md to .docx with APA 7 format', 13, False),
                ('3️⃣  Select the output folder with "📂 Output Folder".', 13, False),
                ('4️⃣  Press "🚀 Convert All" and wait for processing.', 13, False),
                ('', 8, False),
                ('🎯 APA 7 automatic', 16, True),
                ('', 4, False),
                ('• Full cover page: title, author, institution, course, professor, date', 13, False),
                ('• Times New Roman 12pt · Double spacing · 1" margins', 13, False),
                ('• First line indent 0.5" · APA 7 heading levels', 13, False),
                ('• References with hanging indent · Page numbers', 13, False),
                ('', 8, False),
                ('🤖 "AI Prompt" button', 16, True),
                ('', 4, False),
                ('Generates a .md file with detailed instructions so ChatGPT,', 13, False),
                ('Claude or Gemini can structure their output in the exact format', 13, False),
                ('fastMd needs to produce a perfect APA 7 Word document.', 13, False),
                ('', 8, False),
                ('📁 Supported formats', 16, True),
                ('', 4, False),
                ('• Input: .docx, .pdf, .md', 13, False),
                ('• Output: .md or .docx (depending on mode)', 13, False),
                ('• Parallel processing: multiple files at once', 13, False),
            ]

        for text, size, bold in lines:
            if not text:
                ctk.CTkLabel(frame, text='').pack()
            else:
                lbl = ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=size, weight='bold' if bold else 'normal'),
                                   anchor='w', justify='left')
                lbl.pack(fill='x', anchor='w')

        ctk.CTkButton(win, text='OK', width=100, command=win.destroy).pack(pady=(0, 10))

    def _switch_language(self, value):
        self.lang = 'es' if 'ES' in value else 'en'
        self.add_btn.configure(text=t('add_files', self.lang))
        self.add_folder_btn.configure(text=t('add_folder', self.lang))
        self.output_btn.configure(text=t('output_folder', self.lang))
        self.ai_btn.configure(text=t('ai_prompt', self.lang))
        self.help_btn.configure(text=t('help', self.lang))
        self.to_md_radio.configure(text=t('mode_to_md', self.lang))
        self.to_docx_radio.configure(text=t('mode_to_docx', self.lang))
        self.auto_radio.configure(text=t('mode_auto', self.lang))
        self.convert_btn.configure(text=t('convert_all', self.lang))
        self.clear_btn.configure(text=t('clear_list', self.lang))
        self.apa_title.configure(text=t('apa_settings', self.lang))
        self.apa_font_lbl.configure(text=t('font', self.lang))
        self.apa_spacing_lbl.configure(text=t('spacing', self.lang))
        self.cover_check.configure(text=t('cover_page', self.lang))
        self.pages_check.configure(text=t('page_numbers', self.lang))
        self._refresh_file_list()

    def _on_mode_change(self):
        self._clear_list()

    def _convert_all(self):
        if not self.files:
            messagebox.showwarning(t('no_files', self.lang),
                                   t('no_files', self.lang))
            return

        os.makedirs(self.output_dir, exist_ok=True)
        mode = self.mode_var.get()

        self.convert_btn.configure(state='disabled', text='⏳ ...')
        self.add_btn.configure(state='disabled')
        self.add_folder_btn.configure(state='disabled')
        self.clear_btn.configure(state='disabled')
        self.progress_bar.set(0)
        self.status_label.configure(text=t('progress_title', self.lang))

        for fp in self.files:
            self._update_file_status_in_list(fp, 'processing')

        def on_file_status(file_path, status, message, current, total):
            self.root.after(0, lambda: self._on_file_status(
                file_path, status, current, total))

        def on_done(completed, errors, total):
            self.root.after(0, lambda: self._on_done(completed, errors, total))

        self.worker.start_conversion(
            list(self.files), mode, self.output_dir,
            on_file_status, on_done,
            {
                'include_cover': self.cover_var.get(),
                'include_page_numbers': self.pages_var.get(),
            }
        )

    def _on_file_status(self, file_path, status, current, total):
        self._update_file_status_in_list(file_path, status)
        pct = current / total if total > 0 else 0
        self.progress_bar.set(pct)
        self.status_label.configure(
            text=f"{t('progress_title', self.lang)} {current} {t('progress_of', self.lang)} {total}"
        )

    def _on_done(self, completed, errors, total):
        self.convert_btn.configure(state='normal', text=t('convert_all', self.lang))
        self.add_btn.configure(state='normal')
        self.add_folder_btn.configure(state='normal')
        self.clear_btn.configure(state='normal')
        self.progress_bar.set(1)
        final_status = 'error' if errors else 'done'
        for fp in self.files:
            self._update_file_status_in_list(fp, final_status)
        msg = f"✅ {t('conversion_done', self.lang)}: {completed} {t('files_saved', self.lang)} {self.output_dir}"
        if errors:
            msg += f" ({errors} {t('status_error', self.lang)})"
        self.status_label.configure(text=msg)

    def _on_close(self):
        self.worker.cancel()
        self.root.destroy()
