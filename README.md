# Projeto de Análise e Visualização de Dados de Vendas da Padaria

Este projeto foi desenvolvido como atividade prática da disciplina Tópicos de Big Data em Python, com o objetivo de aplicar conceitos de análise de dados, manipulação de arquivos XML e visualização interativa utilizando ferramentas modernas da linguagem Python.

A aplicação permite explorar dados reais de vendas obtidos a partir de notas fiscais em XML, fornecidas por uma padaria de pequeno/médio porte localizada em Copacabana (RJ). O projeto envolve organização dos dados, construção de um banco de dados SQLite e desenvolvimento de um dashboard interativo para auxiliar na tomada de decisões do negócio.

Banco SQLite utilizado: https://drive.google.com/drive/folders/1DOImvxNuPYJRaxNlcTZ3HtPwKV4P9ujT?usp=sharing
(Lembrando que o banco de dados baixado precisa ser colocado na pasta Dashboard-paradaria junto com os outros arquivos.)

## Objetivos

-   Demonstrar a aplicação prática de técnicas de análise e visualização de dados estudadas na disciplina.
-   Organizar e estruturar dados extraídos de XML em um banco SQLite.
-   Criar um dashboard interativo para apoiar a gestão da padaria.
-   Utilizar ferramentas modernas do ecossistema Python para realizar todo o processo de ETL (extração, transformação e carregamento dos dados) e gerar visualizações interativas.

## Ferramentas Utilizadas

-   **Python**: Linguagem principal para manipulação dos arquivos XML, processamento e consultas ao banco.
-   **Pandas**: Utilizada para criação e transformação dos DataFrames antes de da criação do dashboard.
-   **SQLite**: Banco de dados utilizado para armazenar as informações de vendas.
-   **Plotly**: Utilizado para a criação de gráficos interativos e visualmente claros.
-   **Streamlit**: Responsável pela interface do dashboard interativo.
-   **Visual Studio Code (VS Code)**: Ambiente de desenvolvimento utilizado pela equipe.

## Funcionalidades

-   **Consulta automática ao banco SQLite**: Carrega e trata os dados das notas fiscais e itens vendidos.
-   **Filtro por ano e mês**: Permite selecionar uma ou mais categorias de produtos.
-   **Visualizações interativas**:
    -   Gráfico de linha mostrando a evolução mensal do valor total vendido.
    -   Gráfico de barras com os Top 10 produtos mais vendidos.
    -   Gráfico de pizza com os Top 3 produtos do período filtrado.
    -   Gráfico de barras exibindo o total vendido por forma de pagamento.

## Como Executar o Projeto

1. Clone este repositório em sua máquina local:

    ```bash
    git clone https://github.com/jeansouza1994/Dashboard-padaria.git
    ```

2. Certifique-se de ter o Python instalado. Instale as dependências necessárias:

    ```bash
    pip install streamlit pandas plotly
    ```

3. Baixe o banco de dados SQLite pelo link abaixo e coloque na pasta principal(Dashboard-padaria):

    ```bash
    https://drive.google.com/drive/folders/1DOImvxNuPYJRaxNlcTZ3HtPwKV4P9ujT?usp=sharing
    ```

4. Execute a aplicação utilizando o Streamlit:

    ```bash
    streamlit run main.py
    ```

## Estrutura do projeto

```bash
DASHBOARD-PADARIA
│
├── Insercao-dados-bd.py        # Script responsável por ler XMLs e inserir dados no banco SQLite
├── main.py                     # Aplicação principal do Streamlit para visualização dos dados
├── notas_fiscais.db            # Banco de dados SQLite contendo as notas fiscais processadas
├── sql-criacao-tabela.txt      # Script SQL com a estrutura da tabela utilizada no banco
└── README.md                   # Documentação do projeto
```

## Equipe do Projeto

-   Claudio Rebelo
-   Jean Souza
-   Natália Paulino
-   Rafael da Silva
-   Aloisio Santos

-   Prof. Raphael Mauricio(Orientador)
