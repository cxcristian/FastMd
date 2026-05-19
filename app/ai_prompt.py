PROMPT = """# fastMd - Guía de formato Markdown para conversión a Word APA 7

Esta guía te indica exactamente cómo estructurar tu respuesta en Markdown para que al procesarla con **fastMd** se genere un documento Word con **normas APA 7ª edición**.

## Estructura obligatoria del documento

Usa **YAML front matter** al inicio del archivo para los metadatos de la portada:

```yaml
---
title: "Título del documento"
author: "Nombre del autor"
institution: "Nombre de la institución"
course: "Nombre del curso"
professor: "Nombre del profesor"
date: "Fecha"
---
```

## Sistema de headings (títulos)

| Markdown | Resultado APA 7 |
|----------|-----------------|
| `# Título` | Nivel 1 - Centrado, negrita |
| `## Sección` | Nivel 2 - Izquierda, negrita |
| `### Subsección` | Nivel 3 - Izquierda, negrita cursiva |
| `#### Sub-subsección` | Nivel 4 - Sangría, negrita, punto final |
| `##### Nivel 5` | Nivel 5 - Sangría, negrita cursiva, punto final |

Usa **un solo `# Título`** como título principal del documento.

## Formato de texto

- **Negrita**: `**texto**` → **texto en negrita**
- *Cursiva*: `*texto*` → *texto en cursiva*
- ***Negrita cursiva***: `***texto***` → ***texto mixto***
- `Código`: `` `código` `` → código en línea

## Listas

**Listas con viñetas:**
```markdown
- Primer elemento
- Segundo elemento
  - Sub-elemento (con 2 espacios)
```

**Listas numeradas:**
```markdown
1. Primer elemento
2. Segundo elemento
   1. Sub-elemento (con 4 espacios)
```

## Tablas

```markdown
| Encabezado 1 | Encabezado 2 | Encabezado 3 |
|--------------|:------------:|-------------:|
| Celda        |   Centrado   |     Derecha  |
| Otra celda   |   Texto      |         $100 |
```

## Bloques de código

Usa bloques de código delimitados con ``` para código extenso:

```
```python
def ejemplo():
    return "Código formateado"
```
```

## Imágenes

```markdown
![Descripción de la imagen](ruta/a/imagen.png)
```

Las imágenes se insertarán en el documento Word con un tamaño apropiado.

## Citas y referencias

**Citas en el texto:**
```markdown
Según Autor (2023), el resultado fue...
Los resultados demostraron... (Autor, 2023).
```

**Sección de referencias:**
Al final del documento, crea una sección `## Referencias` y lista cada referencia en una línea separada. fastMd aplicará automáticamente sangría francesa (hanging indent) a cada entrada.

```markdown
## Referencias

Autor, A. A. (2023). *Título del libro*. Editorial.

Autor, B. B. (2023). Título del artículo. *Nombre de la Revista*, *12*(3), 45-67. https://doi.org/xxxx
```

## Notas importantes

1. **Portada**: fastMd genera automáticamente la portada con los metadatos del front matter
2. **Interlineado**: todo el documento tendrá interlineado doble
3. **Fuente**: Times New Roman 12pt
4. **Márgenes**: 1 pulgada (2.54 cm) en los cuatro lados
5. **Sangría**: primera línea con sangría de 0.5 pulgadas (excepto títulos y referencias)
6. **Números de página**: esquina superior derecha
7. **Saltos de página**: usa `---` para separar secciones

## Ejemplo completo

```yaml
---
title: "Impacto de la Inteligencia Artificial en la Educación Superior"
author: "María García López"
institution: "Universidad Nacional"
course: "Métodos de Investigación"
professor: "Dr. Juan Martínez"
date: "15 de mayo de 2026"
---
```

```markdown
# Impacto de la IA en Educación

## Introducción

La inteligencia artificial **ha transformado** la educación superior en las últimas décadas *de manera significativa*.

## Método

### Participantes

- 150 estudiantes universitarios
- 15 docentes
- 5 administradores

### Instrumentos

| Instrumento | Duración | Formato |
|-------------|:--------:|:-------:|
| Cuestionario | 30 min | Digital |
| Entrevista | 45 min | Presencial |

## Resultados

Según García (2025), los principales hallazgos fueron:

> La IA mejora el rendimiento académico en un 35%.

## Referencias

García, M. (2025). *Inteligencia artificial en educación*. Editorial Académica.

Pérez, J. (2024). Aprendizaje automático en aulas universitarias. *Revista de Educación*, *15*(2), 123-145. https://doi.org/10.1234/edu.2024.0152
```

---

**Al seguir esta guía, fastMd convertirá tu Markdown a un documento Word con formato APA 7 perfecto, sin que tengas que preocuparte por los estilos.**
"""


def generate_ai_prompt(lang='es'):
    if lang == 'en':
        return PROMPT_EN
    return PROMPT


PROMPT_EN = """# fastMd - Markdown Format Guide for APA 7 Word Conversion

This guide explains how to structure your Markdown output so that when processed with **fastMd**, it generates a Word document with **APA 7th edition** formatting.

## Required document structure

Use **YAML front matter** at the beginning of the file for cover page metadata:

```yaml
---
title: "Document Title"
author: "Author Name"
institution: "Institution Name"
course: "Course Name"
professor: "Professor Name"
date: "Date"
---
```

## Heading system

| Markdown | APA 7 Result |
|----------|--------------|
| `# Title` | Level 1 - Centered, Bold |
| `## Section` | Level 2 - Left, Bold |
| `### Subsection` | Level 3 - Left, Bold Italic |
| `#### Sub-subsection` | Level 4 - Indented, Bold, period |
| `##### Level 5` | Level 5 - Indented, Bold Italic, period |

Use **a single `# Title`** as the main document title.

## Text formatting

- **Bold**: `**text**` → **bold text**
- *Italic*: `*text*` → *italic text*
- ***Bold Italic***: `***text***` → ***mixed text***
- `Code`: `` `code` `` → inline code

## Lists

**Bullet lists:**
```markdown
- First item
- Second item
  - Sub-item (2 spaces indent)
```

**Numbered lists:**
```markdown
1. First item
2. Second item
   1. Sub-item (4 spaces indent)
```

## Tables

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|:--------:|---------:|
| Cell     | Centered |    Right |
| Another  | Text     |     $100 |
```

## Code blocks

Use fenced code blocks with ``` for extensive code.

## Images

```markdown
![Image description](path/to/image.png)
```

## References section

Create a `## References` section at the end. fastMd automatically applies hanging indent to each entry.
"""


def save_prompt_to_file(output_path, lang='es'):
    content = generate_ai_prompt(lang)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return output_path
