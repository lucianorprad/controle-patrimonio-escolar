from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class TipoBem(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "tipo_bem"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Setor(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "setor"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Localizacao(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "localizacao"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Bem(models.Model):
    class EstadoConservacao(models.TextChoices):
        OTIMO = "Ótimo", "Ótimo"
        BOM = "Bom", "Bom"
        REGULAR = "Regular", "Regular"
        RUIM = "Ruim", "Ruim"

    class Situacao(models.TextChoices):
        ATIVO = "Ativo", "Ativo"
        BAIXADO = "Baixado", "Baixado"

    id = models.AutoField(primary_key=True)
    codigo_patrimonio = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=255)
    estado_conservacao = models.CharField(max_length=7, choices=EstadoConservacao.choices)
    situacao = models.CharField(max_length=7, choices=Situacao.choices)
    data_aquisicao = models.DateField(null=True, blank=True)
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, db_column="setor_id")
    tipo_bem = models.ForeignKey(TipoBem, on_delete=models.PROTECT, db_column="tipo_bem_id")

    class Meta:
        db_table = "bem"
        ordering = ["codigo_patrimonio"]
        constraints = [
            models.CheckConstraint(condition=Q(valor__isnull=True) | Q(valor__gte=0), name="bem_valor_nao_negativo"),
        ]

    def __str__(self):
        return f"{self.codigo_patrimonio} - {self.descricao}"


class Movimentacao(models.Model):
    id = models.AutoField(primary_key=True)
    data_movimentacao = models.DateTimeField()
    observacao = models.CharField(max_length=255, null=True, blank=True)
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, db_column="setor_id")
    localizacao_origem = models.ForeignKey(
        Localizacao,
        on_delete=models.PROTECT,
        db_column="localizacao_origem_id",
        related_name="movimentacoes_origem",
    )
    localizacao_destino = models.ForeignKey(
        Localizacao,
        on_delete=models.PROTECT,
        db_column="localizacao_destino_id",
        related_name="movimentacoes_destino",
    )
    bem = models.ForeignKey(Bem, on_delete=models.PROTECT, db_column="bem_id")

    class Meta:
        db_table = "movimentacao"
        ordering = ["-data_movimentacao"]

    def __str__(self):
        return f"{self.bem} - {self.data_movimentacao}"
