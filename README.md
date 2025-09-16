# Guia de Tabela de Medidas (ABNT)

Este repositório contém o código‑fonte de um aplicativo web desenvolvido em
Python com [Streamlit](https://streamlit.io) para estimar tamanhos numéricos
de roupas femininas de acordo com medidas corporais e o bíotipo da usuária.
O objetivo é fornecer um **guia didático** baseado em tabelas de referência
da ABNT (Associação Brasileira de Normas Técnicas) — não substitui a
consulta às tabelas oficiais de cada marca.

## Funcionalidades

* **Entrada de medidas:** altura, busto, cintura e quadril em centímetros.
* **Seleção de bíotipo:** Retangular, Violão, Ampulheta, Triângulo,
  Triângulo invertido ou Oval.
* **Figuras didáticas:** mini‑silhuetas desenhadas com `matplotlib` para
  auxiliar na identificação do formato do corpo.
* **Upload de foto opcional:** a foto é exibida apenas localmente e nunca
  armazenada no servidor.
* **Cálculo do tamanho sugerido:** encontra o melhor tamanho numérico (34‑62)
  comparando as medidas informadas com uma tabela de referência que cresce
  em incrementos de 4 cm para busto, cintura e quadril.
* **Top 3 tamanhos:** exibe os três tamanhos mais próximos, com suas
distâncias e as medidas de referência de cada um.
* **Exportação:** permite baixar os resultados em CSV e um relatório em PDF
  contendo suas medidas, o tamanho sugerido, o top 3 e as figuras.
* **Páginas informativas:** inclui seções de boas‑vindas, resultado, sobre
  e contato, com avisos sobre privacidade e limitações.

## Instalação e execução local

1. Clone ou baixe este repositório.
2. Instale as dependências (idealmente em um ambiente virtual):

   ```bash
   pip install -r requirements.txt
   ```

3. Execute o app com o Streamlit:

   ```bash
   streamlit run app.py
   ```

   O navegador abrirá automaticamente em `http://localhost:8501`.

## Estrutura do projeto

```
.
├── app.py            # Interface Streamlit e roteamento das páginas
├── logic.py          # Tabela de tamanhos, pesos por bíotipo e cálculo de distâncias
├── figures.py        # Geração de figuras esquemáticas dos bíotipos
├── export.py         # Funções para exportar resultados em CSV e PDF
├── assets/
│   └— favicon.png   # Ícone opcional do app
├── tests/
│   └— test_logic.py # Testes unitários básicos
├── requirements.txt  # Dependências do Python
├── README.md         # Este documento
└— .streamlit/
    └— config.toml   # Configuração visual do Streamlit
```

## Deploy no Streamlit Community Cloud

Para publicar o app e gerar um link público no [Streamlit Community
Cloud](https://streamlit.io/cloud), siga estes passos:

1. Faça login em sua conta no Streamlit Community Cloud.
2. Crie um novo aplicativo e conecte sua conta do GitHub.
3. Selecione este repositório e a branch `main` (ou a que contém o código).
4. Defina `app.py` como arquivo principal.
5. Clique em **Deploy**.  O serviço instalará as dependências listadas em
   `requirements.txt` e disponibilizará um link público.

**Alternativa:** você pode hospedar o app em um [Hugging Face
Space](https://huggingface.co/spaces) configurando a mesma estrutura de
arquivos e usando o mesmo `requirements.txt`.

## Avisos e limitações

* **Referência didática:** As tabelas de medidas da ABNT variam de acordo
  com a norma, o tipo de produto e a marca.  Este aplicativo utiliza um
  modelo simplificado com incrementos de 4 cm para fins educacionais.
* **Modelagens diferentes:** As dimensões finais de uma peça dependem do
  modelo, tecido e estilo.  Use o resultado como ponto de partida e
  consulte as tabelas oficiais da sua marca antes de confeccionar ou
  comprar.
* **Privacidade:** Nenhum dado é armazenado ou enviado para servidores —
  todas as informações permanecem apenas na sua sessão do navegador.

## Contribuições

Sinta‑se à vontade para abrir issues ou pull requests com sugestões de
melhoria.  Este projeto foi criado como demonstração educacional e pode
servir de base para customizações específicas.
