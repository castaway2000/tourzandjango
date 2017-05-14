import babel
from django.utils.translation import ugettext as _


languages = []
languages_native = []
languages_english = []

locales = babel.localedata.locale_identifiers()
locales.sort()
for l_id in locales:
    l = babel.Locale(l_id)
    if l.english_name:
        languages_english.append((l_id, _(l.english_name)))
        if l.display_name:
            languages_native.append((l_id, l.display_name))
            if l.display_name == l.english_name:
                label = '%s' % l.english_name
            else:
                label = '%s (%s)' % (l.display_name, l.english_name)
            languages.append((l_id, label))