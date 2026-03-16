from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Sum, F, DecimalField, ExpressionWrapper

from .models import ShoppingList, ShoppingItem, ShoppingShare
from .forms import ShoppingListForm, ShoppingItemForm, ShareListForm, BudgetListForm


# ───────────────────────────── helpers ─────────────────────────────

def _get_list_or_403(uuid, user):
    """Recupera uma lista pelo UUID e verifica se o user tem acesso (dono ou convidado)."""
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid)
    is_owner = shopping_list.user == user
    share = ShoppingShare.objects.filter(shopping_list=shopping_list, shared_with=user).first()
    if not is_owner and share is None:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return shopping_list, is_owner, share


def _calc_totals(shopping_list):
    """Calcula totais financeiros da lista."""
    price_expr = ExpressionWrapper(
        F('quantity_value') * F('price'),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    pending = shopping_list.items.filter(is_purchased=False).aggregate(
        total=Sum(price_expr)
    )['total'] or 0

    bought = shopping_list.items.filter(is_purchased=True).aggregate(
        total=Sum(price_expr)
    )['total'] or 0

    budget = shopping_list.budget or 0
    balance = budget - (pending + bought)

    return {
        'total_pending': pending,
        'total_bought': bought,
        'total_all': pending + bought,
        'budget': budget,
        'balance': balance,
    }


# ────────────────────────── list views ───────────────────────────


@login_required
def index(request):
    """Página principal: exibe todas as listas do usuário (próprias + compartilhadas)."""
    own_lists = ShoppingList.objects.filter(user=request.user)
    shared_ids = ShoppingShare.objects.filter(shared_with=request.user).values_list('shopping_list_id', flat=True)
    shared_lists = ShoppingList.objects.filter(id__in=shared_ids)

    form = ShoppingListForm()
    if request.method == 'POST':
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            new_list = form.save(commit=False)
            new_list.user = request.user
            new_list.save()
            messages.success(request, 'Lista criada com sucesso!')
            return redirect('shopping:list_detail', uuid=new_list.uuid)

    return render(request, 'shopping/list_index.html', {
        'own_lists': own_lists,
        'shared_lists': shared_lists,
        'form': form,
    })


@login_required
def list_detail(request, uuid):
    """Detalha uma lista com itens, totais e formulário de item."""
    shopping_list, is_owner, share = _get_list_or_403(uuid, request.user)
    can_edit = is_owner or (share and share.can_edit)

    pending_items = shopping_list.items.filter(is_purchased=False)
    bought_items = shopping_list.items.filter(is_purchased=True)
    totals = _calc_totals(shopping_list)

    item_form = ShoppingItemForm() if can_edit else None

    return render(request, 'shopping/list_detail.html', {
        'list': shopping_list,
        'is_owner': is_owner,
        'can_edit': can_edit,
        'pending_items': pending_items,
        'bought_items': bought_items,
        'item_form': item_form,
        **totals,
    })


@login_required
def list_edit(request, uuid):
    """Edita nome/orçamento da lista. Apenas o dono."""
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    form = ShoppingListForm(request.POST or None, instance=shopping_list)
    if form.is_valid():
        form.save()
        messages.success(request, 'Lista atualizada!')
        return redirect('shopping:list_detail', uuid=shopping_list.uuid)
    return render(request, 'shopping/list_form.html', {'form': form, 'list': shopping_list, 'action': 'Editar'})


@login_required
def list_delete(request, uuid):
    """Exclui uma lista. Apenas o dono."""
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    if request.method == 'POST':
        shopping_list.delete()
        messages.success(request, 'Lista excluída.')
        return redirect('shopping:index')
    return render(request, 'shopping/list_confirm_delete.html', {'list': shopping_list})


# ───────────────────────── item views ──────────────────────────


@login_required
def item_add(request, list_uuid):
    """Adiciona item à lista. Dono ou convidado com can_edit."""
    shopping_list, is_owner, share = _get_list_or_403(list_uuid, request.user)
    can_edit = is_owner or (share and share.can_edit)
    if not can_edit:
        messages.error(request, 'Sem permissão para adicionar itens.')
        return redirect('shopping:list_detail', uuid=list_uuid)

    form = ShoppingItemForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.shopping_list = shopping_list
        item.save()
        messages.success(request, f'"{item.name}" adicionado!')
        return redirect('shopping:list_detail', uuid=shopping_list.uuid)

    return render(request, 'shopping/item_form.html', {
        'form': form, 'list': shopping_list, 'action': 'Adicionar',
    })


@login_required
def item_edit(request, list_uuid, item_uuid):
    """Edita um item. Dono ou convidado com can_edit."""
    shopping_list, is_owner, share = _get_list_or_403(list_uuid, request.user)
    can_edit = is_owner or (share and share.can_edit)
    if not can_edit:
        messages.error(request, 'Sem permissão para editar itens.')
        return redirect('shopping:list_detail', uuid=list_uuid)

    item = get_object_or_404(ShoppingItem, uuid=item_uuid, shopping_list=shopping_list)
    form = ShoppingItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, 'Item atualizado!')
        return redirect('shopping:list_detail', uuid=shopping_list.uuid)

    return render(request, 'shopping/item_form.html', {
        'form': form, 'list': shopping_list, 'item': item, 'action': 'Editar',
    })


@login_required
def item_delete(request, list_uuid, item_uuid):
    """Exclui um item. Dono ou convidado com can_edit."""
    shopping_list, is_owner, share = _get_list_or_403(list_uuid, request.user)
    can_edit = is_owner or (share and share.can_edit)
    if not can_edit:
        messages.error(request, 'Sem permissão para excluir itens.')
        return redirect('shopping:list_detail', uuid=list_uuid)

    item = get_object_or_404(ShoppingItem, uuid=item_uuid, shopping_list=shopping_list)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item removido.')
        return redirect('shopping:list_detail', uuid=shopping_list.uuid)

    return render(request, 'shopping/item_confirm_delete.html', {'item': item, 'list': shopping_list})


@login_required
def item_toggle(request, list_uuid, item_uuid):
    """Alterna status comprado/pendente via POST (HTMX ou formulário)."""
    shopping_list, is_owner, share = _get_list_or_403(list_uuid, request.user)
    item = get_object_or_404(ShoppingItem, uuid=item_uuid, shopping_list=shopping_list)
    item.is_purchased = not item.is_purchased
    item.save(update_fields=['is_purchased'])

    # Se for requisição HTMX, instrui o browser a recarregar a página completa
    if request.headers.get('HX-Request'):
        response = HttpResponse()
        response['HX-Refresh'] = 'true'
        return response

    return redirect('shopping:list_detail', uuid=shopping_list.uuid)


# ─────────────────────── share & budget ────────────────────────


@login_required
def list_share(request, uuid):
    """Compartilha a lista com outro usuário. Apenas o dono."""
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    form = ShareListForm(request.POST or None)
    shares = shopping_list.shares.select_related('shared_with')

    if form.is_valid():
        target_user = form.cleaned_data['username']
        can_edit = form.cleaned_data['can_edit']

        if target_user == request.user:
            messages.error(request, 'Você não pode compartilhar com você mesmo.')
        else:
            obj, created = ShoppingShare.objects.update_or_create(
                shopping_list=shopping_list,
                shared_with=target_user,
                defaults={'shared_by': request.user, 'can_edit': can_edit},
            )
            msg = 'Lista compartilhada!' if created else 'Permissões atualizadas.'
            messages.success(request, msg)
            return redirect('shopping:list_share', uuid=shopping_list.uuid)

    return render(request, 'shopping/list_share.html', {
        'list': shopping_list,
        'form': form,
        'shares': shares,
    })


@login_required
def share_remove(request, uuid, share_id):
    """Remove um compartilhamento. Apenas o dono."""
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    share = get_object_or_404(ShoppingShare, id=share_id, shopping_list=shopping_list)
    if request.method == 'POST':
        share.delete()
        messages.success(request, 'Acesso removido.')
    return redirect('shopping:list_share', uuid=shopping_list.uuid)


@login_required
def list_budget(request, uuid):
    """Define o orçamento de uma lista. Apenas o dono."""
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    form = BudgetListForm(request.POST or None, instance=shopping_list)
    if form.is_valid():
        form.save()
        messages.success(request, 'Orçamento definido!')
        return redirect('shopping:list_detail', uuid=shopping_list.uuid)
    return render(request, 'shopping/list_budget.html', {'form': form, 'list': shopping_list})
