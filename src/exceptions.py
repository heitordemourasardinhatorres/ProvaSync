class ProvaSyncError(Exception):
    """Classe Base para todos os erros controlados do ProvaSync."""
    pass

class JSONInvalidoError(ProvaSyncError):
    """Disparada quando o JSON está com formato quebrado ou a validação do Pydantic falha."""
    pass

class LimiteExcedidoError(ProvaSyncError):
    """Disparada para prevenir DDoS ou estouro de cota nas requisições do Google."""
    pass

class GoogleAPIError(ProvaSyncError):
    """Disparada para problemas de permissão ou conexão com a API do Google Forms."""
    pass
