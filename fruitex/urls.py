from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fruitex.views.home', name='home'),
    # url(r'^fruitex/', include('fruitex.foo.urls')),
                       
    url(r'^home/', 'fruitex.views.home', name='home'),
    url(r'^items/', include('items.urls')),
    url(r'^cart/', 'cart.views.cart'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
