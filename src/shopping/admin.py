from django.contrib import admin
from .models import ShoppingList, ShoppingItem, ShoppingShare, MonthlyShoppingBudget


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'budget', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['user']


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'shopping_list', 'quantity_value', 'unit', 'price', 'is_purchased']
    search_fields = ['name', 'shopping_list__name']
    list_filter = ['is_purchased', 'unit']


@admin.register(ShoppingShare)
class ShoppingShareAdmin(admin.ModelAdmin):
    list_display = ['shopping_list', 'shared_with', 'shared_by', 'can_edit']


@admin.register(MonthlyShoppingBudget)
class MonthlyShoppingBudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'period', 'amount']
