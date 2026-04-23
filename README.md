# ProvaSync (JSON Mode)

ProvaSync é um sistema web construído em **Python 3.10+** (utilizando **Streamlit**) capaz de ler provas descritas estritamente em **arquivos JSON estruturados** para gerar de forma síncrona um formulário na sua conta do Google Drive com as descrições da prova, sendo ótimo para estudantes indicarem dúvidas em matérias ou exercícios específicos.

## Instalação e Execução

### 1. Clonando ou baixando esse sistema
Navegue via terminal para este diretório raiz. 

> **⚠️ Atenção sobre o Histórico (Trabalho em Grupo):** O banco de dados de provas criadas (`historico.json`) é salvo de forma estritamente **local** na sua máquina e invisível ao versionamento. Portanto, as provas que você sincroniza não aparecerão para os seus colegas caso eles rodem o app nos computadores deles (e vice-versa). A sincronização local é individual!

### 2. Ambientes Virtuais (RECOMENDADO)
No Windows, se for criar um ambiente local, utilize:
```bash
NOME_DO_CAMINHO_DO_PYTHON/python.exe -m venv venv
```
Onde "NOME_DO_CAMINHO_DO_PYTHON" é examente onde sua instalação .exe reside, caso o terminal aponte ausência de instalação no `PATH` padrão.

Ative (Windows):
```bash
venv\Scripts\activate
```

### 3. Instalando as dependências
Rode:
```bash
pip install -r requirements.txt
```

### 4. Configurando Credenciais Google
Para que o sistema ganhe poder de forçar novas abas e perguntas em seu drive:
1. Vá ao Google Cloud Console;
2. Crie ou use um projeto.
3. Ative a "Google Forms API" e a "Google Drive API".
4. Crie uma Credencial OAuth 2.0 do tipo **"App para Computador" (Desktop)**. *(Observação: Se for criar do tipo Web, certifique-se de configurar e travar portas nas configurações, pois o app buscará dinamicamente).*
5. Faça o download do arquivo JSON contendo as chaves geradas.
6. Renomeie o arquivo baixado exatamente para `credentials.json` e coloque-o na mesma pasta raiz do projeto, ao lado do arquivo `app.py`. Apenas isso bastará para o Python ler sua chave com segurança.

### 5. Executando
Para inicializar de vez pelo browser porta 8501:
```bash
streamlit run app.py
```
Faça uploads das provas nos padrões pré-estabelecidos e sincronize!
