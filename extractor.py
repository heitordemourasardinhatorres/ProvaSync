import json

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
        enunciado = item.get("enunciado")
        
        if numero is None:
            raise ValueError(f"Campo 'numero do ex' ausente no item {idx + 1}.")
        if enunciado is None:
            raise ValueError(f"Campo 'enunciado' ausente na questão {numero}.")

        if tipo_prova_upper == "OBJETIVA":
            # Para objetivas, é obrigatório ter o campo "alternativas" mas elas não vão pro form individual de CHECKBOX (dúvidas)
            if "alternativas" not in item:
                raise ValueError(f"Questão {numero} está sem alternativas. Verifique o JSON.")
            
            # Pega até 2 linhas iniciais do enunciado
            enunciado_linhas = str(enunciado).strip().split('\n')
            resumo = " ".join(enunciado_linhas[:2])
            
            questoes_formatadas.append({
                "id": str(numero),
                "resumo": resumo
            })
            
        elif tipo_prova_upper == "DISCURSIVA":
            # Para discursivas, é obrigatório ter o campo "questoes" contendo as letras (subitens)
            if "questoes" not in item:
                raise ValueError(f"Questão {numero} está sem subitens. Verifique o JSON.")
                
            subitens = item.get("questoes")
            if not isinstance(subitens, dict) or not subitens:
                raise ValueError(f"A propriedade 'questoes' da questão {numero} não é um dicionário contendo subitens ou está vazia.")
            
            for chave, valor_subitem in subitens.items():
                chave_min = str(chave).lower()
                id_subitem = f"{numero}{chave_min}"
                
                # Pega até 2 linhas iniciais do valor do subitem (como indicado na especificação)
                subitem_linhas = str(valor_subitem).strip().split('\n')
                resumo = " ".join(subitem_linhas[:2])
                
                questoes_formatadas.append({
                    "id": id_subitem,
                    "resumo": resumo
                })

    return questoes_formatadas
