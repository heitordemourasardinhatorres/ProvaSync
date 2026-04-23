import json
import html
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator
from src.exceptions import JSONInvalidoError

class QuestaoInput(BaseModel):
    """
    Molde rigoroso do Pydantic para validar a entrada de dados.
    Ele converte os tipos, limita tamanhos e barra chaves inexistentes.
    """
    numero_do_ex: int = Field(alias="numero do ex")
    materia: str = Field(default="", max_length=500)
    submateria: str = Field(default="", max_length=500)
    questoes: Optional[Dict[str, str]] = None

    @field_validator("materia", "submateria")
    @classmethod
    def sanitize_html(cls, v: str) -> str:
        # Neutraliza ataques XSS removendo scripts indesejados automaticamente
        return html.escape(str(v))

    @field_validator("questoes")
    @classmethod
    def sanitize_subitens(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if v:
            return {k: html.escape(str(val).strip()[:500]) for k, val in v.items()}
        return v

def parse_json_questoes(conteudo_json: str, tipo_prova: str) -> List[dict]:
    """
    Recebe o conteúdo de um arquivo JSON e valida rigorosamente usando Pydantic
    antes de convertê-lo em lista para o Google Forms.
    """
    try:
        dados = json.loads(conteudo_json)
    except json.JSONDecodeError:
        raise JSONInvalidoError("O arquivo JSON está com formato inválido. Verifique a estrutura e tente novamente.")

    if not dados:
        raise JSONInvalidoError("O arquivo JSON não contém questões.")
        
    if not isinstance(dados, list):
        raise JSONInvalidoError("O arquivo JSON está com formato inválido. A raiz deve ser uma lista de questões.")

    questoes_formatadas = []
    tipo_prova_upper = tipo_prova.upper()

    for idx, item in enumerate(dados):
        try:
            # Pydantic faz a mágica da validação aqui
            questao_valida = QuestaoInput(**item)
        except ValidationError as e:
            # Simplifica o erro do Pydantic para a nossa interface final
            erros = e.errors()
            campo = erros[0].get("loc")[0] if erros[0].get("loc") else "desconhecido"
            raise JSONInvalidoError(f"Erro de validação no item {idx + 1} (Campo '{campo}'): {erros[0].get('msg')}")

        if tipo_prova_upper == "OBJETIVA":
            questoes_formatadas.append({
                "id": str(questao_valida.numero_do_ex),
                "materia": questao_valida.materia,
                "submateria": questao_valida.submateria
            })
            
        elif tipo_prova_upper == "DISCURSIVA":
            if not questao_valida.questoes:
                raise JSONInvalidoError(f"Questão {questao_valida.numero_do_ex} está sem subitens. Verifique o JSON.")
                
            for chave, valor_subitem in questao_valida.questoes.items():
                chave_min = str(chave).lower()
                id_subitem = f"{questao_valida.numero_do_ex}{chave_min}"
                
                questoes_formatadas.append({
                    "id": id_subitem,
                    "materia": questao_valida.materia,
                    "submateria": valor_subitem
                })

    return questoes_formatadas
