from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

import portal.views
import oauth.views
import admin2.views

urlpatterns = [
    path('mrsp/admin/super', admin.site.urls),
    path('mrsp/', portal.views.index, name='index'),
    path('mrsp/login/', portal.views.login, name='login'),
    path('mrsp/rules/', portal.views.rules, name='rules'),
    path('mrsp/apply/', portal.views.apply, name='apply'),
    path('mrsp/thanks/', portal.views.thanks, name='thanks'),
    path('mrsp/edit_docs/', portal.views.edit_docs, name='edit_docs'),
    path('mrsp/waitlist/', portal.views.waitlist, name = 'waitlist'),

    path('mrsp/oauth/login/', oauth.views.oauth, name='oauth'),
    path('mrsp/oauth/callback/', oauth.views.login_client, name='login_client'),
    path('mrsp/oauth/logout/', oauth.views.logout_client, name='logout_client'),

    path('mrsp/mock_login', oauth.views.mock_login, name='mock_login'),

    path('mrsp/admin/acad', admin2.views.acad_admin, name='admin_acad'),
    path('mrsp/admin/acad/details', admin2.views.acad_details, name='admin_acad_details'),

    path('mrsp/admin/hcu', admin2.views.hcu_admin, name='admin_hcu'),
    path('mrsp/admin/hcu/details', admin2.views.hcu_details, name='admin_hcu_details'),

    path('mrsp/admin/file', admin2.views.view_file, name='admin_view_file')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)