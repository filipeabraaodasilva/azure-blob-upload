# Importação de bibliotecas de terceiros
import fitz


# Função para contar as páginas quando o arquivo for PDF
class ContarPaginas:
    def __init__(self, caminho_arquivo: str) -> None:
        pdf_doc = fitz.open(caminho_arquivo)
        self.__num_paginas = pdf_doc.page_count
        pdf_doc.close()

    @property
    def get_numero_paginas(self):
        return self.__num_paginas
