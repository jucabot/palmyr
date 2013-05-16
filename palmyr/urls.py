from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'search.views.search', name='home'),
    # url(r'^palmyr/', include('palmyr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^accounts/logout_then_login', 'django.contrib.auth.views.logout_then_login',name="logout"),
    
    url(r'^datasource/browse$', 'analyze.views.browse_datasource', name='browse-datasource'),
    url(r'^datasource/upload$', 'analyze.views.upload_file', name='upload-datasource'),
    
    url(r'^analysis/browse$', 'analyze.views.browse_analysis', name='browse-analysis'),
    url(r'^analysis/create$', 'analyze.views.create_analysis', name='create-analysis'),
    url(r'^analysis/open$', 'analyze.views.open_analysis', name='open-analysis'),
    url(r'^analysis/summary$', 'analyze.views.summary_analysis', name='summary-analysis'),
    url(r'^analysis/correlate$', 'analyze.views.correlate_analysis', name='correlate-analysis'),
    
    url(r'^api$', 'common.views.api', name='api'),
    url(r'^api/analysis$', 'analyze.views.api', name='analysis-api'),
    
    url(r'^search$', 'search.views.search', name='search'),
    url(r'^api/search$', 'search.views.api', name='search-api'),
)
