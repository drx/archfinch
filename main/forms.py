from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.http import int_to_base36
from django.contrib.formtools.wizard import FormWizard
from django import forms
from archfinch.main.models import Item, ItemProfile
from django.shortcuts import redirect


class AddItemForm1(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'category')


class AddItemForm2(forms.Form):
    pass


class AddItemWizard(FormWizard):
    def done(self, request, form_list):
        item = form_list[0]
        item = item.save()
        item_profile = ItemProfile(item=item)
        item_profile.save()
        item.profile = item_profile
        item.submitter = request.user
        item.save()
        return redirect(reverse('item', args=[int_to_base36(item.id), slugify(item.name)]))

    def get_template(self, step):
        return 'main/additem.html'

    def process_step(self, request, form, step):
        if step != 0:
            return

        if form.is_valid():
            potential_conflicts = Item.search.query('"'+form.cleaned_data['name']+'"').filter(category_id=form.cleaned_data['category'].id)

            if potential_conflicts.count() > 0:
                potential_conflicts = potential_conflicts[0:100]
                self.extra_context = locals()

            else:
                self.form_list.remove(AddItemForm2)
