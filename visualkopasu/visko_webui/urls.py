from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    
    url(r'^search/$', views.search, name='search'),
    
    url(r'^biblioteche/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>[0-9]+)/$', views.doc_display, name='doc_display'),
    url(r'^biblioteche/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>[0-9]+)/(?P<sentence_id>[0-9]+)/$', views.dmrs_display, name='dmrs_display'),
    url(r'^biblioteche/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>[0-9]+)/(?P<sentence_id>[0-9]+)/(?P<interpretation_id>[0-9]+)$', views.dmrs_display, name='dmrs_display'),

    url(r'^search/(?P<collection_name>\w+)/(?P<search_id>[0-9]+)/$', views.dmrs_search_display, name='dmrs_search_display'),

    url(r'^original/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_name>\w+)/(?P<sentence_ident>[0-9]+)/$', views.original_display, name='original_display'),
    url(r'^original/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_name>\w+)/(?P<sentence_ident>[0-9]+)/(?P<interpretationID>[0-9]+)/$', views.original_display, name='original_display'),
    
    url(r'^basket/$', views.basket, name='basket'),

    url(r'^viz$', views.dev_viz, name='dev_viz'),
    url(r'^dev/$', views.dev_test, name='dev_test'),

    
    url(r'^coolisf/$', views.isf_parse, name='isf_parse'),
]
