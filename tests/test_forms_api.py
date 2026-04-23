import pytest
from unittest.mock import patch, MagicMock
from src.forms_api import criar_form_google
from src.exceptions import LimiteExcedidoError

def test_limite_de_150_questoes_bloqueia_abuso():
    # Testa a trava de segurança (DDoS prevention) contra excesso de carga na API do Google
    questoes_gigantes = [{"id": str(i), "materia": "Física"} for i in range(151)]
    
    with pytest.raises(LimiteExcedidoError, match="excede o limite de 150 questões"):
        criar_form_google("Prova Gigante", questoes_gigantes, "Objetiva")

@patch("src.forms_api.get_credentials")
@patch("src.forms_api.build")
def test_criacao_form_sucesso(mock_build, mock_get_credentials):
    """
    Testa se o empacotamento (o Payload) pro Google é gerado corretamente.
    Usamos o @patch para 'MOCKAR' (Simular) a resposta do Google, garantindo 
    que o teste não ative a internet nem crie formulários fantasmas no seu Drive!
    """
    # 1. Configurando a mentira (Mock) do retorno do Google
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    # Simulando a resposta do Forms().create().execute()
    mock_service.forms().create().execute.return_value = {
        "formId": "form_falso_xyz",
        "responderUri": "https://forms.gle/fake"
    }
    
    # 2. Executando o nosso código
    questoes = [{"id": "1", "materia": "História", "submateria": "Guerra Fria"}]
    form_id, form_link = criar_form_google("Prova Teste", questoes, "Objetiva")
    
    # 3. Validando os resultados
    assert form_id == "form_falso_xyz"
    assert form_link == "https://forms.gle/fake"
    
    # Garante que o método batchUpdate foi chamado para inserir a questão de Checkbox
    mock_service.forms().batchUpdate.assert_called_once()
