import json
import html

def parse_json_questoes(conteudo_json, tipo_prova):
    """
    Recebe o conteúdo string/bytes de um arquivo JSON estruturado e o converte 
    em uma lista de questões prontas para alimentar a tabela e ir pro Forms.
    """
    try:
        dados = json.loads(conteudo_json)
    except json.JSONDecodeError:
        raise ValueError("O arquivo JSON está com formato inválido. Verifique a estrutura e tente novamente.")

    if not dados:
        raise ValueError("O arquivo JSON não contém questões.")
        
    if not isinstance(dados, list):
        raise ValueError("O arquivo JSON está com formato inválido. A raiz deve ser uma lista de questões.")

    questoes_formatadas = []

    # Trataremos as labels 'Objetiva'/'Discursiva' ignorando maiúscula/minúscula se precisar.
    tipo_prova_upper = tipo_prova.upper()

    for idx, item in enumerate(dados):
        numero = item.get("numero do ex")
        if numero is None:
            raise ValueError(f"Campo 'numero do ex' ausente no item {idx + 1}.")

        materia_raw = str(item.get("materia", ""))[:500]
        materia = html.escape(materia_raw)
        
        submateria_raw = str(item.get("submateria", ""))[:500]
        submateria_base = html.escape(submateria_raw)

        if tipo_prova_upper == "OBJETIVA":
            questoes_formatadas.append({
                "id": str(numero),
                "materia": materia,
                "submateria": submateria_base
            })
            
        elif tipo_prova_upper == "DISCURSIVA":
            if "questoes" not in item:
                raise ValueError(f"Questão {numero} está sem subitens. Verifique o JSON.")
                
            subitens = item.get("questoes")
            if not isinstance(subitens, dict) or not subitens:
                raise ValueError(f"A propriedade 'questoes' da questão {numero} não é um dicionário contendo subitens ou está vazia.")
            
            for chave, valor_subitem in subitens.items():
                chave_min = str(chave).lower()
                id_subitem = f"{numero}{chave_min}"
                
                submateria_raw = str(valor_subitem).strip()[:500]
                submateria_especifica = html.escape(submateria_raw)
                
                questoes_formatadas.append({
                    "id": id_subitem,
                    "materia": materia,
                    "submateria": submateria_especifica
                })

    return questoes_formatadas
