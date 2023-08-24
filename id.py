# Importações de bibliotecas de terceiros
import uuid


# Gerar novo id
class Novo:
    @staticmethod
    def gerar_id() -> str:
        return str(uuid.uuid4())
