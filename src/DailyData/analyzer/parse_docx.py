from docx import Document


def get_lines(file_path):
    doc = Document(file_path)
    return map(lambda p: p.text, doc.paragraphs)
