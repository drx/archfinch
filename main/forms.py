from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.http import int_to_base36
from django.contrib.formtools.wizard import FormWizard
from django import forms
from django.conf import settings
from archfinch.main import tasks
from archfinch.main.models import Item, ItemProfile, Category
from archfinch.links.models import Link
from archfinch.links.scraper import scrape, generate_thumbnail
from archfinch.utils.spam import AntiSpamModelForm
from django.shortcuts import redirect


class AddItemForm1(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.filter(hide=False))
    class Meta:
        model = Item
        fields = ('name', 'category')


class AddLinkForm1(forms.ModelForm):
    name = forms.CharField(max_length=1000, label='Title', widget=forms.TextInput(attrs={'size': '40'}))
    url = forms.CharField(max_length=1000, label='URL', widget=forms.TextInput(attrs={'size': '40'}))
    class Meta:
        model = Link
        fields = ('name', 'url')


class AddItemForm2(forms.Form):
    pass


class AddItemWizard(FormWizard):
    def done(self, request, form_list):
        item = form_list[0]
        try:
            url = item.cleaned_data['url']
            existing_items = Item.objects.filter(link__url=url)
            if existing_items:
                return redirect(existing_items[0].get_absolute_url())
        except KeyError:
            pass
        item = item.save(commit=False)
        item.submitter = request.user
        item.get_meta_data()
        item.save()
        request.user.add_points(10)
        if self.model.__name__ == 'Link':
            tasks.opinion_set.delay(request.user, item, 4)

        return redirect(item.get_absolute_url())

    def get_template(self, step):
        return 'main/additem.html'

    def process_step(self, request, form, step):
        if step != 0:
            return

        if form.is_valid():
            if self.model.__name__ == 'Link':
                potential_conflicts = Item.objects.none()
            else:
                potential_conflicts = Item.search.query('"'+form.cleaned_data['name']+'"').filter(category_id=form.cleaned_data['category'].id)

            if potential_conflicts.count() > 0:
                potential_conflicts = potential_conflicts[0:100]
                self.extra_context = locals()

            else:
                self.form_list.remove(AddItemForm2)

    def parse_params(self, request, *args, **kwargs):
        self.model = kwargs['model']
        self.extra_context['model'] = self.model.__name__
