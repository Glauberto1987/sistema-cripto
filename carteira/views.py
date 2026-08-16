from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Moeda, Transacao
import requests
import json  # Importante para enviar os dados para o gráfico Javascript

@login_required
def dashboard(request):
    moedas = Moeda.objects.all()
    patrimonio_investido = 0
    valor_atual_carteira = 0
    detalhes_moedas = [] 
    
    for moeda in moedas:
        compras = moeda.transacoes.filter(tipo_operacao='COMPRA')
        qtd_comprada = compras.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        total_gasto = compras.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        
        patrimonio_investido += total_gasto
        valor_atual_carteira += (qtd_comprada * moeda.preco_atual)
        
        if qtd_comprada > 0:
            preco_medio = total_gasto / qtd_comprada
            valor_atual_moeda = qtd_comprada * moeda.preco_atual
            lucro_moeda = valor_atual_moeda - total_gasto
            rentabilidade_moeda = (lucro_moeda / total_gasto) * 100 if total_gasto > 0 else 0
            
            detalhes_moedas.append({
                'id': moeda.id,
                'nome': moeda.nome,
                'simbolo': moeda.simbolo,
                'quantidade': qtd_comprada,
                'preco_medio': preco_medio,
                'preco_atual': moeda.preco_atual,
                'valor_atual': valor_atual_moeda,
                'lucro': lucro_moeda,
                'rentabilidade': rentabilidade_moeda
            })
            
    lucro_prejuizo_rs = valor_atual_carteira - patrimonio_investido
    rentabilidade = (lucro_prejuizo_rs / patrimonio_investido) * 100 if patrimonio_investido > 0 else 0

    # --- PREPARANDO DADOS PARA O GRÁFICO ---
    # Só pega as moedas que você realmente tem saldo
    nomes_grafico = [item['simbolo'] for item in detalhes_moedas if item['valor_atual'] > 0]
    valores_grafico = [float(item['valor_atual']) for item in detalhes_moedas if item['valor_atual'] > 0]

    contexto = {
        'patrimonio_investido': patrimonio_investido,
        'valor_atual_carteira': valor_atual_carteira,
        'lucro_prejuizo_rs': lucro_prejuizo_rs,
        'rentabilidade': rentabilidade,
        'detalhes_moedas': detalhes_moedas,
        'nomes_grafico': json.dumps(nomes_grafico),      # Convertido para o JavaScript ler
        'valores_grafico': json.dumps(valores_grafico),  # Convertido para o JavaScript ler
    }
    return render(request, 'index.html', contexto)

def detalhe_moeda(request, id):
    moeda = get_object_or_404(Moeda, id=id)
    compras = moeda.transacoes.filter(tipo_operacao='COMPRA')
    qtd_comprada = compras.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    total_gasto = compras.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    preco_medio = total_gasto / qtd_comprada if qtd_comprada > 0 else 0
    valor_atual = qtd_comprada * moeda.preco_atual
    lucro = valor_atual - total_gasto
    rentabilidade = (lucro / total_gasto) * 100 if total_gasto > 0 else 0
    
    simbolo_limpo = moeda.simbolo.strip().upper()
    excecoes_grafico = {
        'LUNC': 'BINANCE:LUNCUSDT',
        'BTTC': 'BINANCE:BTTCUSDT',
        'FLR': 'OKX:FLRUSDT',
    }
    
    if simbolo_limpo in excecoes_grafico:
        simbolo_grafico = excecoes_grafico[simbolo_limpo]
    else:
        simbolo_grafico = f"BINANCE:{simbolo_limpo}BRL"
        
    contexto = {
        'moeda': moeda, 'qtd_comprada': qtd_comprada, 'total_gasto': total_gasto,
        'preco_medio': preco_medio, 'valor_atual': valor_atual, 'lucro': lucro,
        'rentabilidade': rentabilidade, 'simbolo_grafico': simbolo_grafico,
        'transacoes': moeda.transacoes.all().order_by('-data')
    }
    return render(request, 'detalhe.html', contexto)

def atualizar_precos(request):
    ids_map = {
        'XRP': 'ripple', 'LUNC': 'terra-luna', 'XLM': 'stellar',
        'BTTC': 'bittorrent', 'ADA': 'cardano', 'FLR': 'flare-networks',
        'SHIB': 'shiba-inu', 'MATIC': 'polygon-ecosystem-token', 'POL': 'polygon-ecosystem-token'
    }
    moedas = Moeda.objects.all()
    ids_para_buscar = [ids_map[m.simbolo.strip().upper()] for m in moedas if m.simbolo.strip().upper() in ids_map]
            
    if ids_para_buscar:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids_para_buscar)}&vs_currencies=brl"
        try:
            dados = requests.get(url, timeout=10).json()
            for moeda in moedas:
                simbolo = moeda.simbolo.strip().upper()
                if simbolo in ids_map and ids_map[simbolo] in dados:
                    moeda.preco_atual = dados[ids_map[simbolo]]['brl']
                    moeda.save()
        except Exception as e:
            print(f"🚨 ERRO: {e}")
            
    return redirect('dashboard')