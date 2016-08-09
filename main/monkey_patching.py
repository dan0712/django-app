from django.forms import Textarea
from pages.widgets_registry import register_widget


class TinyMceTextArea(Textarea):
    """A RichTextarea widget."""

    class Media:
        js = ['tinymce_4/tinymce/tinymce.min.js',
              'tinymce_4/settings/django-filebrowser.js',
              'tinymce_4/settings/full.js'
              ]
        css = {
            'all': [
                'tinymce_4/settings/django-grapelli.css',
            ]
        }

    def __init__(self, language=None, attrs=None, **kwargs):
        attrs = {'class': 'tinymce'}
        self.language = language
        super(TinyMceTextArea, self).__init__(attrs)

    def render(self, name, value, attrs=None, **kwargs):
        rendered = super(TinyMceTextArea, self).render(name, value, attrs)
        return rendered


register_widget(TinyMceTextArea)
