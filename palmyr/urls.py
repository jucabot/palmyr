from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'palmyrweb.views.home', name='home'),
    # url(r'^palmyr/', include('palmyr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^accounts/logout_then_login', 'django.contrib.auth.views.logout_then_login',name="logout"),
    
    url(r'^datasource/browse$', 'palmyrweb.views.browse_datasource', name='browse-datasource'),
    url(r'^datasource/upload$', 'palmyrweb.views.upload_file', name='upload-datasource'),
    url(r'^analysis/browse$', 'palmyrweb.views.browse_analysis', name='browse-analysis'),
    url(r'^analysis/create$', 'palmyrweb.views.create_analysis', name='create-analysis'),
    url(r'^analysis/open$', 'palmyrweb.views.open_analysis', name='open-analysis'),
    url(r'^analysis/summary$', 'palmyrweb.views.summary_analysis', name='summary-analysis'),
    url(r'^analysis/correlate$', 'palmyrweb.views.correlate_analysis', name='correlate-analysis'),
    url(r'^analysis/model$', 'palmyrweb.views.model_analysis', name='model-analysis'),
    url(r'^analysis/api$', 'palmyrweb.api.views.api_analysis', name='api-analysis'),
)
