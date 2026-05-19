import json
from django.shortcuts import render, redirect, get_object_or_404
from . import forms, models
from django.db.models import Sum, Q
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import date
from django.core.mail import send_mail
from django.contrib import messages


# ─── HELPERS ─────────────────────────────────────────────────────────────────────

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='ADMIN').exists()


def is_worker_or_admin(user):
    return user.is_superuser or user.groups.filter(name__in=['ADMIN', 'WORKER']).exists()


def admin_required(view_func):
    """Decorator: only ADMIN/superuser allowed."""
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('adminlogin')
        if not is_admin(request.user):
            messages.error(request, "Accès refusé : réservé à l’administrateur.")
            return redirect('admin-dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def worker_required(view_func):
    """Decorator: ADMIN or WORKER allowed."""
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('adminlogin')
        if not is_worker_or_admin(request.user):
            messages.error(request, "Accès refusé.")
            return redirect('adminlogin')
        return view_func(request, *args, **kwargs)
    return _wrapped


def get_or_create_agent(user):
    """Auto-create AgentCommercial for a user if it doesn’t exist."""
    agent, _ = models.AgentCommercial.objects.get_or_create(user=user)
    return agent


# ─── AUTH / HOME ─────────────────────────────────────────────────────────────────

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return redirect('adminlogin')


def afterlogin_view(request):
    # Everyone goes to dashboard — permissions enforced per-view
    return redirect('admin-dashboard')


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@worker_required
def admin_dashboard_view(request):
    # Auto-create AgentCommercial for current user on first login
    get_or_create_agent(request.user)

    total_prime = models.Dossier.objects.aggregate(Sum('prime_totale'))['prime_totale__sum'] or 0
    total_encaisse = models.Dossier.objects.aggregate(Sum('montant_encaisse'))['montant_encaisse__sum'] or 0
    context = {
        'total_clients': models.Client.objects.count(),
        'total_dossiers': models.Dossier.objects.count(),
        'total_categories': models.Category.objects.count(),
        'total_vehicles': models.Vehicle.objects.count(),
        'total_agents': models.AgentCommercial.objects.count(),
        'dossiers_actifs': models.Dossier.objects.filter(status='Actif').count(),
        'dossiers_expires': models.Dossier.objects.filter(status='Expiré').count(),
        'dossiers_en_attente': models.Dossier.objects.filter(status='En attente').count(),
        'total_prime': total_prime,
        'total_encaisse': total_encaisse,
        'total_reste': total_prime - total_encaisse,
        'remises_en_attente': models.RemiseCompagnie.objects.filter(status='En attente').count(),
        'recent_dossiers': models.Dossier.objects.order_by('-date_creation')[:5],
        'is_admin': is_admin(request.user),
    }
    return render(request, 'insurance/admin_dashboard.html', context)


# ─── WORKERS (admin only) ───────────────────────────────────────────────────────────

@admin_required
def admin_view_workers_view(request):
    worker_group = Group.objects.filter(name='WORKER').first()
    workers = worker_group.user_set.all() if worker_group else User.objects.none()
    return render(request, 'insurance/admin_view_workers.html', {'workers': workers})


@admin_required
def admin_add_worker_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        if not username or not password:
            messages.error(request, "Nom d’utilisateur et mot de passe obligatoires.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, f"Le nom d’utilisateur '{username}' existe déjà.")
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            worker_group, _ = Group.objects.get_or_create(name='WORKER')
            user.groups.add(worker_group)
            models.AgentCommercial.objects.get_or_create(user=user, defaults={'mobile': mobile})
            messages.success(request, f"Employé(e) '{username}' créé(e) avec succès.")
            return redirect('admin-view-workers')
    return render(request, 'insurance/admin_add_worker.html')


@admin_required
def admin_toggle_worker_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    agent = get_object_or_404(models.AgentCommercial, user=user)
    agent.is_active = not agent.is_active
    agent.save()
    user.is_active = agent.is_active
    user.save()
    status = "activé" if agent.is_active else "désactivé"
    messages.success(request, f"Compte de {user.username} {status}.")
    return redirect('admin-view-workers')


@admin_required
def admin_delete_worker_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('admin-view-workers')
    user.delete()
    messages.success(request, "Employé(e) supprimé(e).")
    return redirect('admin-view-workers')


# ─── CLIENTS ───────────────────────────────────────────────────────────────────

@worker_required
def admin_view_client_view(request):
    q = request.GET.get('q', '')
    clients = models.Client.objects.all()
    if q:
        clients = clients.filter(
            Q(nom_complet__icontains=q) | Q(telephone__icontains=q) | Q(cin__icontains=q)
        )
    return render(request, 'insurance/admin_view_client.html', {'clients': clients, 'q': q})


@worker_required
def admin_add_client_view(request):
    clientForm = forms.ClientForm()
    if request.method == 'POST':
        clientForm = forms.ClientForm(request.POST)
        if clientForm.is_valid():
            clientForm.save()
            return redirect('admin-view-client')
    return render(request, 'insurance/admin_add_client.html', {'clientForm': clientForm})


@worker_required
def update_client_view(request, pk):
    client = get_object_or_404(models.Client, pk=pk)
    clientForm = forms.ClientForm(instance=client)
    if request.method == 'POST':
        clientForm = forms.ClientForm(request.POST, instance=client)
        if clientForm.is_valid():
            clientForm.save()
            return redirect('admin-view-client')
    return render(request, 'insurance/update_client.html', {'clientForm': clientForm, 'client': client})


@admin_required
def delete_client_view(request, pk):
    client = get_object_or_404(models.Client, pk=pk)
    client.delete()
    return redirect('admin-view-client')


@worker_required
def client_detail_ajax(request, pk):
    client = get_object_or_404(models.Client, pk=pk)
    vehicles = list(client.vehicles.values('id', 'marque', 'modele', 'immatriculation'))
    return JsonResponse({
        'nom_complet': client.nom_complet,
        'telephone': client.telephone,
        'cin': client.cin or '',
        'vehicles': vehicles,
    })


@worker_required
def client_search_ajax(request):
    q = request.GET.get('q', '')
    results = []
    if len(q) >= 2:
        clients = models.Client.objects.filter(
            Q(nom_complet__icontains=q) | Q(telephone__icontains=q) | Q(cin__icontains=q)
        )[:10]
        results = [{'id': c.id, 'text': str(c)} for c in clients]
    return JsonResponse({'results': results})


# ─── CATEGORIES ────────────────────────────────────────────────────────────────

@worker_required
def admin_category_view(request):
    return render(request, 'insurance/admin_category.html')


@worker_required
def admin_add_category_view(request):
    categoryForm = forms.CategoryForm()
    if request.method == 'POST':
        categoryForm = forms.CategoryForm(request.POST)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request, 'insurance/admin_add_category.html', {'categoryForm': categoryForm})


@worker_required
def admin_view_category_view(request):
    categories = models.Category.objects.all()
    return render(request, 'insurance/admin_view_category.html', {'categories': categories})


@admin_required
def admin_delete_category_view(request):
    categories = models.Category.objects.all()
    return render(request, 'insurance/admin_delete_category.html', {'categories': categories})


@admin_required
def delete_category_view(request, pk):
    category = models.Category.objects.get(id=pk)
    category.delete()
    return redirect('admin-view-category')


@worker_required
def admin_update_category_view(request):
    categories = models.Category.objects.all()
    return render(request, 'insurance/admin_update_category.html', {'categories': categories})


@worker_required
def update_category_view(request, pk):
    category = models.Category.objects.get(id=pk)
    categoryForm = forms.CategoryForm(instance=category)
    if request.method == 'POST':
        categoryForm = forms.CategoryForm(request.POST, instance=category)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request, 'insurance/update_category.html', {'categoryForm': categoryForm})


# ─── DOSSIERS ──────────────────────────────────────────────────────────────────

@worker_required
def admin_dossier_view(request):
    return render(request, 'insurance/admin_dossier.html')


@worker_required
def admin_add_dossier_view(request):
    categories = models.Category.objects.all().order_by('code_categorie')
    clients = models.Client.objects.all().order_by('nom_complet')
    dossierForm = forms.DossierForm()

    if request.method == 'POST':
        dossierForm = forms.DossierForm(request.POST)
        if dossierForm.is_valid():
            dossier = dossierForm.save(commit=False)
            # Auto-assign agent_commercial to current user
            dossier.agent_commercial = get_or_create_agent(request.user)
            dossier.save()
            return redirect('admin-view-dossier')

    return render(request, 'insurance/admin_add_dossier.html', {
        'dossierForm': dossierForm,
        'clients': clients,
        'categories': categories,
    })


@worker_required
def admin_view_dossier_view(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    cat_filter = request.GET.get('categorie', '')
    dossiers = models.Dossier.objects.select_related(
        'client', 'vehicle', 'categorie', 'agent_commercial__user'
    ).all()
    if q:
        dossiers = dossiers.filter(
            Q(assure__icontains=q) | Q(numero_police__icontains=q) |
            Q(client__nom_complet__icontains=q) | Q(vehicle__immatriculation__icontains=q) |
            Q(numero_attestation__icontains=q) | Q(numero_quittance__icontains=q)
        )
    if status_filter:
        dossiers = dossiers.filter(status=status_filter)
    if cat_filter:
        dossiers = dossiers.filter(categorie_id=cat_filter)
    categories = models.Category.objects.all()
    return render(request, 'insurance/admin_view_dossier.html', {
        'dossiers': dossiers, 'q': q,
        'status_filter': status_filter,
        'cat_filter': cat_filter,
        'categories': categories,
    })


@worker_required
def update_dossier_view(request, pk):
    dossier = get_object_or_404(models.Dossier, pk=pk)
    categories = models.Category.objects.all().order_by('code_categorie')
    clients = models.Client.objects.all().order_by('nom_complet')
    dossierForm = forms.DossierForm(instance=dossier)
    if request.method == 'POST':
        dossierForm = forms.DossierForm(request.POST, instance=dossier)
        if dossierForm.is_valid():
            dossierForm.save()
            return redirect('admin-view-dossier')
    return render(request, 'insurance/update_dossier.html', {
        'dossierForm': dossierForm, 'clients': clients,
        'categories': categories, 'dossier': dossier,
    })


@admin_required
def delete_dossier_view(request, pk):
    dossier = get_object_or_404(models.Dossier, pk=pk)
    dossier.delete()
    return redirect('admin-view-dossier')


# ─── VEHICLES ──────────────────────────────────────────────────────────────────

@worker_required
def admin_add_vehicle_view(request):
    vehicleForm = forms.VehicleForm()
    if request.method == 'POST':
        vehicleForm = forms.VehicleForm(request.POST)
        if vehicleForm.is_valid():
            vehicleForm.save()
            return redirect('admin-view-vehicle')
    return render(request, 'insurance/admin_add_vehicle.html', {'vehicleForm': vehicleForm})


@worker_required
def admin_view_vehicle_view(request):
    vehicles = models.Vehicle.objects.select_related('categorie', 'client').all()
    return render(request, 'insurance/admin_view_vehicle.html', {'vehicles': vehicles})


# ─── REMISE COMPAGNIE ──────────────────────────────────────────────────────────

@admin_required
def admin_view_remise_view(request):
    remises = models.RemiseCompagnie.objects.all()
    return render(request, 'insurance/admin_view_remise.html', {'remises': remises})


@admin_required
def admin_add_remise_view(request):
    remiseForm = forms.RemiseCompagnieForm()
    if request.method == 'POST':
        remiseForm = forms.RemiseCompagnieForm(request.POST)
        if remiseForm.is_valid():
            remise = remiseForm.save(commit=False)
            remise.created_by = request.user
            remise.save()
            remiseForm.save_m2m()
            return redirect('admin-view-remise')
    return render(request, 'insurance/admin_add_remise.html', {'remiseForm': remiseForm})


# ─── QUESTIONS ─────────────────────────────────────────────────────────────────

@worker_required
def admin_question_view(request):
    questions = models.Question.objects.all()
    return render(request, 'insurance/admin_question.html', {'questions': questions})


@worker_required
def update_question_view(request, pk):
    question = models.Question.objects.get(id=pk)
    questionForm = forms.QuestionForm(instance=question)
    if request.method == 'POST':
        questionForm = forms.QuestionForm(request.POST, instance=question)
        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            question.admin_comment = request.POST.get('admin_comment')
            question.save()
            return redirect('admin-question')
    return render(request, 'insurance/update_question.html', {'questionForm': questionForm})


# ─── MISC ──────────────────────────────────────────────────────────────────────

def aboutus_view(request):
    return render(request, 'insurance/aboutus.html')


def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(
                str(name) + ' || ' + str(email),
                message,
                settings.EMAIL_HOST_USER,
                settings.EMAIL_RECEIVING_USER,
                fail_silently=False
            )
            return render(request, 'insurance/contactussuccess.html')
    return render(request, 'insurance/contactus.html', {'form': sub})
