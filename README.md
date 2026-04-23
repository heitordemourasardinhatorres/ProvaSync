# ProvaSync (JSON Mode)

O **ProvaSync** é um sistema web autônomo focado em eficiência acadêmica. Ele é capaz de ler o escopo de provas processadas através de **arquivos JSON estruturados** para gerar, de forma instantânea e síncrona, um formulário responsivo na sua conta do Google Drive com todas as descrições da avaliação. É uma ferramenta ideal para professores e turmas de estudantes indicarem dúvidas em matérias, módulos ou exercícios específicos.

> **Desenvolvido por Heitor** | 🚀 [Acesse meu Portfólio: heitor-dev.vercel.app](https://heitor-dev.vercel.app)

---

## 🛠 Tech Stack

- **Linguagem Principal:** Python 3.10+
- **Frontend / UI:** Streamlit
- **Integração:** Google Forms API & Google Drive API
- **Autenticação:** Google OAuth 2.0 (Local Storage Token)

---

## ⚙️ Pré-requisitos

Antes de iniciar, certifique-se de que sua máquina possui:
- Python 3.10 ou superior instalado no `PATH`.
- Acesso à internet para bater na API do Google.
- Uma conta ativa no [Google Cloud Console](https://console.cloud.google.com/) com privilégios para gerar chaves OAuth.

---

## 🚀 Getting Started (Setup Local)

Siga este guia detalhado para rodar a aplicação em menos de 5 minutos na sua máquina:

### 1. Clonando o Repositório
Abra o seu terminal de preferência e navegue até a raiz deste projeto baixado/clonado.

> **⚠️ Atenção sobre o Histórico (Trabalho em Grupo):** O banco de dados de provas criadas (`data/historico.json`) é salvo de forma estritamente **local** na sua máquina e invisível ao versionamento. A sincronização local é individual!

### 2. Criação do Ambiente Virtual (Recomendado)
Para isolar as dependências e não poluir o seu sistema, crie um ambiente:

No Windows:
```bash
# Se o Python estiver no seu PATH:
python -m venv venv

# Ative o ambiente:
venv\Scripts\activate
```

### 3. Instalação das Dependências
Com o ambiente ativado `(venv)`, instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 4. Configuração das Credenciais do Google (OAuth)
Para que o código consiga manipular o seu Google Drive:
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie ou selecione um Projeto existente.
3. Vá em "APIs e Serviços" > "Biblioteca" e **Ative** a `Google Forms API` e a `Google Drive API`.
4. Vá em "Tela de consentimento OAuth" e adicione seu e-mail aos "Usuários de teste".
5. Vá em "Credenciais" > "Criar Credenciais" > **"ID do Cliente OAuth"**.
6. ⚠️ Escolha o tipo de aplicativo: **App para Computador (Desktop)**.
7. Faça o download do arquivo JSON recém gerado.
8. Renomeie esse arquivo exatamente para `credentials.json` e coloque-o na **raiz** do projeto (ao lado do `app.py`). 

### 5. Executando a Aplicação
Com a chave validada, inicialize a interface web do Streamlit:
```bash
streamlit run app.py
```
O sistema abrirá nativamente no seu navegador principal rodando em `localhost:8501`. Em seu primeiro envio, uma aba do Google solicitará seu login para autorizar a criação dos forms.

---

## 🏗 Architecture Overview

O ProvaSync foi reestruturado seguindo princípios profissionais de arquitetura de projeto Python para separar Lógica de Tela de Regras de Negócio.

### Directory Structure
```text
ProvaSync/
├── app.py                 # Ponto de Entrada (Frontend Streamlit)
├── credentials.json       # Sua chave (não enviada ao Git)
├── token.json             # Sessão do Google autogerada (não enviada ao Git)
├── requirements.txt       # Manifesto de bibliotecas Python
├── README.md              # Documentação principal
│
├── src/                   # Core Business Logic (Cérebro do App)
│   ├── extractor.py       # (Parser) Lógica de sanitização e montagem do JSON
│   ├── forms_api.py       # (Service) Lógica de Comunicação OAuth com o Google
│   └── historico.py       # (Controller) Gerencia de Leitura e Escrita de Logs
│
└── data/                  # Banco de Dados Local
    └── historico.json     # Tabela silenciosa dos forms gerados
```

### Request Lifecycle
1. O usuário faz o upload de um `.json` no Frontend (`app.py`).
2. O sistema verifica os bloqueios e limites de memória.
3. A Payload segue para o `src/extractor.py`, onde as tags HTML são sanitizadas, limitadas a 500 caracteres, e tipadas.
4. O Frontend exibe uma tabela interativa para aprovação humana final.
5. Ao aprovar, o `src/forms_api.py` resgata o `credentials.json`, abre uma porta local e manda o batch para a nuvem.
6. A resposta contendo o link final é devolvida e injetada na tela e também no `src/historico.py` para armazenamento.

---

## 🔐 Environment & Autenticação

Este sistema lida com Tokens e Credenciais que dão poder de edição no seu Google Drive.
- **NUNCA** suba os arquivos `credentials.json` ou `token.json` para repositórios públicos do Github. 
- O arquivo `.gitignore` do projeto já está configurado para barrá-los, porém preste atenção extra caso mova pastas manualmente.
- Se você quiser revogar o acesso do ProvaSync à sua conta Google, simplesmente delete o arquivo `token.json` gerado na raiz e vá ao painel de Permissões da sua Conta Google.

---

## 🚑 Troubleshooting (Soluções de Problemas)

### Erro: `redirect_uri_mismatch` ou `access_denied` no Google
**Sintoma:** Ao tentar criar o primeiro formulário, uma página do Google abre com um texto vermelho dizendo que a URI não confere ou o App não está autorizado.
**Solução:** 
1. Verifique se no Google Cloud você gerou a credencial como **App para Computador**. Se você gerou como "App da Web", a porta dinâmica zero utilizada pelo código falhará em rotear de volta.
2. Certifique-se de que o seu e-mail foi incluído como "Usuário de Teste" na tela de consentimento do Google Cloud.

### Erro: `FileNotFoundError: O arquivo .../credentials.json não foi encontrado`
**Sintoma:** O console avisa que não achou a chave de acesso.
**Solução:** O arquivo baixado do Google geralmente possui um nome gigante (ex: `client_secret_xyz.json`). Você deve renomeá-lo explicitamente para `credentials.json` e jogá-lo exatamente na raiz do projeto (mesmo nível do `app.py`), pois a camada lógica irá subir o nível da pasta para procurá-lo lá.

### Erro: A interface do Streamlit diz "O payload excede 2MB" ou "Limite de 150 questões"
**Sintoma:** Bloqueio de submissão do formulário.
**Solução:** Isso faz parte do escudo de segurança **DDoS/Memory Exhaustion** implementado no código-fonte. Divida o seu JSON de questões em dois ou três arquivos menores, ou altere o código em `app.py` sob seu próprio risco de estourar a memória.
