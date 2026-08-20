from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib import messages
from .models import Moeda, Transacao, HistoricoPatrimonio
from datetime import date, datetime
import requests
import json

@login_required(login_url='/admin/')
def dashboard(request):
    moedas = Moeda.objects.all()
    patrimonio_investido = 0
    valor_atual_carteira = 0
    detalhes_moedas = [] 
    
    for moeda in moedas:
        compras = moeda.transacoes.filter(tipo_operacao='COMPRA')
        qtd_comprada = compras.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        total_gasto = compras.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        
        # Convertendo tudo para float para impedir conflitos de tipos na matematica
        qtd_float = float(qtd_comprada)
        preco_float = float(moeda.preco_atual)
        gasto_float = float(total_gasto)
        
        patrimonio_investido += gasto_float
        valor_atual_carteira += (qtd_float * preco_float)
        
        if qtd_float > 0:
            preco_medio = gasto_float / qtd_float
            valor_atual_moeda = qtd_float * preco_float
            lucro_moeda = valor_atual_moeda - gasto_float
            rentabilidade_moeda = (lucro_moeda / gasto_float) * 100 if gasto_float > 0 else 0
            
            detalhes_moedas.append({
                'id': moeda.id,
                'nome': moeda.nome,
                'simbolo': moeda.simbolo,
                'quantidade': qtd_float,
                'preco_medio': float(preco_medio),
                'preco_atual': preco_float,
                'valor_atual': float(valor_atual_moeda),
                'lucro': float(lucro_moeda),
                'rentabilidade': float(rentabilidade_moeda)
            })
            
    lucro_prejuizo_rs = float(valor_atual_carteira) - float(patrimonio_investido)
    rentabilidade = (lucro_prejuizo_rs / float(patrimonio_investido)) * 100 if float(patrimonio_investido) > 0 else 0

    nomes_grafico = [item['simbolo'] for item in detalhes_moedas if item['valor_atual'] > 0]
    valores_grafico = [float(item['valor_atual']) for item in detalhes_moedas if item['valor_atual'] > 0]

    hoje = date.today()

    if HistoricoPatrimonio.objects.count() <= 1:
        HistoricoPatrimonio.objects.all().delete()
        transacoes_ord = Transacao.objects.select_related('moeda').all().order_by('data')
        acumulado = 0
        for t in transacoes_ord:
            if t.tipo_operacao == 'COMPRA':
                acumulado += float(t.valor_total)
            elif t.tipo_operacao == 'VENDA':
                acumulado -= float(t.valor_total)
            
            d_val = t.data
            if isinstance(d_val, datetime):
                d_val = d_val.date()
            
            HistoricoPatrimonio.objects.update_or_create(
                data=d_val,
                defaults={'valor_total': round(acumulado, 2)}
            )

    HistoricoPatrimonio.objects.update_or_create(
        data=hoje,
        defaults={'valor_total': round(float(valor_atual_carteira), 2)}
    )

    historico = list(HistoricoPatrimonio.objects.all().order_by('-data')[:30])[::-1]
    
    datas_historico_list = []
    valores_historico_list = []
    tooltips_historico_list = []

    todas_transacoes = list(Transacao.objects.select_related('moeda').all())

    for h in historico:
        datas_historico_list.append(h.data.strftime('%d/%m'))
        valores_historico_list.append(float(h.valor_total))
        
        detalhes_dia = []
        for t in todas_transacoes:
            t_data = t.data.date() if isinstance(t.data, datetime) else t.data
            if t_data == h.data:
                if t.tipo_operacao == 'COMPRA':
                    detalhes_dia.append(f"🟢 Comprou {t.moeda.simbolo}")
                else:
                    detalhes_dia.append(f"🔴 Vendeu {t.moeda.simbolo}")
        
        if detalhes_dia:
            tooltips_historico_list.append(" | ".join(detalhes_dia))
        elif h.data == hoje:
            tooltips_historico_list.append("💰 Valor Atual")
        else:
            tooltips_historico_list.append("Sem transações")

    datas_historico = json.dumps(datas_historico_list)
    valores_historico = json.dumps(valores_historico_list)
    tooltips_historico = json.dumps(tooltips_historico_list)

    # --- NOVO: Cálculo do Desempenho do Dia Anterior ---
    historico_recente = HistoricoPatrimonio.objects.all().order_by('-data')[:2]
    lucro_dia_anterior = 0
    percentual_dia_anterior = 0
    
    if len(historico_recente) >= 2:
        valor_hoje = float(historico_recente[0].valor_total)
        valor_ontem = float(historico_recente[1].valor_total)
        
        lucro_dia_anterior = valor_hoje - valor_ontem
        if valor_ontem > 0:
            percentual_dia_anterior = (lucro_dia_anterior / valor_ontem) * 100
    # ---------------------------------------------------

    contexto = {
        'patrimonio_investido': float(patrimonio_investido),
        'valor_atual_carteira': float(valor_atual_carteira),
        'lucro_prejuizo_rs': float(lucro_prejuizo_rs),
        'rentabilidade': float(rentabilidade),
        'detalhes_moedas': detalhes_moedas,
        'nomes_grafico': json.dumps(nomes_grafico),
        'valores_grafico': json.dumps(valores_grafico),
        'datas_historico': datas_historico,
        'valores_historico': valores_historico,
        'tooltips_historico': tooltips_historico,
        'lucro_dia_anterior': lucro_dia_anterior,
        'percentual_dia_anterior': percentual_dia_anterior,
    }
    return render(request, 'index.html', contexto)

def detalhe_moeda(request, id):
    moeda = get_object_or_404(Moeda, id=id)
    compras = moeda.transacoes.filter(tipo_operacao='COMPRA')
    qtd_comprada = compras.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    total_gasto = compras.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    
    qtd_float = float(qtd_comprada)
    gasto_float = float(total_gasto)
    preco_float = float(moeda.preco_atual)
    
    preco_medio = gasto_float / qtd_float if qtd_float > 0 else 0
    valor_atual = qtd_float * preco_float
    lucro = valor_atual - gasto_float
    rentabilidade = (lucro / gasto_float) * 100 if gasto_float > 0 else 0
    
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
        'moeda': moeda, 'qtd_comprada': float(qtd_comprada), 'total_gasto': float(total_gasto),
        'preco_medio': float(preco_medio), 'valor_atual': float(valor_atual), 'lucro': float(lucro),
        'rentabilidade': float(rentabilidade), 'simbolo_grafico': simbolo_grafico,
        'transacoes': moeda.transacoes.all().order_by('-data')
    }
    return render(request, 'detalhe.html', contexto)

def atualizar_precos(request):
    try:
        try:
            dolar_req = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL', timeout=10).json()
            valor_dolar = float(dolar_req['USDBRL']['bid'])
        except Exception as e:
            messages.error(request, f"Falha ao buscar Dólar: {str(e)}")
            return redirect('dashboard')
            
        try:
            binance_req = requests.get('https://api.binance.com/api/v3/ticker/price', timeout=10).json()
            precos_binance = {item['symbol']: float(item['price']) for item in binance_req}
        except Exception as e:
            messages.error(request, f"Falha ao buscar Binance: {str(e)}")
            return redirect('dashboard')
            
        moedas = Moeda.objects.all()
        moedas_atualizadas = 0
        moedas_com_erro = []

        for moeda in moedas:
            try:
                sigla = moeda.simbolo.strip().upper()
                
                if sigla == 'POL': sigla = 'POL'
                if sigla == 'MATIC': sigla = 'POL'
                if sigla == 'BTT': sigla = 'BTTC'
                
                par = f"{sigla}USDT"
                
                if par in precos_binance:
                    preco_calculado = precos_binance[par] * valor_dolar
                    moeda.preco_atual = f"{preco_calculado:.8f}"
                    moeda.save()
                    moedas_atualizadas += 1
                else:
                    moedas_com_erro.append(sigla)
            except Exception as e:
                messages.error(request, f"Erro ao salvar moeda {moeda.simbolo}: {str(e)}")

        if moedas_atualizadas > 0:
            messages.success(request, f"Preços de {moedas_atualizadas} moedas atualizados com sucesso!")
        if moedas_com_erro:
            messages.warning(request, f"Moedas não encontradas na Binance: {', '.join(moedas_com_erro)}")
            
    except Exception as e:
        messages.error(request, f"Erro Crítico Geral: {str(e)}")
        
    return redirect('dashboard')