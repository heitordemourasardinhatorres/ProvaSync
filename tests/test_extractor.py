import pytest
from src.extractor import parse_json_questoes
from src.exceptions import JSONInvalidoError
import json

def test_json_invalido_deve_falhar():
    # Testa se o extrator barra um arquivo mal formatado em string
    with pytest.raises(JSONInvalidoError, match="O arquivo JSON est.*formato inv.*lido"):
        parse_json_questoes("{ texto quebrado", "Objetiva")

def test_json_raiz_nao_eh_lista_deve_falhar():
    # Testa se o extrator impede que subam um objeto vazio ao invés de array
    json_invalido = json.dumps({"numero do ex": 1})
    with pytest.raises(JSONInvalidoError, match="A raiz deve ser uma lista de questões"):
        parse_json_questoes(json_invalido, "Objetiva")

def test_prova_objetiva_sucesso():
    # Testa o cenário de ouro onde um JSON de múltipla escolha entra e é processado com HTML sanitizado
    payload = [
        {
            "numero do ex": 1,
            "materia": "Química <script>alert(1)</script>",
            "submateria": "Tabela Periódica"
        }
    ]
    json_str = json.dumps(payload)
    resultado = parse_json_questoes(json_str, "Objetiva")
    
    assert len(resultado) == 1
    assert resultado[0]["id"] == "1"
    # A sanitização XSS HTML que botamos lá atrás deve remover os chevrons "<"
    assert resultado[0]["materia"] == "Química &lt;script&gt;alert(1)&lt;/script&gt;"
    assert resultado[0]["submateria"] == "Tabela Periódica"

def test_prova_discursiva_ausencia_de_subitens():
    # Testa se a segurança barra provas discursivas enviadas faltando os sub-itens
    payload = [
        {
            "numero do ex": 2,
            "materia": "Física",
            "submateria": "Cinemática"
        }
    ]
    json_str = json.dumps(payload)
    with pytest.raises(JSONInvalidoError, match="está sem subitens. Verifique o JSON"):
        parse_json_questoes(json_str, "Discursiva")

def test_prova_discursiva_sucesso():
    # Testa a derivação das letras "a", "b", "c" em provas discursivas
    payload = [
        {
            "numero do ex": 3,
            "materia": "Matemática",
            "submateria": "Geometria",
            "questoes": {
                "a": "Área do triângulo",
                "b": "Volume da Esfera"
            }
        }
    ]
    json_str = json.dumps(payload)
    resultado = parse_json_questoes(json_str, "Discursiva")
    
    # 1 root questão com 2 subitens deve virar 2 entradas no checkbox final
    assert len(resultado) == 2
    assert resultado[0]["id"] == "3a"
    assert resultado[0]["submateria"] == "Área do triângulo"
    assert resultado[1]["id"] == "3b"
    assert resultado[1]["submateria"] == "Volume da Esfera"
