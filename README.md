# 🚀 fastMd v1.0

**Conversor bidireccional de documentos con normas APA 7ª edición**

Convierte fácilmente entre Word, PDF y Markdown manteniendo la estructura de carpetas. Ideal para estudiantes, investigadores y profesionales que necesitan trabajar con múltiples formatos.

---

## ✨ Características

### 📄 Conversión Bidireccional
- **Word/PDF → Markdown**: Convierte `.docx` y `.pdf` a `.md` con extracción de imágenes
- **Markdown → Word (APA 7)**: Convierte `.md` a `.docx` con formato completo APA 7ª edición

### 📁 Soporte de Carpetas
- Procesa **carpetas completas** manteniendo la estructura de directorios
- Busca recursivamente archivos en subcarpetas
- Crea automáticamente la estructura en la carpeta de salida
- Funciona en **ambas direcciones** de conversión

### 🎯 Formato APA 7 Automático
- ✅ Portada completa (título, autor, institución, curso, profesor, fecha)
- ✅ Times New Roman 12pt
- ✅ Interlineado doble
- ✅ Márgenes de 1 pulgada
- ✅ Sangría de primera línea 0.5"
- ✅ Niveles de heading según APA 7
- ✅ Referencias con sangría francesa
- ✅ Números de página automáticos

### ⚡ Procesamiento Rápido
- Procesamiento en paralelo (múltiples archivos simultáneamente)
- Interfaz gráfica intuitiva con barra de progreso

### 🤖 Integración con IA
- Generador de prompts para ChatGPT, Claude y Gemini
- Instrucciones detalladas para que la IA estructure documentos perfectos

---

## 🛠️ Requisitos

- **Python 3.8+**
- Sistema operativo: Windows, macOS o Linux

### Dependencias
```
python-docx
pdf2image
pillow
customtkinter
tkinterdnd2
```

---

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/cxcristian/FastMd.git
cd fastMd
```

### 2. Crear entorno virtual (opcional pero recomendado)
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
python main.py
```

O en Windows, simplemente ejecuta:
```bash
run_fastMd.bat
```

---

## 🎯 Cómo Usar

### Opción 1: Interfaz Gráfica (Recomendado)
1. **Agregar archivos/carpetas**
   - Haz clic en "➕ Agregar archivos" y selecciona archivos o carpetas
   - O arrastra archivos/carpetas directamente a la ventana

2. **Seleccionar modo de conversión**
   - 📝 **Word/PDF → Markdown**: Convierte documentos de Word/PDF a Markdown
   - 📄 **Markdown → Word (APA 7)**: Convierte Markdown a Word con formato APA 7

3. **Configurar carpeta de salida**
   - Haz clic en "📂 Carpeta salida" para elegir dónde guardar los resultados

4. **Configurar opciones APA 7** (solo para Markdown → Word)
   - Portada: Incluir portada automática
   - Números de página: Agregar números de página

5. **Convertir**
   - Haz clic en "🚀 Convertir todo" y espera a que se procesen los archivos
   - Verás una barra de progreso con el estado de cada conversión

### Opción 2: Línea de Comandos
```bash
# Conversión individual de archivo
python -m app.converters.docx_to_md input.docx output.md ./images

# Conversión de carpeta completa
python -m app.worker
```

---

## 📁 Estructura de Carpetas

```
fastMd/
├── main.py                    # Punto de entrada principal
├── requirements.txt           # Dependencias del proyecto
├── run_fastMd.bat            # Script para ejecutar en Windows
├── README.md                 # Este archivo
├── app/
│   ├── __init__.py
│   ├── gui.py               # Interfaz gráfica (CustomTkinter)
│   ├── worker.py            # Procesamiento de conversiones (multihilo)
│   ├── i18n.py              # Internacionalización (ES/EN)
│   ├── ai_prompt.py         # Generador de prompts IA
│   ├── apa7.py              # Formatter APA 7
│   └── converters/
│       ├── __init__.py
│       ├── docx_to_md.py    # Conversor Word → Markdown
│       ├── pdf_to_md.py     # Conversor PDF → Markdown
│       └── md_to_docx.py    # Conversor Markdown → Word
└── output/                  # Carpeta para archivos convertidos
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Convertir una carpeta de Word a Markdown

**Estructura inicial:**
```
MisDocumentos/
├── capitulo1.docx
├── capitulo2.docx
└── apendices/
    └── figuras.docx
```

**Después de convertir:**
```
output/
└── MisDocumentos/
    ├── capitulo1.md
    ├── capitulo1_images/
    ├── capitulo2.md
    ├── capitulo2_images/
    └── apendices/
        ├── figuras.md
        └── figuras_images/
```

### Ejemplo 2: Convertir Markdown a Word con APA 7

**Estructura inicial:**
```
TrabajosFinales/
├── introduccion.md
├── metodologia.md
└── resultados.md
```

**Después de convertir:**
```
output/
└── TrabajosFinales/
    ├── introduccion.docx  (con formato APA 7)
    ├── metodologia.docx   (con formato APA 7)
    └── resultados.docx    (con formato APA 7)
```

---

## 🤖 Integración con IA

fastMd incluye un generador de prompts para ChatGPT, Claude y Gemini:

1. Haz clic en "Prompt IA" en la interfaz
2. Se generará un archivo `.md` con instrucciones detalladas
3. Copia el contenido y pégalo en tu IA preferida
4. La IA estructurará perfectamente el documento en Markdown
5. Convierte el resultado con fastMd a Word (APA 7) automáticamente

**Ventajas:**
- Documentos perfectamente formateados
- Evita reformateo manual
- Compatibilidad garantizada con APA 7

---

## 🌐 Idiomas Soportados

- 🇪🇸 Español (es)
- 🇺🇸 English (en)

Cambia el idioma desde el botón de selector en la interfaz.

---

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Carpeta de salida personalizada
set OUTPUT_DIR=C:\MisCarpeta\Salida

# Idioma por defecto
set APP_LANG=es
```

### Opciones APA 7 Personalizadas
Edita `app/apa7.py` para:
- Cambiar la fuente
- Ajustar márgenes
- Modificar espaciado
- Personalizar portada

---

## 📊 Formatos Soportados

### Entrada
| Formato | Conversión |
|---------|-----------|
| `.docx` | Word → Markdown |
| `.pdf`  | PDF → Markdown |
| `.md`   | Markdown → Word |

### Salida
| Formato | Conversión |
|---------|-----------|
| `.md`   | ← Word/PDF |
| `.docx` | ← Markdown |

---

## 🐛 Solución de Problemas

### Error: "No module named 'customtkinter'"
```bash
pip install customtkinter
```

### Error: "No module named 'docx'"
```bash
pip install python-docx
```

### Las imágenes no se extraen del PDF
Asegúrate de tener Ghostscript instalado:
```bash
# Windows
choco install ghostscript

# macOS
brew install ghostscript

# Linux
sudo apt-get install ghostscript
```

### La interfaz gráfica no aparece
- Asegúrate de estar ejecutando con Python 3.8 o superior
- En Linux, puede que necesites instalar dependencias adicionales de Tk:
```bash
sudo apt-get install python3-tk
```

---

## 📝 Notas sobre APA 7

La conversión de Markdown a Word sigue las directrices completas de APA 7ª edición:

- Portada con información completa
- Página de tabla de contenidos (automática)
- Encabezados y títulos formateados
- Márgenes estándar de 1"
- Fuente Times New Roman 12pt
- Interlineado doble en todo el documento
- Referencias con sangría francesa
- Números de página en esquina superior derecha

**Limitaciones:**
- Las referencias bibliográficas deben estar manualmente formateadas en APA 7
- Las tablas se convierten básicamente (se recomienda ajustar manualmente)
- Los elementos complejos de Word pueden necesitar ajustes

---

## 🚀 Mejoras Futuras

- [ ] Soporte para más formatos (Google Docs, ODT)
- [ ] Interfaz en más idiomas
- [ ] Conversión batch desde línea de comandos
- [ ] Configuración de opciones APA 7 en GUI
- [ ] Vista previa antes de convertir
- [ ] Historial de conversiones
- [ ] API REST para integraciones

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver `LICENSE` para más detalles.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📧 Soporte

Si encuentras problemas o tienes sugerencias:

1. Abre un issue en GitHub
2. Incluye:
   - Sistema operativo y versión de Python
   - Archivo de ejemplo que cause el problema
   - Mensaje de error completo
   - Pasos para reproducir el problema

---

## ⭐ Si te gusta fastMd

¡No olvides darle una estrella en GitHub! ⭐

---

## 🎓 Casos de Uso

fastMd es perfecto para:

- ✅ Estudiantes universitarios escribiendo tesis
- ✅ Investigadores documentando proyectos
- ✅ Profesionales creando reportes en APA
- ✅ Equipos colaborativos usando Markdown
- ✅ Conversión masiva de documentos
- ✅ Estandarización de formatos documentales

---

## 📌 Versión

**v1.0** - Mayo 2026

- ✅ Conversión bidireccional completa
- ✅ Soporte de carpetas con estructura preservada
- ✅ Formato APA 7 automático
- ✅ Interfaz gráfica intuitiva
- ✅ Procesamiento multihilo
- ✅ Soporte multiidioma (ES/EN)

---

**Hecho con ❤️ para estudiantes e investigadores.**
