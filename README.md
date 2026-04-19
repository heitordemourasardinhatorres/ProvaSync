# ProvaSync (JSON Mode)

ProvaSync é um sistema web construído em **Python 3.10+** (utilizando **Streamlit**) capaz de ler provas descritas estritamente em **arquivos JSON estruturados** para gerar de forma síncrona um formulário na sua conta do Google Drive com as descrições da prova, sendo ótimo para estudantes indicarem dúvidas em matérias ou exercícios específicos.

## Instalação e Execução

### 1. Clonando ou baixando esse sistema
Navegue via terminal para este diretório raiz. O banco de dados histórico é salvo puramente em formato arquivo local ignorado no git (`historico.json`).

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
4. Crie uma Credencial OAuth 2.0 Client ID (tipo "Desktop" ou "Web" com redirect http://localhost). 
5. Faça o download dessa JSON key cruzada.
6. Substitua o `credentials.example.json` por nome de arquivo contendo a sua verídica chaves transferidas e certifique-se dela relocar na raiz para que o python e o fluxo logue corretamente com porta zero.

### 5. Executando
Para inicializar de vez pelo browser porta 8501:
```bash
streamlit run app.py
```
Faça uploads das provas nos padrões pré-estabelecidos e sincronize!
