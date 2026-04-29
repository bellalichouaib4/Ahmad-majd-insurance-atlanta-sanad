import json
from django.shortcuts import render, redirect, get_object_or_404
from . import forms, models
from django.db.models import Sum, Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import date
from django.core.mail import send_mail
from django.contrib.auth.models import User
from customer import models as CMODEL
from customer import forms as CFORM


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'insurance/index.html')


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer/customer-dashboard')
    return redirect('admin-dashboard')


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    total_prime = models.Dossier.objects.aggregate(Sum('prime_totale'))['prime_totale__sum'] or 0
    total_encaisse = models.Dossier.objects.aggregate(Sum('montant_encaisse'))['montant_encaisse__sum'] or 0
    total_reste = total_prime - total_encaisse
    context = {
        'total_clients': models.Client.objects.count(),
        'total_dossiers': models.Dossier.objects.count(),
        'total_categories': models.Category.objects.count(),
        'total_vehicles': models.Vehicle.objects.count(),
        'total_agents': models.AgentCommercial.objects.count(),
        'dossiers_actifs': models.Dossier.objects.filter(status='Actif').count(),
        'dossiers_expires': models.Dossier.objects.filter(status='Expir\u00e9').count(),
        'dossiers_en_attente': models.Dossier.objects.filter(status='En attente').count(),
        'total_prime': total_prime,
        'total_encaisse': total_encaisse,
        'total_reste': total_reste,
        'remises_en_attente': models.RemiseCompagnie.objects.filter(status='En attente').count(),
        'recent_dossiers': models.Dossier.objects.order_by('-date_creation')[:5],
    }
    return render(request, 'insurance/admin_dashboard.html', context=context)


# ─── CLIENTS ───────────────────────────────────────────────────────────────────

@login_required(login_url='adminlogin')
def admin_view_client_view(request):
    q = request.GET.get('q', '')
    clients = models.Client.objects.all()
    if q:
        clients = clients.filter(
            Q(nom_complet__icontains=q) | Q(telephone__icontains=q) | Q(cin__icontains=q)
        )
    return render(request, 'insurance/admin_view_client.html', {'clients': clients, 'q': q})


@login_required(login_url='adminlogin')
def admin_add_client_view(request):
    clientForm = forms.ClientForm()
    if request.method == 'POST':
        clientForm = forms.ClientForm(request.POST)
        if clientForm.is_valid():
            clientForm.save()
            return redirect('admin-view-client')
    return render(request, 'insurance/admin_add_client.html', {'clientForm': clientForm})


@login_required(login_url='adminlogin')
def update_client_view(request, pk):
    client = get_object_or_404(models.Client, pk=pk)
    clientForm = forms.ClientForm(instance=client)
    if request.method == 'POST':
        clientForm = forms.ClientForm(request.POST, instance=client)
        if clientForm.is_valid():
            clientForm.save()
            return redirect('admin-view-client')
    return render(request, 'insurance/update_client.html', {'clientForm': clientForm, 'client': client})


@login_required(login_url='adminlogin')
def delete_client_view(request, pk):
    client = get_object_or_404(models.Client, pk=pk)
    client.delete()
    return redirect('admin-view-client')


# Ajax endpoint: return client JSON for autofill
@login_required(login_url='adminlogin')
def client_detail_ajax(request, pk):
    client = get_object_or_404(models.Client, pk=pk)
    vehicles = list(client.vehicles.values('id', 'marque', 'modele', 'immatriculation'))
    return JsonResponse({
        'nom_complet': client.nom_complet,
        'telephone': client.telephone,
        'cin': client.cin or '',
        'vehicles': vehicles,
    })


# Ajax: search clients by name/cin/tel
@login_required(login_url='adminlogin')
def client_search_ajax(request):
    q = request.GET.get('q', '')
    results = []
    if len(q) >= 2:
        clients = models.Client.objects.filter(
            Q(nom_complet__icontains=q) | Q(telephone__icontains=q) | Q(cin__icontains=q)
        )[:10]
        results = [{'id': c.id, 'text': str(c)} for c in clients]
    return JsonResponse({'results': results})


# Legacy customer views (kept)
@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    customers = CMODEL.Customer.objects.all()
    return render(request, 'insurance/admin_view_customer.html', {'customers': customers})


@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = CMODEL.Customer.objects.get(id=pk)
    user = User.objects.get(id=customer.user_id)
    userForm = CFORM.CustomerUserForm(instance=user)
    customerForm = CFORM.CustomerForm(request.FILES, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = CFORM.CustomerUserForm(request.POST, instance=user)
        customerForm = CFORM.CustomerForm(request.POST, request.FILES, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('admin-view-customer')
    return render(request, 'insurance/update_customer.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_customer_view(request, pk):
    customer = CMODEL.Customer.objects.get(id=pk)
    user = User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return HttpResponseRedirect('/admin-view-customer')


# ─── CATEGORIES ────────────────────────────────────────────────────────────────

@login_required(login_url='adminlogin')
def admin_category_view(request):
    return render(request, 'insurance/admin_category.html')


@login_required(login_url='adminlogin')
def admin_add_category_view(request):
    categoryForm = forms.CategoryForm()
    if request.method == 'POST':
        categoryForm = forms.CategoryForm(request.POST)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request, 'insurance/admin_add_category.html', {'categoryForm': categoryForm})


@login_required(login_url='adminlogin')
def admin_view_category_view(request):
    categories = models.Category.objects.all()
    return render(request, 'insurance/admin_view_category.html', {'categories': categories})


@login_required(login_url='adminlogin')
def admin_delete_category_view(request):
    categories = models.Category.objects.all()
    return render(request, 'insurance/admin_delete_category.html', {'categories': categories})


@login_required(login_url='adminlogin')
def delete_category_view(request, pk):
    category = models.Category.objects.get(id=pk)
    category.delete()
    return redirect('admin-view-category')


@login_required(login_url='adminlogin')
def admin_update_category_view(request):
    categories = models.Category.objects.all()
    return render(request, 'insurance/admin_update_category.html', {'categories': categories})


@login_required(login_url='adminlogin')
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

@login_required(login_url='adminlogin')
def admin_dossier_view(request):
    return render(request, 'insurance/admin_dossier.html')


@login_required(login_url='adminlogin')
def admin_add_dossier_view(request):
    dossierForm = forms.DossierForm()
    clients = models.Client.objects.all().order_by('nom_complet')
    if request.method == 'POST':
        dossierForm = forms.DossierForm(request.POST)
        if dossierForm.is_valid():
            dossierForm.save()
            return redirect('admin-view-dossier')
    return render(request, 'insurance/admin_add_dossier.html', {'dossierForm': dossierForm, 'clients': clients})


@login_required(login_url='adminlogin')
def admin_view_dossier_view(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    dossiers = models.Dossier.objects.select_related('client', 'vehicle', 'vehicle__categorie', 'agent_commercial').all()
    if q:
        dossiers = dossiers.filter(
            Q(assure__icontains=q) | Q(numero_police__icontains=q) |
            Q(client__nom_complet__icontains=q) | Q(vehicle__immatriculation__icontains=q) |
            Q(numero_attestation__icontains=q) | Q(numero_quittance__icontains=q)
        )
    if status_filter:
        dossiers = dossiers.filter(status=status_filter)
    return render(request, 'insurance/admin_view_dossier.html', {'dossiers': dossiers, 'q': q, 'status_filter': status_filter})


@login_required(login_url='adminlogin')
def update_dossier_view(request, pk):
    dossier = get_object_or_404(models.Dossier, pk=pk)
    dossierForm = forms.DossierForm(instance=dossier)
    clients = models.Client.objects.all().order_by('nom_complet')
    if request.method == 'POST':
        dossierForm = forms.DossierForm(request.POST, instance=dossier)
        if dossierForm.is_valid():
            dossierForm.save()
            return redirect('admin-view-dossier')
    return render(request, 'insurance/update_dossier.html', {'dossierForm': dossierForm, 'clients': clients})


@login_required(login_url='adminlogin')
def delete_dossier_view(request, pk):
    dossier = get_object_or_404(models.Dossier, pk=pk)
    dossier.delete()
    return redirect('admin-view-dossier')


# ─── VEHICLES ──────────────────────────────────────────────────────────────────

@login_required(login_url='adminlogin')
def admin_add_vehicle_view(request):
    vehicleForm = forms.VehicleForm()
    if request.method == 'POST':
        vehicleForm = forms.VehicleForm(request.POST)
        if vehicleForm.is_valid():
            vehicleForm.save()
            return redirect('admin-view-vehicle')
        # form invalid — fall through and show errors
    return render(request, 'insurance/admin_add_vehicle.html', {'vehicleForm': vehicleForm})


@login_required(login_url='adminlogin')
def admin_view_vehicle_view(request):
    vehicles = models.Vehicle.objects.select_related('categorie', 'client').all()
    return render(request, 'insurance/admin_view_vehicle.html', {'vehicles': vehicles})


# ─── REMISE COMPAGNIE ──────────────────────────────────────────────────────────

@login_required(login_url='adminlogin')
def admin_view_remise_view(request):
    remises = models.RemiseCompagnie.objects.all()
    return render(request, 'insurance/admin_view_remise.html', {'remises': remises})


@login_required(login_url='adminlogin')
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

@login_required(login_url='adminlogin')
def admin_question_view(request):
    questions = models.Question.objects.all()
    return render(request, 'insurance/admin_question.html', {'questions': questions})


@login_required(login_url='adminlogin')
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
