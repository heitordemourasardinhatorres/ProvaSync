import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from src.exceptions import LimiteExcedidoError

# Escopos do Google Forms e Drive requeridos para editar formulários.
SCOPES = [
    'https://www.googleapis.com/auth/forms.body', 
    'https://www.googleapis.com/auth/drive'
]

# Paths hardcoded garantindo proteção contra path traversal em imports ou execução de outro diretório
# BASE_DIR sobe um nível pois forms_api está agora dentro de src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')

def get_credentials():
    """
    Obtém, atualiza ou cria novas credenciais OAuth2 do Google para os escopos definidos.
    Salva localmente no token.json para evitar re-autenticação.
    """
    creds = None
    # Verifica o armazenamento de sessão local seguro
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
    # Se não há credenciais válidas e ativas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"O arquivo {CREDENTIALS_PATH} não foi encontrado. "
                    "Renomeie o 'credentials.example.json' fornecido, inclua as chaves do Google Cloud Console e tente de novo."
                )
            
            # Abre uma porta dinâmica no localhost para receber a autorização do Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(TOKEN_PATH, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
            
    return creds

def criar_form_google(titulo, questoes, tipo):
    """
    Cria o Google Forms contendo um checkbox múltiplo com as questões identificadas.
    
    Args:
        titulo (str): Título do documento Google Forms.
        questoes (list[dict]): Lista de dicionários das questões, com id e resumo.
        tipo (str): 'Objetiva' ou 'Discursiva'.
    
    Returns:
        tuple[str, str]: form_id e responder_uri(link do form)
    """
    if len(questoes) > 150:
        raise LimiteExcedidoError("Falha de Segurança: O sistema bloqueou o envio pois excede o limite de 150 questões simultâneas, prevenindo abuso da API do Google.")

    creds = get_credentials()
    forms_service = build('forms', 'v1', credentials=creds)

    # Cria formulário vazio básico
    form_base = {
        "info": {
            "title": titulo,
            "documentTitle": titulo
        }
    }
    
    resultado_base = forms_service.forms().create(body=form_base).execute()
    form_id = resultado_base["formId"]
    responder_uri = resultado_base["responderUri"]

    # Prepara as opções de resposta baseada nas questões mapeadas
    options = []
    for q in questoes:
        prefixo = f"Questão {q['id']}"
        materia_texto = f" ({q.get('materia')})" if q.get('materia') else ""
        label = f"{prefixo}{materia_texto} — {q.get('submateria', '')}"
        options.append({"value": label})

    # Objeto de Update para adicionar a Descrição e a Pergunta de Checkbox
    update_request = {
        "requests": [
            {
                "updateFormInfo": {
                    "info": {
                        "description": "Marque as questões em que você teve dúvida."
                    },
                    "updateMask": "description"
                }
            },
            {
                "createItem": {
                    "item": {
                        "title": "Questões com Dúvida",
                        "questionItem": {
                            "question": {
                                "choiceQuestion": {
                                    "type": "CHECKBOX",
                                    "options": options
                                }
                            }
                        }
                    },
                    "location": {
                        "index": 0
                    }
                }
            }
        ]
    }
    
    # Atualiza em Lote
    forms_service.forms().batchUpdate(formId=form_id, body=update_request).execute()
    
    return form_id, responder_uri
