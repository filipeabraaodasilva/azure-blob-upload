# Importações de bibliotecas de terceiros
from typing import Optional
import pyodbc
from pyodbc import Row


# Super classe para realizar conexão com o banco
class Conexao:
    def __init__(self) -> None:
        self.__conn = pyodbc.connect(
            'Driver={SQL Server};'
            'Server=nome_servidor.database.windows.net;'
            'Database=banco_de_dados;'
            'Uid=usuario;'
            'Pwd=senha;'
        )


# Função para obter chaves para acesso ao Azure
class UnidadeCliente(Conexao):
    def __init__(self, id_unidade_cliente: str) -> None:
        super().__init__()
        self.__cursor = self._Conexao__conn.cursor()
        self.__cursor.execute("""
            SELECT      u.Id AS 'IdUnidade',
                        c.Id AS 'IdCliente',
                        u.Azure_NomeConta AS 'ContaAzure',
                        u.Azure_ChaveAcessoPrimario AS 'ChaveAzure'
            FROM        Schema.UnidadeCliente uc
            INNER JOIN  Schema.Unidade u ON u.Id = uc.IdUnidade AND uc.Id = ?
            INNER JOIN  Schema.Cliente c ON c.Id = uc.IdCliente
        """, id_unidade_cliente)

        self.__resultado = self.__cursor.fetchone()
        self.__cursor.close()
        self._Conexao__conn.close()


    @property
    def get_retorno(self) -> dict:
        dados = {
            "id_cliente": self.__resultado[1],
            "id_unidade": self.__resultado[0],
            "azure_conta": self.__resultado[2],
            "azure_chave": self.__resultado[3]
        }
        return dados


class Documento(Conexao):
    def __init__(self, registro: int) -> None:
        super().__init__()
        self.__cursor = self._Conexao__conn.cursor()
        self.__cursor.execute("""
            SELECT  d.Id 
            FROM    Schema.Documento d 
            WHERE   d.Codigo = {}""".format(registro))

        self.__resultado = self.__cursor.fetchone()
        self.__cursor.close()
        self._Conexao__conn.close()

    @property
    def get_id_documento(self) -> Optional[Row]:
        return self.__resultado


# Função para verificar existência do arquivo
class Arquivo(Conexao):
    def __init__(self, registro: int, arquivo: str) -> None:
        super().__init__()
        self.__cursor = self._Conexao__conn.cursor()
        self.__cursor.execute("""
        SELECT      COUNT(i.Id) AS 'QtdeArquivos' 
        FROM        Schema.Documento d 
        INNER JOIN  Schema.Imagem i ON i.IdDocumento = d.Id 
                    AND i._del IS NULL 
                    AND d.codigo = '{}'
                    AND i.Nome = '{}'
        """.format(registro, arquivo))
        self.__resultado = self.__cursor.fetchone()

        self.__cursor.close()
        self._Conexao__conn.close()

        self.__existente: int = self.__resultado[0]

    @property
    def get_existente(self) -> int:
        return self.__existente


# Função para verificar existência da extensão
class Extensao(Conexao):
    def __init__(self, extensao: str) -> None:
        super().__init__()
        self.__cursor = self._Conexao__conn.cursor()
        self.__cursor.execute("""
        SELECT  TOP 1 e.Id AS 'IdExtensao'
        FROM    Schema.Extensao e 
        WHERE   e.Extensao = '{}'
        """.format(extensao))
        self.__resultado = self.__cursor.fetchone()

        self.__cursor.close()
        self._Conexao__conn.close()

    @property
    def get_id_extensao(self) -> int:
        return self.__resultado
