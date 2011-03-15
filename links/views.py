from archfinch.main.forms import AddLinkForm1, AddItemForm2, AddItemWizard
from archfinch.links.models import Link
from lazysignup.decorators import allow_lazy_user

@allow_lazy_user
def submit(request):
    wiz = AddItemWizard([AddLinkForm1, AddItemForm2])
    return wiz(request, model=Link)

