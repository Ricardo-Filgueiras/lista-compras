import os
import django
import random
from decimal import Decimal

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from shopping.models import ShoppingList, ShoppingItem

# --- CONFIGURAÇÃO ---
# Pode ser o ID (ex: 1) ou o Username (ex: 'userdev')
TARGET_USER = 'userdev'  
# ---------------------

def get_user(target):
    """Busca o usuário por ID (se for número) ou Username (se for texto)."""
    try:
        # Tenta converter para int, se conseguir, busca por ID
        if isinstance(target, int) or (isinstance(target, str) and target.isdigit()):
            return User.objects.get(pk=int(target))
        # Caso contrário, busca por username
        return User.objects.get(username=target)
    except User.DoesNotExist:
        return None

PRODUTOS_EXEMPLO = [
    ("Lápis Preto HB", "Escrita", 1.50),
    ("Caneta Esferográfica Azul", "Escrita", 2.00),
    ("Borracha Branca", "Escrita", 0.80),
    ("Apontador com Depósito", "Escrita", 3.50),
    ("Caderno Universitário 10 Matérias", "Papéis", 25.90),
    ("Bloco de Notas Adesivas", "Papéis", 5.00),
    ("Régua 30cm", "Medição", 2.50),
    ("Tesoura Escolar", "Artes", 4.90),
    ("Cola Branca 90g", "Artes", 3.20),
    ("Estojo de Feltro", "Organização", 12.00),
    ("Pasta Transparente", "Organização", 3.00),
    ("Marca Texto Amarelo", "Escrita", 4.50),
    ("Caixa de Lápis de Cor 12 cores", "Artes", 15.00),
    ("Giz de Cera 6 cores", "Artes", 2.50),
    ("Papel Sulfite A4 100 fls", "Papéis", 18.00),
    ("Grampeador Pequeno", "Escritório", 15.00),
    ("Clips de Papel (caixa)", "Escritório", 4.00),
    ("Corretivo em Fita", "Escrita", 8.50),
    ("Calculadora Científica", "Eletrônicos", 45.00),
    ("Compasso de Metal", "Desenho", 12.50),
    ("Mochila Escolar", "Transporte", 120.00),
    ("Lancheira Térmica", "Transporte", 45.00),
    ("Agenda 2026", "Papéis", 30.00),
    ("Dicionário de Português", "Livros", 22.00),
    ("Esquadro 45 graus", "Desenho", 4.00),
    ("Transferidor 180 graus", "Desenho", 3.50),
    ("Tinta Guache 6 cores", "Artes", 6.00),
    ("Pincel nº 8", "Artes", 2.80),
    ("Cartolina Branca", "Papéis", 1.20),
    ("Papel Celofane", "Artes", 0.90),
]

def create_items(shopping_list_obj, quantity):
    """Cria uma quantidade X de itens aleatórios para uma lista."""
    for i in range(quantity):
        # Escolhe um produto aleatório da lista de exemplos ou gera um genérico se acabar
        if i < len(PRODUTOS_EXEMPLO):
            p_name, p_cat, p_price = PRODUTOS_EXEMPLO[i % len(PRODUTOS_EXEMPLO)]
        else:
            p_name, p_cat, p_price = f"Item Extra {i+1}", "Diversos", random.uniform(1.0, 50.0)
            
        ShoppingItem.objects.create(
            shopping_list=shopping_list_obj, # CORRIGIDO: O nome do campo no modelo é 'shopping_list'
            name=p_name,
            quantity=random.randint(1, 5),
            price=Decimal(str(round(p_price, 2))),
            category=p_cat
        )

def run():
    user = get_user(TARGET_USER)
    
    if not user:
        print(f"❌ Erro: Usuário '{TARGET_USER}' não encontrado no banco de dados.")
        return

    print(f"--- Iniciando população para o usuário: {user.username} (ID: {user.id}) ---")

    # 1. Lista Pequena (10 itens)
    list_small = ShoppingList.objects.create(
        user=user,
        name="Lista Pequena (Escritório Rápido)",
        budget=100.00
    )
    create_items(list_small, 10)
    print(f"✔ Lista Pequena criada com 10 itens.")

    # 2. Lista Média (30 itens)
    list_medium = ShoppingList.objects.create(
        user=user,
        name="Lista Média (Material 1º Semestre)",
        budget=350.00
    )
    create_items(list_medium, 30)
    print(f"✔ Lista Média criada com 30 itens.")

    # 3. Lista Grande (50 itens)
    list_large = ShoppingList.objects.create(
        user=user,
        name="Lista Grande (Completa Ano Letivo)",
        budget=800.00
    )
    create_items(list_large, 50)
    print(f"✔ Lista Grande criada com 50 itens.")

    print("\n--- Processo concluído com sucesso! ---")

if __name__ == "__main__":
    run()
