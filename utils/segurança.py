"""
Módulo de Serviços de Segurança

Abstrai as operações de criptografia de alto nível utilizando o algoritmo bcrypt.
Garante o isolamento e proteção de credenciais antes da persistência em banco de dados.
"""

import bcrypt

class SegurancaService:
    
    @staticmethod
    def criptografar_senha(senha_limpa: str) -> str:
        """Transforma a senha em um hash seguro (bytes) e decodifica para string antes de salvar no banco."""
        senha_bytes = senha_limpa.encode('utf-8')
        hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt(rounds=12))
        return hash_bytes.decode('utf-8')

    @staticmethod
    def verificar_senha(senha_digitada: str, hash_do_banco: str) -> bool:
        """Verifica se a senha digitada bate com o hash salvo."""
        try:
            return bcrypt.checkpw(
                senha_digitada.encode('utf-8'),
                hash_do_banco.encode('utf-8')
            )
        except Exception:
            return False