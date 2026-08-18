def atualizar_precos(request):
    moedas = Moeda.objects.all()
    
    # Prepara as siglas (A Polygon mudou para POL, mas o mercado ainda usa MATIC nos bastidores)
    simbolos = []
    for m in moedas:
        s = m.simbolo.strip().upper()
        simbolos.append('MATIC' if s == 'POL' else s)
        
    if simbolos:
        # Puxando da CryptoCompare (livre de bloqueios em nuvem)
        url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms={','.join(simbolos)}&tsyms=BRL"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                dados = response.json()
                
                for moeda in moedas:
                    simbolo_banco = moeda.simbolo.strip().upper()
                    # Se for POL, dizemos ao sistema para ler o valor de MATIC
                    busca = 'MATIC' if simbolo_banco == 'POL' else simbolo_banco
                    
                    if busca in dados and 'BRL' in dados[busca]:
                        moeda.preco_atual = dados[busca]['BRL']
                        moeda.save()
                        
                messages.success(request, "Preços atualizados com sucesso!")
            else:
                messages.error(request, "Servidor de preços indisponível no momento.")
        except Exception as e:
            messages.error(request, "Falha de conexão com a API.")
            print(f"🚨 ERRO: {e}")
            
    return redirect('dashboard')