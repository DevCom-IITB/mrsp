from django.urls import path

import portal.views
import oauth.views
import admin2.views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', portal.views.index, name='index'),
    path('login/', portal.views.login, name='login'),
    path('rules/', portal.views.rules, name='rules'),
    path('apply/', portal.views.apply, name='apply'),
    path('thanks/', portal.views.thanks, name='thanks'),
    path('edit_docs/', portal.views.edit_docs, name='edit_docs'),

    path('oauth/login/', oauth.views.oauth, name='oauth'),
    path('oauth/callback/', oauth.views.login_client, name='login_client'),
    path('oauth/logout/', oauth.views.logout_client, name='logout_client'),

    path('mock_login', oauth.views.mock_login, name='mock_login'),

    path('admin/acad', admin2.views.acad_admin, name='admin_acad'),
    path('admin/acad/details', admin2.views.acad_details, name='admin_acad_details'),

    path('admin/hcu', admin2.views.hcu_admin, name='admin_hcu'),
    path('admin/hcu/details', admin2.views.hcu_details, name='admin_hcu_details'),

    path('admin/file', admin2.views.view_file, name='admin_view_file')
]
