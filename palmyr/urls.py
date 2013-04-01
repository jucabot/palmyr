from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'web.views.home', name='home'),
    # url(r'^palmyr/', include('palmyr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^accounts/logout_then_login', 'django.contrib.auth.views.logout_then_login',name="logout"),
    
    url(r'^datasource/browse$', 'web.views.browse_datasource', name='browse-datasource'),
    url(r'^datasource/upload$', 'web.views.upload_file', name='upload-datasource'),
    url(r'^analysis/browse$', 'web.views.browse_analysis', name='browse-analysis'),
    url(r'^analysis/create$', 'web.views.create_analysis', name='create-analysis'),
    url(r'^analysis/open$', 'web.views.open_analysis', name='open-analysis'),
    url(r'^analysis/summary$', 'web.views.summary_analysis', name='summary-analysis'),
    url(r'^analysis/correlate$', 'web.views.correlate_analysis', name='correlate-analysis'),
    url(r'^analysis/model$', 'web.views.model_analysis', name='model-analysis'),
    url(r'^analysis/api$', 'web.api.views.api_analysis', name='api-analysis'),
    url(r'^datahub/browse$', 'web.views.browse_datahub', name='browse-datahub'),
    url(r'^datahub/show$', 'web.views.show_data', name='show-data'),
    url(r'^api$', 'web.api.views.api_general', name='api-general'),
)
