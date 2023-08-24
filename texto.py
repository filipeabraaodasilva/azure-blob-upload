# Importações de bibliotecas de terceiros
import re


# Função para tratamento de texto
class Tratamento:
    def caracteres_especiais_e_extensao(self, texto: str, extensao: str) -> str:

        self.__texto = texto

        padrao = re.compile(re.escape(f".{extensao}"), re.IGNORECASE)
        self.__texto = padrao.sub("", self.__texto)
        self.__texto = self.__caract(texto)

        return self.__texto

    def __caract(self, texto: str):

        texto_tratado = texto \
            .replace("\\", " ") \
            .replace("/", " ") \
            .replace("|", " ") \
            .replace("<", " ") \
            .replace(">", " ") \
            .replace("*", " ") \
            .replace(":", " ") \
            .replace('"', " ") \
            .replace("'", " ") \
            .replace("?", " ")

        return texto_tratado