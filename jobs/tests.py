import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Job, Application


def make_user(username, role):
    user = User.objects.create_user(username=username, password='Test@12345')
    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)
    return user


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class JobPortalTests(TestCase):
    def setUp(self):
        self.recruiter = make_user('rec1', 'recruiter')
        self.seeker = make_user('seek1', 'seeker')
        self.job = Job.objects.create(
            recruiter=self.recruiter, title='Python Developer', company='Test Co',
            location='Hyderabad', skills='Python, Django', description='Test job',
        )

    def test_home_page_shows_jobs(self):
        r = self.client.get(reverse('home'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Python Developer')

    def test_location_filter_excludes_other_locations(self):
        r = self.client.get(reverse('home'), {'location': 'Chennai'})
        self.assertNotContains(r, 'Python Developer')

    def test_register_assigns_role(self):
        self.client.post(reverse('register'), {
            'username': 'new1', 'email': 'n@test.com',
            'password': 'Test@12345', 'role': 'recruiter',
        })
        user = User.objects.get(username='new1')
        self.assertTrue(user.groups.filter(name='recruiter').exists())

    def test_login_success_and_failure(self):
        ok = self.client.post(reverse('login'), {'username': 'seek1', 'password': 'Test@12345'})
        self.assertEqual(ok.status_code, 302)
        self.client.logout()
        bad = self.client.post(reverse('login'), {'username': 'seek1', 'password': 'wrong'})
        self.assertContains(bad, 'Invalid username or password')

    def test_anonymous_redirected_from_my_applications(self):
        r = self.client.get(reverse('my_applications'))
        self.assertEqual(r.status_code, 302)

    def test_recruiter_can_post_job(self):
        self.client.login(username='rec1', password='Test@12345')
        self.client.post(reverse('post_job'), {
            'title': 'Tester', 'company': 'ABC', 'location': 'Pune',
            'skills': 'Selenium', 'job_type': 'FT', 'description': 'QA role',
        })
        self.assertEqual(Job.objects.count(), 2)

    def test_seeker_cannot_post_job(self):
        self.client.login(username='seek1', password='Test@12345')
        self.client.post(reverse('post_job'), {
            'title': 'Tester', 'company': 'ABC', 'location': 'Pune',
            'skills': 'Selenium', 'job_type': 'FT', 'description': 'QA role',
        })
        self.assertEqual(Job.objects.count(), 1)

    def test_seeker_can_apply_with_resume(self):
        self.client.login(username='seek1', password='Test@12345')
        resume = SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test', content_type='application/pdf')
        self.client.post(reverse('apply_job', args=[self.job.pk]), {'resume': resume})
        self.assertEqual(Application.objects.filter(job=self.job, applicant=self.seeker).count(), 1)

    def test_recruiter_cannot_apply(self):
        self.client.login(username='rec1', password='Test@12345')
        resume = SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test', content_type='application/pdf')
        self.client.post(reverse('apply_job', args=[self.job.pk]), {'resume': resume})
        self.assertEqual(Application.objects.count(), 0)

    def test_duplicate_application_blocked(self):
        Application.objects.create(job=self.job, applicant=self.seeker, resume='resumes/x.pdf')
        self.client.login(username='seek1', password='Test@12345')
        resume = SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test', content_type='application/pdf')
        self.client.post(reverse('apply_job', args=[self.job.pk]), {'resume': resume})
        self.assertEqual(Application.objects.count(), 1)

    def test_recruiter_can_update_status(self):
        app = Application.objects.create(job=self.job, applicant=self.seeker, resume='resumes/x.pdf')
        self.client.login(username='rec1', password='Test@12345')
        self.client.post(reverse('job_applicants', args=[self.job.pk]),
                         {'app_id': app.pk, 'status': 'Shortlisted'})
        app.refresh_from_db()
        self.assertEqual(app.status, 'Shortlisted')

    def test_other_recruiter_cannot_view_applicants(self):
        make_user('rec2', 'recruiter')
        self.client.login(username='rec2', password='Test@12345')
        r = self.client.get(reverse('job_applicants', args=[self.job.pk]))
        self.assertEqual(r.status_code, 404)