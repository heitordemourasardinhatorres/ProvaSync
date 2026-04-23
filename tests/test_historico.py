import pytest
import os
import json
from src import historico

@pytest.fixture
def isolar_banco_de_dados(tmp_path, monkeypatch):
    """
    Fixture mágica do Pytest. Ela cria uma pasta temporária falsa (tmp_path) 
    e força o historico.py a usar ela em vez da sua pasta data/ real.
    Isso impede que os testes sujem o seu histórico de verdade!
    """
    db_falso_dir = tmp_path / "data"
    db_falso_file = db_falso_dir / "historico.json"
    
    # Sequestra as variáveis do arquivo original e substitui pelas falsas
    monkeypatch.setattr(historico, "DATA_DIR", str(db_falso_dir))
    monkeypatch.setattr(historico, "HISTORICO_FILE", str(db_falso_file))
    
    return db_falso_file

def test_carregar_historico_vazio(isolar_banco_de_dados):
    # Testa se o sistema reage bem quando um aluno roda o app pela primeira vez (sem arquivo json gerado ainda)
    dados = historico.carregar_historico()
    assert isinstance(dados, list)
    assert len(dados) == 0

def test_salvar_e_carregar_historico_sucesso(isolar_banco_de_dados):
    # Testa salvar um log fictício
    historico.salvar_historico(
        nome="Prova de Física",
        tipo="Objetiva",
        num_questoes=40,
        form_link="https://forms.gle/teste123",
        form_id="id_12345"
    )
    
    # Testa carregar e valida se gravou com perfeição
    dados = historico.carregar_historico()
    
    assert len(dados) == 1
    assert dados[0]["nome"] == "Prova de Física"
    assert dados[0]["tipo"] == "Objetiva"
    assert dados[0]["questoes_detectadas"] == 40
    assert "criado_em" in dados[0]
