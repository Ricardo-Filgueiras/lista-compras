from django.contrib import admin
from .models import (
    ShoppingList, 
    ShoppingItem, 
    ShoppingShare, 
    MonthlyShoppingBudget,
    Product
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock', 'barcode')
    search_fields = ('name', 'barcode', 'category')
    list_filter = ('category',)

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'status', 'is_template', 'is_locked', 'created_at')
    list_filter = ('status', 'is_template', 'is_locked', 'created_at')
    search_fields = ('name', 'user__username', 'school', 'student_name')
    readonly_fields = ('uuid',)

@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ('get_item_name', 'shopping_list', 'quantity', 'get_item_price', 'is_purchased')
    list_filter = ('is_purchased', 'shopping_list')
    search_fields = ('name', 'product__name', 'shopping_list__name')
    readonly_fields = ('uuid',)

    def get_item_name(self, obj):
        return obj.get_item_name()
    get_item_name.short_description = 'Produto'

    def get_item_price(self, obj):
        return obj.get_item_price()
    get_item_price.short_description = 'Preço Unitário'

@admin.register(ShoppingShare)
class ShoppingShareAdmin(admin.ModelAdmin):
    list_display = ('shopping_list', 'shared_with', 'shared_by', 'can_edit', 'created_at')
    list_filter = ('can_edit', 'created_at')

@admin.register(MonthlyShoppingBudget)
class MonthlyShoppingBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'period', 'amount')
    list_filter = ('period',)
