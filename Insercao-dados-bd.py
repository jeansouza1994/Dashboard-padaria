import sqlite3
import xml.etree.ElementTree as ET
import os

CAMINHO_BANCO = "notas_fiscais.db"
CAMINHO_PASTA = "dados"
ANOS_VALIDOS = {"2022", "2023", "2024"}
MESES_VALIDOS = {"Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"}



# função para ler e extrair dados do XML da Nota fiscal eletrônica
def ler_extrair_dados_nota_fiscal(xml_path):
    # lê o XML e obtém o elemento raiz
    tree = ET.parse(xml_path)
    root = tree.getroot()

    ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

    # localiza o bloco principal da nota
    infNFe = root.find(".//nfe:infNFe", ns)
    if infNFe is None:
        raise ValueError(f"Elemento infNFe não encontrado em {xml_path}")

    # ID da nota
    id_nfe = infNFe.attrib.get("Id", "")
    if id_nfe.startswith("NFe"):
        id_nfe = id_nfe[3:]

    # extrai número, data e valor total da NF
    nNF = root.findtext(".//nfe:ide/nfe:nNF", default="", namespaces=ns)
    dhEmi = root.findtext(".//nfe:ide/nfe:dhEmi", default="", namespaces=ns)
    vNF_text = root.findtext(".//nfe:total/nfe:ICMSTot/nfe:vNF", default="0", namespaces=ns)

    # converte o valor da NF para float
    vNF = float(vNF_text.replace(",", "."))

    # separação da data em ano, mês e dia
    if "T" in dhEmi:
        data = dhEmi.split("T")[0]
    else:
        data = dhEmi

    ano, mes, dia = data.split("-")
    ano = ano.zfill(4)
    mes = mes.zfill(2)
    dia = dia.zfill(2)

    # pega o tipo de pagamento
    tPag_elem = root.find(".//nfe:pag/nfe:detPag/nfe:tPag", ns)
    tipo_pagamento = tPag_elem.text if tPag_elem is not None else None

    itens = []

    # cada det é um item(produto) da nota fiscal
    for det in root.findall(".//nfe:det", ns):
        prod = det.find("nfe:prod", ns)
        if prod is None:
            continue

        # monta um dicionário com os dados de cada item(produto)
        itens.append({
            "id_nfe": id_nfe,
            "numero_nf": nNF,
            "data_emissao": dhEmi,
            "valor_nf": vNF,
            "item_descricao": prod.findtext("nfe:xProd", default="", namespaces=ns),
            "item_valor_total": float(prod.findtext("nfe:vProd", default="0", namespaces=ns)),
            "item_quantidade": float(prod.findtext("nfe:qCom", default="0", namespaces=ns)),
            "item_valor_unit": float(prod.findtext("nfe:vUnCom", default="0", namespaces=ns)),
            "item_codigo": prod.findtext("nfe:cProd", default="", namespaces=ns),
            "ano": ano,
            "mes": mes,
            "dia": dia,
            "tipo_pagamento": tipo_pagamento
        })

    return itens


# inserção dos produtos no banco de dados SQLite
def inserir_itens_db(items):
    conn = sqlite3.connect(CAMINHO_BANCO)
    cur = conn.cursor()

    # cria a tabela caso não exista
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notas (
        id_nfe TEXT PRIMARY KEY,
        numero_nf TEXT,
        data_emissao TEXT,
        valor_nf REAL,
        item_descricao TEXT,
        item_valor_total REAL,
        item_quantidade REAL,
        item_valor_unit REAL,
        item_codigo TEXT,
        ano TEXT,
        mes TEXT,
        dia TEXT,
        tipo_pagamento TEXT
    )
    """)
    conn.commit()

    # insere cada item da nota fiscal no banco
    for item in items:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO notas (
                    id_nfe, numero_nf, data_emissao, valor_nf,
                    item_descricao, item_valor_total, item_quantidade,
                    item_valor_unit, item_codigo, ano, mes, dia, tipo_pagamento
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["id_nfe"],
                item["numero_nf"],
                item["data_emissao"],
                item["valor_nf"],
                item["item_descricao"],
                item["item_valor_total"],
                item["item_quantidade"],
                item["item_valor_unit"],
                item["item_codigo"],
                item["ano"],
                item["mes"],
                item["dia"],
                item["tipo_pagamento"]
            ))
        except sqlite3.IntegrityError:
            print(f"Nota já existe: {item['id_nfe']}")

    conn.commit()
    conn.close()


# rotina inicial – percorre as pastas e processa os XMLs

for ano in ANOS_VALIDOS:
    ano_path = os.path.join(CAMINHO_PASTA, ano)

    # se o ano não existir, avisa e pula
    if not os.path.isdir(ano_path):
        print(f"Ano não encontrado: {ano}")
        continue

    for mes in MESES_VALIDOS:
        mes_path = os.path.join(ano_path, mes)

        # se o mês não existir dentro daquele ano, pula
        if not os.path.isdir(mes_path):
            print(f"Mês não encontrado em {ano}: {mes}")
            continue

        # processa todos os XMLs dentro da pasta
        for file in os.listdir(mes_path):
            if file.lower().endswith(".xml"):
                xml_path = os.path.join(mes_path, file)
                try:
                    itens = ler_extrair_dados_nota_fiscal(xml_path)
                    inserir_itens_db(itens)
                    print(f"Inserido: {xml_path}")
                except Exception as e:
                    print(f"Erro ao processar: {xml_path}")
                    print("Erro:", e)

print("Finalizado com sucesso!")
