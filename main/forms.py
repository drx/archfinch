from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.http import int_to_base36
from django.contrib.formtools.wizard import FormWizard
from django import forms
from archfinch.main import tasks
from archfinch.main.models import Item, ItemProfile, Category
from archfinch.links.models import Link
from archfinch.links.scraper import scrape, generate_thumbnail
from django.shortcuts import redirect


class AddItemForm1(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.filter(hide=False))
    class Meta:
        model = Item
        fields = ('name', 'category')


class AddLinkForm1(forms.ModelForm):
    name = forms.CharField(max_length=1000, label='Title')
    class Meta:
        model = Link
        fields = ('name', 'url')


class AddItemForm2(forms.Form):
    pass


class AddItemWizard(FormWizard):
    def done(self, request, form_list):
        item = form_list[0]
        item = item.save(commit=False)
        if self.model.__name__ == 'Link':
            scraped_data = scrape(item.url)
            item.category_id = scraped_data['category_id']
            if 'thumbnail_url' in scraped_data:
                item.thumbnail = {'url': scraped_data['thumbnail_url'], 'width': scraped_data['thumbnail_width'], 'height': scraped_data['thumbnail_height']}
            if 'url' in scraped_data:
                item.image = {'url': scraped_data['url'], 'width': scraped_data['width'], 'height': scraped_data['height']}
            if 'html' in scraped_data:
                item.html = scraped_data['html']
            if scraped_data['category'] == 'pic':
                generate_thumbnail(item)

                    
        item.save()
        item_profile = ItemProfile(item=item)
        item_profile.save()
        item.profile = item_profile
        item.submitter = request.user
        item.save()
        request.user.add_points(10)
        if self.model.__name__ == 'Link':
            tasks.opinion_set.delay(request.user, item, 5)
        return redirect(reverse('item', args=[int_to_base36(item.id), slugify(item.name)]))

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
