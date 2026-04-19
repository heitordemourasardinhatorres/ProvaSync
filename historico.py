import json
import os
from datetime import datetime

HISTORICO_FILE = "historico.json"

def carregar_historico():
    """
    Carrega a lista de formulários previamente salvos no historico.json.
    Retorna uma lista de dicionários. Se o arquivo não existir ou for inválido, retorna lista vazia.
    """
    if not os.path.exists(HISTORICO_FILE):
        return []
    
    try:
        with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get("forms", [])
    except (json.JSONDecodeError, IOError) as e:
        print(f"Aviso: Não foi possível ler o histórico existente: {e}")
        return []

def salvar_historico(nome, tipo, num_questoes, form_link, form_id):
    """
    Adiciona um novo registro ao historico.json.
    
    Args:
        nome (str): Nome do PDF sem a extensão.
        tipo (str): 'objetiva' ou 'discursiva'.
        num_questoes (int): Número de questões detectadas/enviadas.
        form_link (str): URL para resposta do Google Form gerado.
        form_id (str): ID interno do Google Form.
    """
    forms = carregar_historico()
    
    novo_registro = {
        "nome": nome,
        "tipo": tipo,
        "questoes_detectadas": num_questoes,
        "form_link": form_link,
        "form_id": form_id,
        "criado_em": datetime.now().strftime("%Y-%m-%d")
    }
    
    forms.insert(0, novo_registro) # Adiciona no topo como mais recente
    
    try:
        with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
            json.dump({"forms": forms}, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Erro ao salvar no histórico: {e}")
        return False
