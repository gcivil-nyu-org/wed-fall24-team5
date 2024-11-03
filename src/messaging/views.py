from django.http import JsonResponse


def messaging(request):
    return JsonResponse({"message": "Messaging functionality coming up soon"})
