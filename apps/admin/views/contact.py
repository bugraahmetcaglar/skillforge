from django.http import HttpResponse


def contact_list_placeholder(request):
    return HttpResponse("Contact list - Coming Soon!")


def contact_detail_placeholder(request, pk):
    return HttpResponse(f"Contact detail {pk} - Coming Soon!")


def contact_create_placeholder(request):
    return HttpResponse("Contact create - Coming Soon!")