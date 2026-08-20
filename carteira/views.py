def atualizar_precos(request):
    try:
        # 1. BUSCA O VALOR DO DÓLAR (COM PLANO B)
        try:
            valor_dolar = 0
            # Tentativa 1: AwesomeAPI
            req1 = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL', timeout=10)
            data1 = req1.json()
            
            if 'USDBRL' in data1:
                valor_dolar = float(data1['USDBRL']['bid'])
            else:
                # Tentativa 2: Exchangerate API (Fallback se a AwesomeAPI bloquear o Render)
                req2 = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
                data2 = req2.json()
                valor_dolar = float(data2['rates']['BRL'])
                
        except Exception as e:
            print(f"🔴 ERRO AO BUSCAR DÓLAR: {str(e)}")
            messages.error(request, f"Falha ao buscar cotação do Dólar: {str(e)}")
            return redirect('dashboard')
            
        # 2. BUSCA OS PREÇOS NA BINANCE
        try:
            binance_req = requests.get('https://api.binance.com/api/v3/ticker/price', timeout=10).json()
            # Se a Binance retornar erro, ela manda um dicionário com 'code' em vez de uma lista
            if isinstance(binance_req, dict) and 'code' in binance_req:
                raise Exception(binance_req.get('msg', 'Erro desconhecido da Binance'))
                
            precos_binance = {item['symbol']: float(item['price']) for item in binance_req}
        except Exception as e:
            print(f"🔴 ERRO NA BINANCE: {str(e)}")
            messages.error(request, f"Falha ao conectar com a Binance: {str(e)}")
            return redirect('dashboard')
            
        # 3. ATUALIZA AS MOEDAS NO BANCO
        moedas = Moeda.objects.all()
        moedas_atualizadas = 0
        moedas_com_erro = []

        for moeda in moedas:
            try:
                sigla = moeda.simbolo.strip().upper()
                
                # Ajustes de símbolos
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
                print(f"🔴 ERRO AO SALVAR MOEDA {moeda.simbolo}: {str(e)}")
                messages.error(request, f"Erro ao salvar moeda {moeda.simbolo}: {str(e)}")

        if moedas_atualizadas > 0:
            messages.success(request, f"Preços de {moedas_atualizadas} moedas atualizados com sucesso!")
        if moedas_com_erro:
            messages.warning(request, f"Moedas não encontradas na Binance: {', '.join(moedas_com_erro)}")
            
    except Exception as e:
        print(f"🔴 ERRO CRÍTICO GERAL: {str(e)}")
        messages.error(request, f"Erro Crítico Geral: {str(e)}")
        
  def atualizar_precos(request):
    try:
        # 1. BUSCA O VALOR DO DÓLAR (COM PLANO B)
        try:
            valor_dolar = 0
            # Tentativa 1: AwesomeAPI
            req1 = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL', timeout=10)
            data1 = req1.json()
            
            if 'USDBRL' in data1:
                valor_dolar = float(data1['USDBRL']['bid'])
            else:
                # Tentativa 2: Exchangerate API (Fallback se a AwesomeAPI bloquear o Render)
                req2 = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
                data2 = req2.json()
                valor_dolar = float(data2['rates']['BRL'])
                
        except Exception as e:
            print(f"🔴 ERRO AO BUSCAR DÓLAR: {str(e)}")
            messages.error(request, f"Falha ao buscar cotação do Dólar: {str(e)}")
            return redirect('dashboard')
            
        # 2. BUSCA OS PREÇOS NA BINANCE
        try:
            binance_req = requests.get('https://api.binance.com/api/v3/ticker/price', timeout=10).json()
            # Se a Binance retornar erro, ela manda um dicionário com 'code' em vez de uma lista
            if isinstance(binance_req, dict) and 'code' in binance_req:
                raise Exception(binance_req.get('msg', 'Erro desconhecido da Binance'))
                
            precos_binance = {item['symbol']: float(item['price']) for item in binance_req}
        except Exception as e:
            print(f"🔴 ERRO NA BINANCE: {str(e)}")
            messages.error(request, f"Falha ao conectar com a Binance: {str(e)}")
            return redirect('dashboard')
            
        # 3. ATUALIZA AS MOEDAS NO BANCO
        moedas = Moeda.objects.all()
        moedas_atualizadas = 0
        moedas_com_erro = []

        for moeda in moedas:
            try:
                sigla = moeda.simbolo.strip().upper()
                
                # Ajustes de símbolos
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
                print(f"🔴 ERRO AO SALVAR MOEDA {moeda.simbolo}: {str(e)}")
                messages.error(request, f"Erro ao salvar moeda {moeda.simbolo}: {str(e)}")

        if moedas_atualizadas > 0:
            messages.success(request, f"Preços de {moedas_atualizadas} moedas atualizados com sucesso!")
        if moedas_com_erro:
            messages.warning(request, f"Moedas não encontradas na Binance: {', '.join(moedas_com_erro)}")
            
    except Exception as e:
        print(f"🔴 ERRO CRÍTICO GERAL: {str(e)}")
        messages.error(request, f"Erro Crítico Geral: {str(e)}")
        
    return redirect('dashboard')