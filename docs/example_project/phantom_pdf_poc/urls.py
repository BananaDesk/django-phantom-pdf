from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'phantom_pdf_poc.views.home', name='home'),
    url(r'^$', "poc.views.home"),
    url(r'^admin/', include(admin.site.urls)),
)
