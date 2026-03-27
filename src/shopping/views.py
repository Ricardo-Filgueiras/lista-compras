import io
import csv
import base64
import qrcode
from decimal import Decimal
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Sum, F

from .models import ShoppingList, ShoppingItem, ShoppingShare, Product
from .forms import ShoppingListForm, ShoppingItemForm, ShareListForm, BudgetListForm


# ───────────────────────────── helpers ─────────────────────────────

def _get_list_or_403(uuid, user):
    """Recupera uma lista pelo UUID e verifica se o user tem acesso (dono ou convidado)."""
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid)
    
    # Staff sempre tem acesso para fins de gestão
    if user.is_staff:
        return shopping_list, shopping_list.user == user, None
        
    is_owner = shopping_list.user == user
    share = ShoppingShare.objects.filter(shopping_list=shopping_list, shared_with=user).first()
    if not is_owner and share is None:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return shopping_list, is_owner, share


def generate_base64_qr(url):
    """Gera um QR Code em Base64 para inclusão direta em HTML/PDF."""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ────────────────────────── core views ───────────────────────────

def home(request):
    """Nova Landing Page Premium como index da aplicação."""
    if request.user.is_authenticated:
        return redirect('shopping:dashboard_redirect')
    return render(request, 'shopping/landing.html')


@login_required
def redirect_by_role(request):
    """Encaminha o usuário baseando-se no seu nível de permissão."""
    if request.user.is_staff:
        return redirect('shopping:admin_dashboard')
    return redirect('shopping:index')


@login_required
def index(request):
    """Página principal do cliente: exibe todas as suas listas."""
    own_lists = ShoppingList.objects.filter(user=request.user, is_template=False)
    shared_ids = ShoppingShare.objects.filter(shared_with=request.user).values_list('shopping_list_id', flat=True)
    shared_lists = ShoppingList.objects.filter(id__in=shared_ids)

    # Templates públicos disponíveis para clonagem
    templates = ShoppingList.objects.filter(is_template=True)

    form = ShoppingListForm()
    if request.method == 'POST':
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            new_list = form.save(commit=False)
            new_list.user = request.user
            new_list.save()
            messages.success(request, 'Lista criada com sucesso!')
            return redirect('shopping:list_detail', uuid=new_list.uuid)

    # Cálculo de estatísticas rápidas
    total_items = sum(lst.items.count() for lst in own_lists) + \
                  sum(lst.items.count() for lst in shared_lists)

    return render(request, 'shopping/index.html', {
        'own_lists': own_lists,
        'shared_lists': shared_lists,
        'templates': templates,
        'form': form,
        'total_items': total_items, # Passando estatística para o template
    })


@login_required
def list_detail(request, uuid):
    """Detalha uma lista com itens e formulário de adição."""
    shopping_list, is_owner, share = _get_list_or_403(uuid, request.user)
    can_edit = (is_owner or (share and share.can_edit)) and not shopping_list.is_locked

    items = shopping_list.items.all().select_related('product')
    pending_items = items.filter(is_purchased=False)
    bought_items = items.filter(is_purchased=True)
    
    item_form = ShoppingItemForm() if can_edit else None

    return render(request, 'shopping/list_detail.html', {
        'list': shopping_list,
        'is_owner': is_owner,
        'can_edit': can_edit,
        'pending_items': pending_items,
        'bought_items': bought_items,
        'item_form': item_form,
        'total_all': shopping_list.get_total(),
        'total_pix': shopping_list.get_pix_total(),
    })


# ───────────────────────── staff views ──────────────────────────

@staff_member_required
def admin_dashboard(request):
    """Pipeline de pedidos (Staff)."""
    listas = ShoppingList.objects.filter(is_template=False).order_by('-created_at')
    
    context = {
        'listas': listas,
        'qtd_finalizadas': listas.filter(is_locked=True).count(),
        'qtd_nao_finalizadas': listas.filter(is_locked=False).count(),
    }
    return render(request, 'shopping/staff/dashboard.html', context)


@staff_member_required
def update_status_htmx(request, uuid):
    """Atualiza o status da lista via HTMX."""
    lista = get_object_or_404(ShoppingList, uuid=uuid)
    novo_status = request.POST.get('status')
    
    if novo_status in dict(ShoppingList.STATUS_CHOICES):
        lista.status = novo_status
        # Se fechar ou avançar, tranca a edição para o cliente
        if novo_status != 'aberta':
            lista.is_locked = True
        else:
            lista.is_locked = False
        lista.save()
        
    return render(request, 'shopping/staff/components/shoppinglist_row.html', {'lista': lista})


@staff_member_required
def import_products_csv(request):
    """Importação massiva de produtos."""
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        list_name = request.POST.get('list_name')
        
        if not csv_file:
            messages.error(request, 'Nenhum arquivo enviado.')
            return redirect('shopping:admin_catalogo')
            
        try:
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string) # Pular header

            count = 0
            csv_products = []
            for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                product, _ = Product.objects.update_or_create(
                    name=row[0],
                    defaults={
                        'price': Decimal(row[1]),
                        'category': row[2],
                        'stock': int(row[3]),
                        'barcode': row[4],
                        'image_url': row[5] if len(row) > 5 else None,
                    }
                )
                csv_products.append(product)
                count += 1
                
            if list_name and list_name.strip():
                template_name = list_name.strip()
                template_list = ShoppingList.objects.create(
                    user=request.user,
                    name=template_name,
                    is_template=True,
                    school=template_name 
                )
                for prod in csv_products:
                    ShoppingItem.objects.create(
                        shopping_list=template_list,
                        product=prod,
                        name=prod.name,
                        quantity=1,
                        price=prod.price,
                        category=prod.category
                    )
                messages.success(request, f'{count} produtos armazenados e novo Template Institucional "{template_name}" criado com sucesso!')
            else:
                messages.success(request, f'{count} produtos processados e atualizados no catálogo!')
        except Exception as e:
            messages.error(request, f'Erro ao processar CSV: {e}')
            
        return redirect('shopping:admin_catalogo')
    
    return render(request, 'shopping/staff/import_csv.html')


@staff_member_required
def generate_picking_pdf(request, uuid):
    """Gera PDF de separação (Picking List)."""
    lista = get_object_or_404(ShoppingList, uuid=uuid)
    items = lista.items.all().select_related('product').order_by('product__category')
    
    qr_base64 = generate_base64_qr(request.build_absolute_uri(lista.get_absolute_url()))
    
    context = {
        'shopping_list': lista,
        'items': items,
        'total': lista.get_total(),
        'pix_total': lista.get_pix_total(),
        'qr_base64': qr_base64,
    }
    
    html_string = render_to_string('shopping/staff/pdf/picking_list.html', context)
    
    try:
        from weasyprint import HTML
        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Picking_{lista.uuid.hex[:8]}.pdf"'
        return response
    except Exception as e:
        return HttpResponse(f"Erro PDF: {e}", status=500)


@staff_member_required
def admin_catalogo(request):
    """Visão geral do catálogo e templates."""
    products = Product.objects.all()
    templates = ShoppingList.objects.filter(is_template=True)
    return render(request, 'shopping/staff/catalogo.html', {
        'products': products,
        'templates': templates,
    })


# ───────────────────────── item views ──────────────────────────


@login_required
def item_add(request, list_uuid):
    """Adiciona item à lista."""
    shopping_list, is_owner, share = _get_list_or_403(list_uuid, request.user)
    if shopping_list.is_locked:
        messages.error(request, 'Lista travada para edição.')
        return redirect('shopping:list_detail', uuid=list_uuid)

    form = ShoppingItemForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.shopping_list = shopping_list
        item.save()
        return redirect('shopping:list_detail', uuid=list_uuid)

    return render(request, 'shopping/item_form.html', {'form': form, 'list': shopping_list})


@login_required
def item_edit(request, list_uuid, item_uuid):
    """Edita item (Suporta HTMX +/-)."""
    shopping_list, is_owner, share = _get_list_or_403(list_uuid, request.user)
    if shopping_list.is_locked:
        return HttpResponse('Lista travada', status=403)

    item = get_object_or_404(ShoppingItem, uuid=item_uuid, shopping_list=shopping_list)
    
    action = request.GET.get('action')
    if request.method == 'POST' and action in ['inc', 'dec']:
        if action == 'inc':
            item.quantity += 1
        elif action == 'dec' and item.quantity > 1:
            item.quantity -= 1
        item.save(update_fields=['quantity'])
        
        response = render(request, 'shopping/partials/item_row.html', {
            'item': item, 'list': shopping_list, 'can_edit': True
        })
        response['HX-Trigger'] = 'update-totals'
        return response

    form = ShoppingItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('shopping:list_detail', uuid=list_uuid)

    return render(request, 'shopping/item_form.html', {'form': form, 'list': shopping_list, 'item': item})

@login_required
def item_delete(request, list_uuid, item_uuid):
    shopping_list, _, _ = _get_list_or_403(list_uuid, request.user)
    if shopping_list.is_locked: return HttpResponse(status=403)
    item = get_object_or_404(ShoppingItem, uuid=item_uuid, shopping_list=shopping_list)
    item.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse('')
        response['HX-Trigger'] = 'update-totals'
        return response
    return redirect('shopping:list_detail', uuid=list_uuid)

@login_required
def item_toggle(request, list_uuid, item_uuid):
    item = get_object_or_404(ShoppingItem, uuid=item_uuid, shopping_list__uuid=list_uuid)
    item.is_purchased = not item.is_purchased
    item.save(update_fields=['is_purchased'])
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Refresh': 'true'})
    return redirect('shopping:list_detail', uuid=list_uuid)

@login_required
def list_share(request, uuid):
    shopping_list = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    form = ShareListForm(request.POST or None)
    if form.is_valid():
        target_user = form.cleaned_data['username']
        ShoppingShare.objects.update_or_create(
            shopping_list=shopping_list, shared_with=target_user,
            defaults={'shared_by': request.user, 'can_edit': form.cleaned_data['can_edit']}
        )
        return redirect('shopping:list_share', uuid=uuid)
    return render(request, 'shopping/list_share.html', {'list': shopping_list, 'form': form, 'shares': shopping_list.shares.all()})

@login_required
def share_remove(request, uuid, share_id):
    share = get_object_or_404(ShoppingShare, id=share_id, shopping_list__uuid=uuid, shopping_list__user=request.user)
    share.delete()
    return redirect('shopping:list_share', uuid=uuid)

@login_required
def list_totals(request, uuid):
    shopping_list, _, _ = _get_list_or_403(uuid, request.user)
    return render(request, 'shopping/partials/footer_summary.html', {
        'list': shopping_list,
        'total_all': shopping_list.get_total(),
        'total_pix': shopping_list.get_pix_total(),
    })

@login_required
def list_qrcode(request, uuid):
    """Gera um QR Code dinâmico para a lista (join ou clone)."""
    shopping_list, _, _ = _get_list_or_403(uuid, request.user)
    
    qr_type = request.GET.get('type', 'clone')
    from django.urls import reverse
    
    if qr_type == 'join':
        url_path = reverse('shopping:list_join', args=[uuid])
    else:
        url_path = reverse('shopping:list_clone', args=[uuid])
        
    full_url = request.build_absolute_uri(url_path)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(full_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    
    return HttpResponse(buf.getvalue(), content_type="image/png")

@login_required
def list_pdf(request, uuid):
    # Reutiliza lógica de picking mas com template de cliente
    return generate_picking_pdf(request, uuid) # Simplificado para teste

@login_required
def list_clone(request, uuid):
    # Permite clonar qualquer lista válida (não somente aquelas marcadas como template),
    # para suportar o uso de links gerados pela tela de compartilhamento.
    template = get_object_or_404(ShoppingList, uuid=uuid)

    if request.method == 'POST':
        nova = ShoppingList.objects.create(
            user=request.user,
            name=f"Cópia de {template.school}",
            school=template.school,
            grade=template.grade,
            is_template=False,
        )
        for item in template.items.all():
            ShoppingItem.objects.create(
                shopping_list=nova,
                product=item.product,
                quantity=item.quantity,
                name=item.name,
                price=item.price,
                category=item.category,
            )
        return redirect('shopping:list_detail', uuid=nova.uuid)

    return render(request, 'shopping/list_clone_confirm.html', {'list': template})

@login_required
def list_join(request, uuid):
    lista = get_object_or_404(ShoppingList, uuid=uuid)
    ShoppingShare.objects.get_or_create(shopping_list=lista, shared_with=request.user, defaults={'shared_by': lista.user, 'can_edit': True})
    return redirect('shopping:list_detail', uuid=uuid)

@login_required
def list_budget(request, uuid):
    lista = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    form = BudgetListForm(request.POST or None, instance=lista)
    if form.is_valid():
        form.save()
        return redirect('shopping:list_detail', uuid=uuid)
    return render(request, 'shopping/list_budget.html', {'form': form, 'list': lista})

@login_required
def list_edit(request, uuid):
    lista = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    form = ShoppingListForm(request.POST or None, instance=lista)
    if request.method == 'POST':
        # Permite bloquear a lista via POST direto do footer
        if request.POST.get('is_locked') == 'True':
            lista.is_locked = True
            lista.status = 'fechada'  # Atualiza o status para ser capturado no painel do administrador!
            lista.save()
            return redirect('shopping:list_detail', uuid=uuid)
            
        if form.is_valid():
            form.save()
            return redirect('shopping:list_detail', uuid=uuid)
    return render(request, 'shopping/list_form.html', {'form': form, 'list': lista})

@login_required
def list_delete(request, uuid):
    lista = get_object_or_404(ShoppingList, uuid=uuid, user=request.user)
    if request.method == 'POST':
        lista.delete()
        return redirect('shopping:index')
    return render(request, 'shopping/list_confirm_delete.html', {'list': lista})

@login_required
def shared_list_remove(request, uuid):
    """Remove o compartilhamento da lista para o usuário atual (não deleta a lista original)."""
    share = ShoppingShare.objects.filter(shopping_list__uuid=uuid, shared_with=request.user).first()
    if share:
        share.delete()
        messages.success(request, 'Lista removida da sua área compartilhada.')
    else:
        messages.error(request, 'Compartilhamento não encontrado.')
    return redirect('shopping:index')
