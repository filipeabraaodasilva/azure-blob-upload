# Importações de bibliotecas de terceiros
import os
import magic
from tqdm import tqdm
from typing import List
from azure.storage.blob import BlobServiceClient, BlobClient, BlobType,ContentSettings

# Importações de bibliotecas internas
from id import Novo
from pdf import ContarPaginas
from texto import Tratamento
from sql import UnidadeCliente, Documento, Arquivo, Extensao


# Aplicação
pasta_de_trabalho: str = input("\nDIGITE O CAMINHO PARA A PASTA DE TRABALHO: ")
id_usuario_resp: str = input("\nDIGITE O IDUSUARIO RESPONSÁVEL PELA ASSOCIAÇÃO: ")
id_unidade_cliente: str = input("\nDIGITE O IDUNIDADECLIENTE DE DESTINO DOS ARQUIVOS: ")

azure = UnidadeCliente(id_unidade_cliente)
dados_azure = azure.get_retorno

url_azure: str = "https://{}.blob.core.windows.net".format(dados_azure["azure_conta"])

# Crie um cliente de serviço de blob
blob_service_client = BlobServiceClient(account_url= url_azure, credential=dados_azure["azure_chave"])

# Criando lista para receber as extensões dos arquivos a serem associados
lista_de_extensoes: List = []
lista_de_extensoes_inexistentes: List = []

with open(pasta_de_trabalho + "\\lista-img.txt", "r") as verificar_extensoes:
    for linha in verificar_extensoes:

        # Tratando o txt para obter as extensões dos arquivos
        registro, arquivo_nome = linha.strip().split("|")
        caminho_arquivo: str = "{}\\Files\\{}".format(pasta_de_trabalho, arquivo_nome)
        extensao: str = os.path.splitext(caminho_arquivo)[1]
        extensao: str = extensao.replace(".", "").lower()

        # Verificando se a extensão existe na lista e se não, inserindo-a na lista
        if extensao not in lista_de_extensoes:
            lista_de_extensoes.append(extensao)

    for extensao in lista_de_extensoes:

        # Verificando se a extensão existe no banco de dados
        extensao_objeto = Extensao(extensao)
        id_extensao: int = extensao_objeto.get_id_extensao

        # Variáveis para utilizar no concat
        icone: str = 'icone'

        # Montando o insert caso não existir
        if id_extensao is None:
            with open(pasta_de_trabalho + "\\00_Extensoes_Insert.sql", "a", encoding="utf-8") as insert_extensoes:
                insert_extensoes.write("INSERT INTO Schema.Extensao (Extensao, Icone) VALUES ('{}', '{}');\n".format(
                    extensao.lower(),
                    icone
                ))
            lista_de_extensoes_inexistentes.append(extensao)


if len(lista_de_extensoes_inexistentes) != 0:
    print("\nExecute o arquivo '00_Extensoes_Insert.sql' que está na pasta de trabalho,")
    print("Ao finalizar o processo, pressione enter para que a aplicação prossiga com o associação.\n")

    # Pausar a aplicação para aguardar o usuário executar o insert de extensões
    os.system("pause")
    print("\n")

else:
    pass

with open(pasta_de_trabalho + "\\lista-img.txt", "r") as arquivos:

    # Conta o total de linhas para inserir a barra de progresso
    total_linhas = sum(1 for linha in arquivos)
    arquivos.seek(0)
    print('\n')

    for linha in tqdm(arquivos, total=total_linhas, desc='Progresso'):

        # Extrair as informações de código, nome de arquivo do arquivo txt
        registro, arquivo_nome = linha.strip().split("|")
        arquivo_nome: str = arquivo_nome.replace("'", " ")

        # Caminho completo para o arquivo
        caminho_arquivo: str = "{}\\Files\\{}".format(pasta_de_trabalho, arquivo_nome)

        # Obtendo IdDocumento do código de registro informado
        documento = Documento(registro)
        resultado = documento.get_id_documento
        id_documento: str = str(resultado[0])

        id_imagem: str = Novo.gerar_id()

        # Tentando obter o tamanho do arquivo
        try:
            tamanho: int = os.path.getsize(caminho_arquivo)

        except Exception as erro_tamanho:
            with open(pasta_de_trabalho + "\\Log" + "\\00_Erro_Extracao_de_Tamanho.txt", "a", encoding="utf-8") as log_tamanho:
                log_tamanho.write("Erro ao extrair o tamanho do arquivo '{}' | {}\n".format(arquivo_nome, erro_tamanho))

            continue

        # Obtém a extensão do arquivo
        extensao: str = os.path.splitext(caminho_arquivo)[1]
        extensao: str = extensao.replace(".", "").lower()

        # Tratando caracteres especiais
        tratamento_obj = Tratamento()
        arquivo_tratado: str = tratamento_obj.caracteres_especiais_e_extensao(arquivo_nome, extensao)

        arquivo_objeto = Arquivo(registro, arquivo_tratado)
        arquivo_existencia: bool = True if arquivo_objeto.get_existente > 0 else False

        extensao_objeto = Extensao(extensao)
        id_extensao: int = extensao_objeto.get_id_extensao[0]
        
        mime_type = ""

        if arquivo_existencia:
            with open(pasta_de_trabalho +
                      "\\Log" +
                      "\\00_Erro_Arquivo_Ja_Existente.txt",
                      "a",
                      encoding="utf-8"
                      ) as log_existente:
                log_existente.write("O arquivo '{}' já existe para o registro '{}'\n".format(arquivo_tratado, registro))

        else:
            try:
                if id_extensao is not None:
                    if extensao == "pdf":
                        paginas = ContarPaginas(caminho_arquivo)
                        qtde_paginas: int = paginas.get_numero_paginas
                        
                        mime_type = "application/pdf"

                    else:
                        qtde_paginas: str = "NULL"
                        
                        mime_type = magic.from_file(caminho_arquivo, mime=True)

                    with open(pasta_de_trabalho + "\\00_Imagem_Insert.sql", "a", encoding="utf-8") as insert_imagem:
                        insert_imagem.write("INSERT INTO Schema.Imagem VALUES ('{}', '{}', 1, 'http://{"
                                            "}.blob.core.windows.net/{}/{}.{}', '{}', {}, {}, GETDATE(), {}, '{}', "
                                            "NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);\n"
                                            .format(id_imagem.upper(),
                                                    id_documento.upper(),
                                                    dados_azure["azure_conta"],
                                                    dados_azure["id_cliente"].lower(),
                                                    id_imagem.lower(),
                                                    extensao,
                                                    arquivo_tratado,
                                                    qtde_paginas,
                                                    tamanho,
                                                    id_extensao,
                                                    id_usuario_resp.upper()))



                    blob_client = blob_service_client.get_blob_client(
                        container=dados_azure["id_cliente"].lower(),
                        blob="{}.{}".format(id_imagem.lower(), extensao)
                    )

                    # Abra o arquivo para leitura
                    with open(caminho_arquivo, "rb") as f:
                        data = f.read()
                        content_type = mime_type
                        blob_client.upload_blob(data,content_type=content_type)

                    with open(pasta_de_trabalho + "\\Log" + "\\00_Log_Sucesso.txt", "a", encoding="utf-8") as log_sucesso_up:
                        log_sucesso_up.write("DE: {} | PARA: {}.{}\n".format(arquivo_nome, id_imagem.lower(), extensao))

                else:
                    with open(pasta_de_trabalho +
                              "\\Log" +
                              "\\00_Erro_Extensao_Inexistente.txt",
                              "a",
                              encoding="utf-8"
                              ) as log_extensao:
                        log_extensao.write("A extensao {} não existe no banco de dados.\n".format(extensao))
            except Exception as erro_excecao:
                with open(pasta_de_trabalho +
                          "\\Log" +
                          "\\00_Erro_Desconhecido.txt",
                          "a",
                          encoding="utf-8"
                          ) as erro_desconhecido:
                    erro_desconhecido.write("Erro não tratado: {}\n".format(erro_excecao))
