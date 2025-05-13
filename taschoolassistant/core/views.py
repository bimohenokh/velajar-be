from django.http import HttpResponse


def health_check(request):
    # You can add more sophisticated checks here if needed,
    # e.g., check database connection, cache, etc.
    return HttpResponse("OK", status=200)