import io
import qrcode
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

    total_all = pending + bought
    total_pix = total_all * DecimalField(max_digits=10, decimal_places=2).to_python(0.9)
    budget = shopping_list.budget or 0
    balance = budget - total_all

    return {
        'total_pending': pending,
        'total_bought': bought,
        'total_all': total_all,
        'total_pix': total_pix,
        'budget': budget,
        'balance': balance,
    }


# ────────────────────────── list views ───────────────────────────


def home(request):
    """Página de destino (Landing Page) para usuários não logados."""
    if request.user.is_authenticated:
        return redirect('shopping:index')
    return render(request, 'shopping/home.html')


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
    """Edita nome/orçamento/status da lista. Apenas o dono ou convidado com permissão."""
    shopping_list, is_owner, share = _get_list_or_403(uuid, request.user)
    can_edit = is_owner or (share and share.can_edit)
    
    if not can_edit:
        messages.error(request, 'Sem permissão.')
        return redirect('shopping:index')

    if request.method == 'POST' and 'is_locked' in request.POST:
        shopping_list.is_locked = request.POST.get('is_locked') == 'True'
        shopping_list.save(update_fields=['is_locked'])
        messages.success(request, 'Status da lista atualizado!')
        return redirect('shopping:list_detail', uuid=shopping_list.uuid)

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
    
    if shopping_list.is_locked:
        messages.error(request, 'Lista travada para edição.')
        return redirect('shopping:list_detail', uuid=list_uuid)

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
    """Edita um item. Dono ou convidado com can_edit. Suporta HTMX +/-."""
    shopping_list, is_owner, share = _get_list_or_403(list_uuid, request.user)
    can_edit = is_owner or (share and share.can_edit)
    
    if shopping_list.is_locked:
        return HttpResponse('Lista travada', status=403)

    if not can_edit:
        return HttpResponse('Sem permissão', status=403)

    item = get_object_or_404(ShoppingItem, uuid=item_uuid, shopping_list=shopping_list)
    
    # Lógica HTMX para botões de quantidade
    action = request.GET.get('action')
    if request.method == 'POST' and action in ['inc', 'dec']:
        if action == 'inc':
            item.quantity_value += 1
        elif action == 'dec' and item.quantity_value > 1:
            item.quantity_value -= 1
        item.save(update_fields=['quantity_value'])
        
        # Retorna apenas o card atualizado (ou sinaliza refresh se necessário para o total)
        # Para atualizar o footer via HTMX, poderíamos usar HX-Trigger, mas vamos simplificar por hora
        response = render(request, 'shopping/partials/item_row.html', {
            'item': item, 'list': shopping_list, 'can_edit': can_edit
        })
        response['HX-Trigger'] = 'update-totals'
        return response

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
    
    if shopping_list.is_locked:
        return HttpResponse('Lista travada', status=403)

    if not can_edit:
        return HttpResponse('Sem permissão', status=403)

    item = get_object_or_404(ShoppingItem, uuid=item_uuid, shopping_list=shopping_list)
    
    if request.method == 'POST' or request.method == 'DELETE':
        item.delete()
        if request.headers.get('HX-Request'):
            response = HttpResponse('')
            response['HX-Trigger'] = 'update-totals'
            return response
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
def list_totals(request, uuid):
    """Retorna apenas o resumo financeiro para atualização via HTMX."""
    shopping_list, is_owner, share = _get_list_or_403(uuid, request.user)
    totals = _calc_totals(shopping_list)
    return render(request, 'shopping/partials/footer_summary.html', {
        'list': shopping_list,
        **totals,
    })


@login_required
def list_join(request, uuid):
    """Permite que um usuário entre na lista como editor via link direto."""
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid)
    
    # Se não for o dono, cria o compartilhamento automaticamente
    if shopping_list.user != request.user:
        ShoppingShare.objects.get_or_create(
            shopping_list=shopping_list,
            shared_with=request.user,
            defaults={'shared_by': shopping_list.user, 'can_edit': True}
        )
        messages.success(request, f'Você agora é um editor da lista: {shopping_list.name}')
    
    return redirect('shopping:list_detail', uuid=uuid)


@login_required
def list_clone(request, uuid):
    """Exibe confirmação e cria uma cópia privada (template) de uma lista existente."""
    original_list = get_object_or_404(ShoppingList, uuid=uuid)
    
    if request.method == 'POST':
        # Cria a nova lista
        new_list = ShoppingList.objects.create(
            user=request.user,
            name=f"{original_list.name} (Cópia)",
            budget=original_list.budget
        )
        
        # Copia todos os itens da lista original
        items = original_list.items.all()
        new_items = []
        for item in items:
            new_items.append(ShoppingItem(
                shopping_list=new_list,
                name=item.name,
                quantity_value=item.quantity_value,
                unit=item.unit,
                price=item.price,
                category=item.category,
                is_purchased=False
            ))
        
        ShoppingItem.objects.bulk_create(new_items)
        
        messages.success(request, f'Lista "{new_list.name}" criada com sucesso!')
        return redirect('shopping:list_detail', uuid=new_list.uuid)

    return render(request, 'shopping/list_clone_confirm.html', {'list': original_list})


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


@login_required
def list_qrcode(request, uuid):
    """Gera um QR Code dinâmico para a lista (join ou clone)."""
    # Verifica permissão (apenas quem tem acesso à lista pode gerar o QR)
    shopping_list, is_owner, share = _get_list_or_403(uuid, request.user)
    
    qr_type = request.GET.get('type', 'clone')
    
    # Define a URL baseada no tipo
    from django.urls import reverse
    if qr_type == 'join':
        url_path = reverse('shopping:list_join', args=[uuid])
    else:
        url_path = reverse('shopping:list_clone', args=[uuid])
        
    full_url = f"{request.scheme}://{request.get_host()}{url_path}"
    
    # Gera o QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Salva em buffer de memória
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return HttpResponse(buf.getvalue(), content_type="image/png")
