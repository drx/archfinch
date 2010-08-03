from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.http import int_to_base36
from django.contrib.formtools.wizard import FormWizard
from django import forms
from main.models import Item
from django.shortcuts import redirect


class AddItemForm1(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'category')


class AddItemForm2(forms.Form):
    pass


class AddItemWizard(FormWizard):
    def done(self, request, form_list):
        item = form_list[0].save()
        return redirect(reverse('item', args=[int_to_base36(item.id), slugify(item.name)]))

    def get_template(self, step):
        return 'main/additem.html'

    def process_step(self, request, form, step):
        if step != 0:
            return

        if form.is_valid():
            potential_conflicts = Item.objects.filter(category=form.cleaned_data['category']).filter(name__icontains=form.cleaned_data['name'])

            if potential_conflicts.count() > 0:
                potential_conflicts = potential_conflicts[:100]
                self.extra_context = locals()

            else:
                self.form_list.remove(AddItemForm2)
