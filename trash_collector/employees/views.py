from django.db import models
from django.db.models.fields import NullBooleanField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.apps import apps
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from datetime import date

from .models import Employee
from customers.models import Customer

@login_required
def index(request):
    # The following line will get the logged-in user (if there is one) within any view function
    logged_in_user = request.user
    
    try:
        logged_in_employee = Employee.objects.get(user=logged_in_user)

        today = date.today()
        weekday = today.weekday()
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day = weekdays[weekday]
        zip_customers = Customer.objects.filter(zip_code=logged_in_employee.zip_code)
        weekly_pick_up_customers = Customer.objects.filter(weekly_pickup=day)
        one_time_pick_up_customers = Customer.objects.filter(one_time_pickup=today)
        all_customers = Customer.objects.all()
        non_suspended_customers = []
        for customer in all_customers:
            if customer.suspend_start < today and customer.suspend_end < today:
                non_suspended_customers.append(customer)
        context = {
            'logged_in_employee': logged_in_employee,
            'today': today,
            'weekday': weekday,
            'day': day,
            'zip_customers': zip_customers,
            'weekly_pick_up_customers': weekly_pick_up_customers,
            'one_time_pick_up_customers': one_time_pick_up_customers,
            'non_suspended_customers': non_suspended_customers
        }
        return render(request, 'employees/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))

@login_required
def create(request):
    logged_in_user = request.user
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        new_employee = Employee(name=name_from_form, user=logged_in_user, zip_code=zip_from_form)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')

@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        logged_in_employee.name = name_from_form
        logged_in_employee.zip_code = zip_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee': logged_in_employee
        }
        return render(request, 'employees/edit_profile.html', context)
