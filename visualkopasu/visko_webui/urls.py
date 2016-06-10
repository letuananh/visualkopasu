from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    
    url(r'^search/$', views.search, name='search'),
    
    url(r'^doc/(?P<doc_id>[0-9]+)/$', views.doc_display, name='doc_display'),
    
    url(r'^dmrs/(?P<sentence_id>[0-9]+)/$', views.dmrs_display, name='dmrs_display'),
    url(r'^dmrs/search/(?P<search_id>[0-9]+)/$', views.dmrs_search_display, name='dmrs_search_display'),
    
    url(r'^basket/$', views.basket, name='basket'),
    
    url(r'^original/(?P<document>\w+)/(?P<sentenceID>[0-9]+)/$', views.original_display, name='original_display'),
    url(r'^original/sentence/(?P<sentenceID>[0-9]+)/$', views.original_display, name='original_display'),
    url(r'^original/(?P<document>\w+)/(?P<sentenceID>[0-9]+)/(?P<interpretationID>[0-9]+)/$', views.original_display, name='original_display'),

    url(r'^coolisf/$', views.isf_parse, name='isf_parse'),
]
