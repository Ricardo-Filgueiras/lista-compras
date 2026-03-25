import secrets
import string

def gerar_secret_key(size=8):
    """
    Gera uma chave de segurança aleatória com o tamanho especificado.
    
    :param size: O tamanho da chave de segurança (default é 32)
    :type size: int
    :return: Uma chave de segurança aleatória
    :rtype: str
    """
    letters_and_digits = string.ascii_letters + string.digits
    secret_key = ''.join(secrets.choice(letters_and_digits) for _ in range(size))
    return secret_key

# Exemplo de uso:
secret_key = gerar_secret_key()
print(secret_key)
