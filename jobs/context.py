def role(request):
    u = request.user
    return {'is_recruiter': u.is_authenticated and u.groups.filter(name='recruiter').exists()}