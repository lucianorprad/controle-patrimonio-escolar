from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from .models import Bem, Localizacao, Movimentacao, Setor, TipoBem
from .serializers import (
    BemSerializer,
    GroupSerializer,
    LocalizacaoSerializer,
    MovimentacaoSerializer,
    SetorSerializer,
    TipoBemSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]


class TipoBemViewSet(viewsets.ModelViewSet):
    queryset = TipoBem.objects.all()
    serializer_class = TipoBemSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class SetorViewSet(viewsets.ModelViewSet):
    queryset = Setor.objects.all()
    serializer_class = SetorSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class LocalizacaoViewSet(viewsets.ModelViewSet):
    queryset = Localizacao.objects.all()
    serializer_class = LocalizacaoSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class BemViewSet(viewsets.ModelViewSet):
    queryset = Bem.objects.select_related("setor", "tipo_bem").all()
    serializer_class = BemSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class MovimentacaoViewSet(viewsets.ModelViewSet):
    queryset = Movimentacao.objects.select_related(
        "bem",
        "setor",
        "localizacao_origem",
        "localizacao_destino",
    ).all()
    serializer_class = MovimentacaoSerializer
    permission_classes = [permissions.DjangoModelPermissions]
