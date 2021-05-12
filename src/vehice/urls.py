"""vehice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page
from django_js_reverse.views import urls_js

admin.site.site_header = "Administración de datos"
admin.site.index_title = "VEHICE"
admin.site.site_title = "DATOS"

urlpatterns = [
    url(r"^jet/", include("jet.urls", "jet")),  # Django JET URLS
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    url(r"^admin/", admin.site.urls),
    url(r"^accounts/", include("accounts.urls")),
    url(r"^", include("app.urls")),
    url(r"^", include("backend.urls")),
    url(r"lab/", include("lab.urls")),
    url(r"report/", include("report.urls")),
    url("avatar/", include("avatar.urls")),
    url("review/", include("review.urls")),
    url(r"^jsreverse/$", urls_js, name="js_reverse"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
