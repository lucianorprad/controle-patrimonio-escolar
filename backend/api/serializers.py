from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .models import Bem, Localizacao, Movimentacao, Setor, TipoBem


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class TipoBemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoBem
        fields = ["id", "nome", "descricao"]


class SetorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setor
        fields = ["id", "nome", "descricao"]


class LocalizacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localizacao
        fields = ["id", "nome", "descricao"]


class BemSerializer(serializers.ModelSerializer):
    tipo_bem_nome = serializers.CharField(source="tipo_bem.nome", read_only=True)
    setor_nome = serializers.CharField(source="setor.nome", read_only=True)

    class Meta:
        model = Bem
        fields = [
            "id",
            "codigo_patrimonio",
            "descricao",
            "estado_conservacao",
            "situacao",
            "data_aquisicao",
            "valor",
            "setor",
            "setor_nome",
            "tipo_bem",
            "tipo_bem_nome",
        ]


class MovimentacaoSerializer(serializers.ModelSerializer):
    bem_codigo_patrimonio = serializers.CharField(source="bem.codigo_patrimonio", read_only=True)
    localizacao_origem_nome = serializers.CharField(source="localizacao_origem.nome", read_only=True)
    localizacao_destino_nome = serializers.CharField(source="localizacao_destino.nome", read_only=True)
    setor_nome = serializers.CharField(source="setor.nome", read_only=True)

    class Meta:
        model = Movimentacao
        fields = [
            "id",
            "data_movimentacao",
            "observacao",
            "setor",
            "setor_nome",
            "localizacao_origem",
            "localizacao_origem_nome",
            "localizacao_destino",
            "localizacao_destino_nome",
            "bem",
            "bem_codigo_patrimonio",
        ]
