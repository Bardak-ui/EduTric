"""
URL configuration for EduTric project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"

urlpatterns = [
    path("", RedirectView.as_view(url="/accounts/register/", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.Accounts.urls")),
    path('journal/', include('apps.Journal.urls', namespace='journal')),
    path("profile/", include("apps.Profile.urls")),
    path("shedule/", include("apps.Shedule.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
