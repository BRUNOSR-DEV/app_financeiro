import bcrypt

class SegurancaService:
    
    @staticmethod
    def criptografar_senha(senha_limpa: str) -> str:
        """Transforma a senha em um hash seguro (bytes) e decodifica para string antes de salvar no banco."""
        # O bcrypt precisa de bytes, então convertemos a string
        senha_bytes = senha_limpa.encode('utf-8')
        # Gera o salt e o hash
        hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt(rounds=12))
        # Retorna como string para salvar fácil no VARCHAR do banco
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
            # Se o hash no banco não for um bcrypt válido, falha de forma segura
            return False