from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from .models import Company, StormEvent, Deployment
import logging
import time

logger = logging.getLogger(__name__)


def is_storm_admin(user):
    return user.is_authenticated and user.groups.filter(name='StormAdmins').exists()


def ratelimited_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f'login_attempts_{ip}'
        attempts = cache.get(cache_key, 0)
        
        if attempts >= 5:
            messages.error(request, 'Too many login attempts. Please try again later.')
            return redirect('admin:login')
        
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            cache.delete(cache_key)
            login(request, user)
            return redirect('home')
        else:
            cache.set(cache_key, attempts + 1, timeout=300)
            messages.error(request, 'Invalid username or password')
    return redirect('admin:login')


def health_check(request):
    try:
        Company.objects.exists()
        return JsonResponse({'status': 'healthy'}, status=200)
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=500)


def home(request):
    companies = Company.objects.filter(deleted_at__isnull=True)
    return render(request, 'storm_companies/home.html', {'companies': companies})


@user_passes_test(is_storm_admin)
def company_create(request):
    if request.method == 'POST':
        company = Company(
            name=request.POST.get('name'),
            contact_name=request.POST.get('contact_name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            services=request.POST.getlist('services'),
            status=request.POST.get('status', 'available'),
            notes=request.POST.get('notes', ''),
        )
        company.save()
        messages.success(request, f'{company.name} created successfully.')
        return redirect('home')
    return render(request, 'storm_companies/company_form.html', {'action': 'Create'})


@user_passes_test(is_storm_admin)
def company_update(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.name = request.POST.get('name')
        company.contact_name = request.POST.get('contact_name')
        company.phone = request.POST.get('phone')
        company.email = request.POST.get('email', '')
        company.address = request.POST.get('address', '')
        company.services = request.POST.getlist('services')
        company.status = request.POST.get('status', 'available')
        company.notes = request.POST.get('notes', '')
        company.save()
        messages.success(request, f'{company.name} updated successfully.')
        return redirect('home')
    return render(request, 'storm_companies/company_form.html', {'company': company, 'action': 'Update'})


@user_passes_test(is_storm_admin)
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.deleted_at = timezone.now()
        company.save()
        messages.success(request, f'{company.name} deleted.')
        return redirect('home')
    return render(request, 'storm_companies/company_confirm_delete.html', {'company': company})


def stormevent_list(request):
    events = StormEvent.objects.filter(deleted_at__isnull=True)
    return render(request, 'storm_companies/stormevent_list.html', {'events': events})


@user_passes_test(is_storm_admin)
def stormevent_create(request):
    if request.method == 'POST':
        event = StormEvent(
            name=request.POST.get('name'),
            date=request.POST.get('date'),
            severity=request.POST.get('severity'),
            affected_area=request.POST.get('affected_area'),
            description=request.POST.get('description', ''),
        )
        event.save()
        messages.success(request, f'{event.name} created successfully.')
        return redirect('stormevent_list')
    return render(request, 'storm_companies/stormevent_form.html', {'action': 'Create'})


@user_passes_test(is_storm_admin)
def stormevent_update(request, pk):
    event = get_object_or_404(StormEvent, pk=pk)
    if request.method == 'POST':
        event.name = request.POST.get('name')
        event.date = request.POST.get('date')
        event.severity = request.POST.get('severity')
        event.affected_area = request.POST.get('affected_area')
        event.description = request.POST.get('description', '')
        event.save()
        messages.success(request, f'{event.name} updated successfully.')
        return redirect('stormevent_list')
    return render(request, 'storm_companies/stormevent_form.html', {'event': event, 'action': 'Update'})


@user_passes_test(is_storm_admin)
def stormevent_delete(request, pk):
    event = get_object_or_404(StormEvent, pk=pk)
    if request.method == 'POST':
        event.deleted_at = timezone.now()
        event.save()
        messages.success(request, f'{event.name} deleted.')
        return redirect('stormevent_list')
    return render(request, 'storm_companies/stormevent_confirm_delete.html', {'event': event})


def deployment_list(request):
    deployments = Deployment.objects.filter(deleted_at__isnull=True).select_related('company', 'storm_event')
    return render(request, 'storm_companies/deployment_list.html', {'deployments': deployments})


@user_passes_test(is_storm_admin)
def deployment_create(request):
    companies = Company.objects.all()
    events = StormEvent.objects.all()
    hours = list(range(24))
    minutes = list(range(0, 60, 5))
    if request.method == 'POST':
        deployment = Deployment(
            company_id=request.POST.get('company'),
            storm_event_id=request.POST.get('storm_event'),
            status=request.POST.get('status', 'requested'),
            deployed_from_city=request.POST.get('deployed_from_city', ''),
            deployed_from_state=request.POST.get('deployed_from_state', ''),
            notes=request.POST.get('notes', ''),
        )
        deployment.save()
        messages.success(request, f'Deployment created successfully.')
        return redirect('deployment_list')
    return render(request, 'storm_companies/deployment_form.html', {'action': 'Create', 'companies': companies, 'events': events, 'hours': hours, 'minutes': minutes})


@user_passes_test(is_storm_admin)
def deployment_update(request, pk):
    deployment = get_object_or_404(Deployment, pk=pk)
    companies = Company.objects.all()
    events = StormEvent.objects.all()
    hours = list(range(24))
    minutes = list(range(0, 60, 5))
    if request.method == 'POST':
        deployment.company_id = request.POST.get('company')
        deployment.storm_event_id = request.POST.get('storm_event')
        deployment.status = request.POST.get('status', 'requested')
        deployment.deployed_from_city = request.POST.get('deployed_from_city', '')
        deployment.deployed_from_state = request.POST.get('deployed_from_state', '')
        deployment.notes = request.POST.get('notes', '')
        confirmed_date = request.POST.get('confirmed_date')
        confirmed_hour = request.POST.get('confirmed_hour')
        confirmed_minute = request.POST.get('confirmed_minute')
        if confirmed_date and confirmed_hour and confirmed_minute:
            deployment.confirmed_at = parse_datetime(f"{confirmed_date}T{confirmed_hour}:{confirmed_minute}:00")
        else:
            deployment.confirmed_at = None
        arrived_date = request.POST.get('arrived_date')
        arrived_hour = request.POST.get('arrived_hour')
        arrived_minute = request.POST.get('arrived_minute')
        if arrived_date and arrived_hour and arrived_minute:
            deployment.arrived_at = parse_datetime(f"{arrived_date}T{arrived_hour}:{arrived_minute}:00")
        else:
            deployment.arrived_at = None
        active_date = request.POST.get('active_date')
        active_hour = request.POST.get('active_hour')
        active_minute = request.POST.get('active_minute')
        if active_date and active_hour and active_minute:
            deployment.active_at = parse_datetime(f"{active_date}T{active_hour}:{active_minute}:00")
        else:
            deployment.active_at = None
        deployment.save()
        messages.success(request, f'Deployment updated successfully.')
        return redirect('deployment_list')
    return render(request, 'storm_companies/deployment_form.html', {'deployment': deployment, 'action': 'Update', 'companies': companies, 'events': events, 'hours': hours, 'minutes': minutes})


@user_passes_test(is_storm_admin)
def deployment_delete(request, pk):
    deployment = get_object_or_404(Deployment, pk=pk)
    if request.method == 'POST':
        deployment.deleted_at = timezone.now()
        deployment.save()
        messages.success(request, 'Deployment deleted.')
        return redirect('deployment_list')
    return render(request, 'storm_companies/deployment_confirm_delete.html', {'deployment': deployment})
