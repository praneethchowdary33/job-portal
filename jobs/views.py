from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import RegisterForm, JobForm, ApplicationForm
from .models import Job, Application


def home(request):
    jobs = Job.objects.all()
    location = request.GET.get('location', '')
    q = request.GET.get('q', '')
    if location:
        jobs = jobs.filter(location__icontains=location)
    if q:
        jobs = jobs.filter(title__icontains=q) | jobs.filter(skills__icontains=q)
    return render(request, 'jobs/home.html', {'jobs': jobs, 'location': location, 'q': q})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            group, _ = Group.objects.get_or_create(name=form.cleaned_data['role'])
            user.groups.add(group)
            messages.success(request, 'Account created. Please login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'jobs/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid username or password')
    return render(request, 'jobs/login.html')


def user_logout(request):
    logout(request)
    return redirect('home')

def is_recruiter(user):
    return user.is_authenticated and user.groups.filter(name='recruiter').exists()


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    applied = request.user.is_authenticated and Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'applied': applied})


@login_required
def post_job(request):
    if not is_recruiter(request.user):
        messages.error(request, 'Only recruiters can post jobs')
        return redirect('home')
    form = JobForm(request.POST or None)
    if form.is_valid():
        job = form.save(commit=False)
        job.recruiter = request.user
        job.save()
        messages.success(request, 'Job posted successfully')
        return redirect('dashboard')
    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if is_recruiter(request.user):
        messages.error(request, 'Recruiters cannot apply for jobs')
        return redirect('job_detail', pk=pk)
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, 'You already applied for this job')
        return redirect('my_applications')
    form = ApplicationForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        app = form.save(commit=False)
        app.job = job
        app.applicant = request.user
        app.save()
        messages.success(request, 'Applied successfully')
        return redirect('my_applications')
    return render(request, 'jobs/apply.html', {'form': form, 'job': job})


@login_required
def my_applications(request):
    apps = Application.objects.filter(applicant=request.user).select_related('job')
    return render(request, 'jobs/my_applications.html', {'applications': apps})


@login_required
def dashboard(request):
    if not is_recruiter(request.user):
        return redirect('my_applications')
    jobs = Job.objects.filter(recruiter=request.user)
    return render(request, 'jobs/dashboard.html', {'jobs': jobs})


@login_required
def job_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    if request.method == 'POST':
        app = get_object_or_404(Application, pk=request.POST.get('app_id'), job=job)
        status = request.POST.get('status')
        if status in dict(Application.STATUS_CHOICES):
            app.status = status
            app.save()
        return redirect('job_applicants', pk=pk)
    return render(request, 'jobs/job_applicants.html', {'job': job, 'applications': job.applications.select_related('applicant')})