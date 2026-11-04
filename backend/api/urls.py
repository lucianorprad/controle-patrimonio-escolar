from django.urls import include, path
from rest_framework import routers
from .views import (
    BemViewSet,
    GroupViewSet,
    LocalizacaoViewSet,
    MovimentacaoViewSet,
    SetorViewSet,
    TipoBemViewSet,
    UserViewSet,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"tipos_bem", TipoBemViewSet)
router.register(r"setores", SetorViewSet)
router.register(r"localizacoes", LocalizacaoViewSet)
router.register(r"bens", BemViewSet)
router.register(r"movimentacoes", MovimentacaoViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]