from django import forms
from django.contrib.auth.models import User
from .models import ShoppingList, ShoppingItem, ShoppingShare, Product


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['name', 'budget']
        labels = {
            'name': 'Nome da lista', 
            'budget': 'Orçamento (R$)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Material Escolar 2026'}),
            'budget': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0,00', 'step': '0.01'}),
        }


class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        fields = ['product', 'name', 'quantity', 'price', 'category']
        labels = {
            'product': 'Produto do Catálogo',
            'name': 'Nome (se não houver no catálogo)',
            'quantity': 'Quantidade',
            'price': 'Preço (Manual)',
            'category': 'Categoria',
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Lápis HB'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'category': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Escrita'}),
        }


class ShareListForm(forms.Form):
    username = forms.CharField(
        label='Usuário',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome de usuário'}),
    )
    can_edit = forms.BooleanField(
        label='Permitir edição',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('Usuário não encontrado.')


class BudgetListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['budget']
        labels = {'budget': 'Orçamento da lista (R$)'}
        widgets = {
            'budget': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
        }


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Senha'}),
    )
    password2 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Repita a senha'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {'username': 'Nome de usuário', 'email': 'E-mail'}
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Seu username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'seu@email.com'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não coincidem.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
