from django.db import models
from django.utils import timezone

class Moeda(models.Model):
    nome = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=10)
    preco_atual = models.DecimalField(max_digits=20, decimal_places=10, default=0)

    def __str__(self):
        return self.simbolo

class Transacao(models.Model):
    TIPO_CHOICES = (
        ('COMPRA', 'Compra'),
        ('VENDA', 'Venda'),
    )
    moeda = models.ForeignKey(Moeda, on_delete=models.CASCADE, related_name='transacoes')
    tipo_operacao = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=20, decimal_places=10)
    valor_total = models.DecimalField(max_digits=20, decimal_places=10)
    data = models.DateTimeField(default=timezone.now)

    # NOVA MATEMÁTICA: Calcula o preço da unidade na hora da compra
    @property
    def preco_unitario(self):
        if self.quantidade > 0:
            return self.valor_total / self.quantidade
        return 0

    def __str__(self):
        return f"{self.tipo_operacao} - {self.moeda.simbolo}"