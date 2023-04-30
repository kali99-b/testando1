import requests
import json
import time
import hmac
import hashlib
from urllib.parse import urlencode
import datetime

# Configurações da API
API_KEY = '717ebc8ce149e48acc10ef7777051d612107c3c67bc0d1e6c0cb08a519d9df52'
SECRET_KEY = 'f02fa5415ecc007974d591526ce1382490e35f9944a5dce6a47eb90a3a688630'
ENDPOINT = 'https://testnet.binancefuture.com/fapi/v1/klines'

# Par de moedas e intervalo de tempo do candle
SYMBOL = 'ETHUSDT'
INTERVAL = '5m'

# =========================================================================================================================
while True:
    now = datetime.datetime.now()
    if now.hour == 13 and now.minute == 48:
        # Parâmetros de solicitação da API
        payload = {
            'symbol': SYMBOL,
            'interval': INTERVAL,
            'limit':  1  # Obter apenas o candle atual
        }
    # Autenticação com a chave de API e solicitação de informações do candle atual
        headers = {
            'X-MBX-APIKEY': API_KEY
        }
        response = requests.get(ENDPOINT, params=payload, headers=headers)
        data = json.loads(response.text)

#       para o colocamento das ordens
        tempo_limite = 3600  # limite de tempo em segundos
        tempo_inicio = time.time()

        maxima = float(data[0][2])
        high_price = float("{:.2f}".format(maxima))
        minima = float(data[0][3])
        low_price = float("{:.2f}".format(minima-0.01))
        preco_de_compra = float(data[0][2])
        preco_de_venda = float(data[0][3])

        preco_atual = float(data[0][4])
        # stops  e  takes
        n0 = float(maxima+(maxima-low_price))
        take_compra = float("{:.2f}".format(n0))
        n1 = float(minima-(high_price - minima))
        take_venda = float("{:.2f}".format(n1))

        maxima1 = float(maxima-minima)
        calculo1 = float(0.002 * 100 / maxima1)
        quantidade1 = float("{:.2f}".format(calculo1))
        minima2 = float(maxima-minima)
        calculo2 = float(0.004 * 100 / minima2)
        quantidade2 = float("{:.2f}".format(calculo2))

        print('take_compra =', take_compra)
        print('take_venda =', take_venda)
        print(' preco_atual', preco_atual)

# ========================================================================================================================
    # Adicionando uma ordem de stop market de compra na máxima do candle
        while True:
            try:
                if maxima1:
                    if maxima1 > 500:
                        print('OPERAÇÕES CANCELADAS RISCO MAIOR QUE 5 USDT')
                        break
                    print('hoje esta bom menos de 5 usdt de risco')
                tempo_atual = time.time()  # obtém o tempo atual
                if tempo_atual - tempo_inicio > tempo_limite:
                    if tempo_limite == 3600:  # tempo em segundo
                        print(
                            "Limite de tempo para ordem de compra atingido. Saindo do loop.")
                        print("ordes nao foram colocadas")
                        break
                buy_order_payload_1 = {
                    'symbol': SYMBOL,
                    'side': 'BUY',
                    'type': 'STOP_MARKET',
                    'stopPrice': high_price,
                    'quantity': quantidade1,
                    'recvWindow': 5000,
                    'timestamp': int(time.time() * 1000)
                }
                signature_1 = hmac.new(SECRET_KEY.encode(), urlencode(
                    buy_order_payload_1).encode(), hashlib.sha256).hexdigest()
                buy_order_payload_1['signature'] = signature_1
                buy_order_response_1 = requests.post(
                    'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_payload_1)
                if buy_order_response_1.status_code == 200:
                    print("Ordem de compra bem-sucedida!", high_price)

                    while True:
                        tempo_atual = time.time()  # obtém o tempo atual
                        if tempo_atual - tempo_inicio > tempo_limite:
                            if tempo_limite == 3600:  # tempo em segundo
                                print(
                                    "Limite de tempo para ordem de venda atingido. Saindo do loop.")
                                order_id = buy_order_response_1.json()[
                                    'orderId']

                                cancel_order_payload_1 = {
                                    'symbol': SYMBOL,
                                    'orderId': order_id,
                                    'recvWindow': 5000,
                                    'timestamp': int(time.time() * 1000)
                                }
                                signature_a = hmac.new(SECRET_KEY.encode(), urlencode(
                                    cancel_order_payload_1).encode(), hashlib.sha256).hexdigest()
                                cancel_order_payload_1['signature'] = signature_a
                                cancel_order_response_1 = requests.delete(
                                    'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=cancel_order_payload_1)
                                break
                        sell_order_payload_2 = {
                            'symbol': SYMBOL,
                            'side': 'SELL',
                            'type': 'STOP_MARKET',
                            'stopPrice': low_price,
                            'quantity': quantidade1,
                            'recvWindow': 5000,
                            'timestamp': int(time.time() * 1000)
                        }
                        signature2 = hmac.new(SECRET_KEY.encode(), urlencode(
                            sell_order_payload_2).encode(), hashlib.sha256).hexdigest()
                        sell_order_payload_2['signature'] = signature2
                        sell_order_response_2 = requests.post(
                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_payload_2)
                        if sell_order_response_2.status_code == 200:
                            print("Ordem de venda bem-sucedida!", low_price)
                            print(" volume nas Ordens quantidade1 !", quantidade1)
# =========================================================================================================================
                            # COLOCAMENTOS DOS STOPS TAKE E LOSS
                            while True:
                                try:
                                    now = datetime.datetime.now()
                                    if now.hour == 7:
                                        params = {
                                            'symbol': SYMBOL,
                                            'timestamp': int(time.time() * 1000),
                                            'recvWindow': 5000
                                        }
                                        signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                            params).encode(), hashlib.sha256).hexdigest()
                                        params['signature'] = signature
                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                        response = requests.delete(
                                            'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                        print('ORDENS ABERTAS CANCELADAS',
                                              response.json(), '\nTEMPO ESGOTADO NENHUMA ORDEM FOI PREENCHIDA')
                                        break

                                    buy_order_status_payload_1 = {
                                        'symbol': SYMBOL,
                                        'orderId': buy_order_response_1.json()['orderId'],
                                        'timestamp': int(time.time() * 1000),
                                        'recvWindow': 5000
                                    }
                                    signature_1 = hmac.new(SECRET_KEY.encode(), urlencode(
                                        buy_order_status_payload_1).encode(), hashlib.sha256).hexdigest()
                                    buy_order_status_payload_1['signature'] = signature_1
                                    buy_order_status_response_1 = requests.get(
                                        'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_status_payload_1)
                                    if buy_order_status_response_1.json()['status'] == 'FILLED':
                                        print('Ordem de compra executada:',
                                              buy_order_status_response_1.json())
                                        print(
                                            'ORDEN DE COMPRA PREENCHIDA\nADICIONANDO STOP LOSS E TAKE PROFIT')
# =========================================================================================================================
                                    # Adicionando ordem de stop loss
                                        sell_order_payload_A = {
                                            'symbol': SYMBOL,
                                            'side': 'SELL',
                                            'type': 'STOP_MARKET',
                                            'stopPrice': low_price,
                                            'quantity': quantidade2,
                                            'recvWindow': 5000,
                                            'timestamp': int(time.time() * 1000)
                                        }
                                        signature_A = hmac.new(SECRET_KEY.encode(), urlencode(
                                            sell_order_payload_A).encode(), hashlib.sha256).hexdigest()
                                        sell_order_payload_A['signature'] = signature_A
                                        sell_order_response_A = requests.post(
                                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_payload_A)
#                                   Adicionando uma ordem para take profit de compra
                                        sell_order_payload_a = {
                                            'symbol': SYMBOL,
                                            'side': 'SELL',
                                            'type': 'LIMIT',
                                            'timeInForce': 'GTC',
                                            'quantity': quantidade1,
                                            'price': take_compra,  # preço definido para a venda
                                            'recvWindow': 5000,
                                            'timestamp': int(time.time() * 1000)
                                        }
                                        signature_a = hmac.new(SECRET_KEY.encode(), urlencode(
                                            sell_order_payload_a).encode(), hashlib.sha256).hexdigest()
                                        sell_order_payload_a['signature'] = signature_a
                                        sell_order_response_a = requests.post(
                                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_payload_a)
                                        print('Nova ordem de venda criada:')
                                        print('stop loss =', low_price,
                                              '=', quantidade2+quantidade1)
                                        print('Nova ordem de venda criada:')
                                        print('take profit =', take_compra)
                                        break  # interrompe o loop se a ordem for executada
                                    else:
                                        print("\033c")
                                        print(
                                            'Ordem de compra ainda não executada =', high_price)
# =========================================================================================================================
                                # Verificar status da ordem de venda
                                    sell_order_status_payload_2 = {
                                        'symbol': SYMBOL,
                                        'orderId': sell_order_response_2.json()['orderId'],
                                        'timestamp': int(time.time() * 1000),
                                        'recvWindow': 5000
                                    }
                                    signature2 = hmac.new(SECRET_KEY.encode(), urlencode(
                                        sell_order_status_payload_2).encode(), hashlib.sha256).hexdigest()
                                    sell_order_status_payload_2['signature'] = signature2
                                    sell_order_status_response_2 = requests.get(
                                        'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_status_payload_2)
                                    order_id2 = sell_order_response_2.json()[
                                        'orderId']
                                    if sell_order_status_response_2.json()['status'] == 'FILLED':
                                        print('Ordem de venda executada:',
                                              sell_order_status_response_2.json())
                                        print(
                                            'ORDEM DE VENDA ACIONADA\nADICIONANDO STOP LOSS E TAKE PROFIT')
# =========================================================================================================================
                                    # Adicionando uma ordem de stop loss de compra stop
                                        buy_order_payload_B = {
                                            'symbol': SYMBOL,
                                            'side': 'BUY',
                                            'type': 'STOP_MARKET',
                                            'stopPrice': high_price,
                                            'quantity': quantidade2,
                                            'recvWindow': 5000,
                                            'timestamp': int(time.time() * 1000)
                                        }
                                        signature_B = hmac.new(SECRET_KEY.encode(), urlencode(
                                            buy_order_payload_B).encode(), hashlib.sha256).hexdigest()
                                        buy_order_payload_B['signature'] = signature_B
                                        buy_order_response_B = requests.post(
                                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_payload_B)
                                    #  Adicionando uma ordem take prfit para venda
                                        buy_order_payload_b = {
                                            'symbol': SYMBOL,
                                            'side': 'BUY',
                                            'type': 'LIMIT',
                                            'timeInForce': 'GTC',
                                            'quantity': quantidade1,
                                            'price': take_venda,  # preço definido para a compra take
                                            'recvWindow': 5000,
                                            'timestamp': int(time.time() * 1000)
                                        }
                                        signature_b = hmac.new(SECRET_KEY.encode(), urlencode(
                                            buy_order_payload_b).encode(), hashlib.sha256).hexdigest()
                                        buy_order_payload_b['signature'] = signature_b
                                        buy_order_response_b = requests.post(
                                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_payload_b)

                                        print('Nova ordem de compra criada:')
                                        print('stop loss = ', high_price,
                                              '=', quantidade2+quantidade1)
                                        print('Nova ordem de compra criada:')
                                        print('take profit =', take_venda)
                                        break  # interrompe o loop se a ordem for executada
                                    else:
                                        print(
                                            'Ordem de venda ainda não executada =', low_price)

                                except ValueError as e:
                                    # Lidar com exceções do tipo ValueError
                                    print("Uma exceção ValueError ocorreu:", e)
                                except Exception as e:
                                    print(
                                        "Uma exceção ocorreu, mas não é um ValueError:", e)
                                time.sleep(10)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                             INICIO DO NOVO LOOP ORDENS  TAKE PROFIT E ACIONAMENTO DE STOPS
                            if buy_order_status_response_1.json()['status'] == 'FILLED':
                                while True:
                                    try:
                                        now = datetime.datetime.now()
                                        if now.hour == 7:
                                            print(
                                                'NEM TAKE PROFIT NEM STOP LOSS DE COMPRA FORAM ACIONADOS \nTENPO ESGOTADO')
                                            sell_order_payload = {
                                                'symbol': SYMBOL,
                                                'side': 'SELL',
                                                'type': 'MARKET',
                                                'quantity': quantidade1,
                                                'recvWindow': 5000,
                                                'timestamp': int(time.time() * 1000)
                                            }
                                            signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                sell_order_payload).encode(), hashlib.sha256).hexdigest()
                                            sell_order_payload['signature'] = signature
                                            sell_order_response = requests.post(
                                                'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_payload)

                                            if sell_order_response.status_code == 200:
                                                print(
                                                    'POSIÇAO ZERADA COM SUCESSO')
                                            else:
                                                print(
                                                    'Erro ao executar ZERAGEM a mercado')
                                            params = {
                                                'symbol': SYMBOL,
                                                'timestamp': int(time.time() * 1000),
                                                'recvWindow': 5000
                                            }
                                            signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                params).encode(), hashlib.sha256).hexdigest()
                                            params['signature'] = signature
                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                            response = requests.delete(
                                                'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                            print('ORDENS ABERTAS CANCELADAS',
                                                  response.json())
                                            break
# **************************************************************************************************************************************************
                                        response = requests.get(
                                            ENDPOINT, params=payload, headers=headers)
                                        data = json.loads(response.text)
                                        nova_maxima = float(data[0][2])
                                        preco_atual1 = float(data[0][4])

                                        if nova_maxima > maxima:
                                            maxima = nova_maxima
                                            high_price = "{:.2f}".format(
                                                maxima)

                                        n11 = float(minima-(maxima - minima))
                                        take_venda1 = float(
                                            "{:.2f}".format(n11))

                                    # TAKE PROFIT ACINADO FECHA TODAS AS ORDENS ABERTAS
                                        sell_order_status_payload_a = {
                                            'symbol': SYMBOL,
                                            'orderId': sell_order_response_a.json()['orderId'],
                                            'timestamp': int(time.time() * 1000),
                                            'recvWindow': 5000
                                        }
                                        signature_a = hmac.new(SECRET_KEY.encode(), urlencode(
                                            sell_order_status_payload_a).encode(), hashlib.sha256).hexdigest()
                                        sell_order_status_payload_a['signature'] = signature_a
                                        sell_order_status_response_a = requests.get(
                                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_status_payload_a)

                                        if sell_order_status_response_a.json()['status'] == 'FILLED':
                                            print('Ordem de compra executada:',
                                                  sell_order_status_response_a.json())
                                            print(
                                                'ORDEN DE VENDA TAKE PROFIT == a == PREENCHIDA\nENCERRANDO OPERAÇÕES....')
                                            params = {
                                                'symbol': SYMBOL,
                                                'timestamp': int(time.time() * 1000),
                                                'recvWindow': 5000
                                            }
                                            signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                params).encode(), hashlib.sha256).hexdigest()
                                            params['signature'] = signature
                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                            response = requests.delete(
                                                'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                            print('ORDENS ABERTAS CANCELADAS',
                                                  response.json())
                                            print(
                                                'DIA DE LUCRO TAKE PROFIT == a ==')
                                            print('\nFIM DA EXECUÇÃO')
                                            break
                                        else:
                                            print("\033c")
                                            print(
                                                'TAKE PROFIT DE COMPRA NÂO PREENCHIDO', take_compra, ' quantidade =', quantidade1)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
                #                   SE ORDEM STOP FOR ACINOADA
                                        sell_order_status_payload_A = {
                                            'symbol': SYMBOL,
                                            'orderId': sell_order_response_A.json()['orderId'],
                                            'timestamp': int(time.time() * 1000),
                                            'recvWindow': 5000
                                        }
                                        signature_A = hmac.new(SECRET_KEY.encode(), urlencode(
                                            sell_order_status_payload_A).encode(), hashlib.sha256).hexdigest()
                                        sell_order_status_payload_A['signature'] = signature_A
                                        sell_order_status_response_A = requests.get(
                                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_status_payload_A)

                                        if sell_order_status_response_A.json()['status'] == 'FILLED':
                                            print('STOP LOSS DE COMPRA PREENCHIDO:',
                                                  sell_order_status_response_A.json())
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                   CANSELA A ORDEM TAKE DE COMPRA SE FOR STOPADO
                                            order_id = sell_order_response_a.json()[
                                                'orderId']
                                            cancel_order_payload_a = {
                                                'symbol': SYMBOL,
                                                'orderId': order_id,
                                                'recvWindow': 5000,
                                                'timestamp': int(time.time() * 1000)
                                            }
                                            signature_a = hmac.new(SECRET_KEY.encode(), urlencode(
                                                cancel_order_payload_a).encode(), hashlib.sha256).hexdigest()
                                            cancel_order_payload_a['signature'] = signature_a
                                            cancel_order_response_a = requests.delete(
                                                'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=cancel_order_payload_a)
                                        # Verificar se a ordem foi cancelada com sucesso
                                            if cancel_order_response_a.json()['status'] == 'CANCELED':
                                                print(
                                                    f"TAKE PROFIT CANCELADO :ID:{order_id}", take_compra)
                                                print(
                                                    'STOP LOSS FOI ACIONADO', low_price)
                                                print('')
                                                print(
                                                    'ACRESCENTANDO NOVAS ORDENS == C ==')
# **************************************************************************************************************************************
   #                                    ACRESCENTA NOVAS ORDENS STOP LOSS E TAKE PROFIT
#                                       Adicionando uma ordem de STOP LOSS de compra CASO SEJA STOPADO
                                                buy_order_payload_C = {
                                                    'symbol': SYMBOL,
                                                    'side': 'BUY',
                                                    'type': 'STOP_MARKET',
                                                    'stopPrice': high_price,
                                                    'quantity': quantidade2,
                                                    'recvWindow': 5000,
                                                    'timestamp': int(time.time() * 1000)
                                                }
                                                signature_C = hmac.new(SECRET_KEY.encode(), urlencode(
                                                    buy_order_payload_C).encode(), hashlib.sha256).hexdigest()
                                                buy_order_payload_C['signature'] = signature_C
                                                buy_order_response_C = requests.post(
                                                    'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_payload_C)
# =========================================================================================================================
#                                       Adicionando uma ordem TAKE PROFIT de compra alvo2
                                                buy_order_payload_c = {
                                                    'symbol': SYMBOL,
                                                    'side': 'BUY',
                                                    'type': 'LIMIT',
                                                    'timeInForce': 'GTC',
                                                    'quantity': quantidade2,
                                                    'price': take_venda1,  # preço definido para a compra take
                                                    'recvWindow': 5000,
                                                    'timestamp': int(time.time() * 1000)
                                                }
                                                signature_c = hmac.new(SECRET_KEY.encode(), urlencode(
                                                    buy_order_payload_c).encode(), hashlib.sha256).hexdigest()
                                                buy_order_payload_c['signature'] = signature_c
                                                buy_order_response_c = requests.post(
                                                    'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_payload_c)
                                                print(
                                                    'Nova ordem de compra criada:')
                                                print('STOP LOSS = ',
                                                      high_price, '=', quantidade2)
                                                print(
                                                    'Nova ordem de compra criada:')
                                                print('TAKE PROFIT =',
                                                      take_venda, '=', quantidade2)
# ---------------------------------------------------------------------------------------------------------------------------------------------------------
#                                       MONITORA AS NOVAS ORDENS TAKE E STOP LOSS SE FOR STOPADO
                                                while True:
                                                    try:
                                                        now = datetime.datetime.now()
                                                        if now.hour == 7:
                                                            print(
                                                                'TENPO ESGOTADO')
                                                            buy_order_payload = {
                                                                'symbol': SYMBOL,
                                                                'side': 'BUY',
                                                                'type': 'MARKET',
                                                                'quantity': quantidade2,
                                                                'recvWindow': 5000,
                                                                'timestamp': int(time.time() * 1000)
                                                            }
                                                            signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                buy_order_payload).encode(), hashlib.sha256).hexdigest()
                                                            buy_order_payload['signature'] = signature
                                                            buy_order_response = requests.post(
                                                                'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_payload)

                                                            if buy_order_response.status_code == 200:
                                                                print(
                                                                    'POSIÇAO ZERADA COM SUCESSO')
                                                            else:
                                                                print(
                                                                    'Erro ao executar ZERAGEM a mercado')
                                                            params = {
                                                                'symbol': SYMBOL,
                                                                'timestamp': int(time.time() * 1000),
                                                                'recvWindow': 5000
                                                            }
                                                            signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                params).encode(), hashlib.sha256).hexdigest()
                                                            params['signature'] = signature
                                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                                            response = requests.delete(
                                                                'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                                            print('ORDENS ABERTAS CANCELADAS',
                                                                  response.json())
                                                            print(
                                                                'ORDENS ABERTAS CANCELADAS')
                                                            break

                                                        buy_order_status_payload_C = {
                                                            'symbol': SYMBOL,
                                                            'orderId': buy_order_response_C.json()['orderId'],
                                                            'timestamp': int(time.time() * 1000),
                                                            'recvWindow': 5000
                                                        }
                                                        signature_C = hmac.new(SECRET_KEY.encode(), urlencode(
                                                            buy_order_status_payload_C).encode(), hashlib.sha256).hexdigest()
                                                        buy_order_status_payload_C['signature'] = signature_C
                                                        buy_order_status_response_C = requests.get(
                                                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_status_payload_C)

                                                        if buy_order_status_response_C.json()['status'] == 'FILLED':
                                                            print('Ordem de compra executada:',
                                                                  buy_order_status_response_C.json())

                                                            params = {
                                                                'symbol': SYMBOL,
                                                                'timestamp': int(time.time() * 1000),
                                                                'recvWindow': 5000
                                                            }
                                                            signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                params).encode(), hashlib.sha256).hexdigest()
                                                            params['signature'] = signature
                                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                                            response = requests.delete(
                                                                'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                                            print('ORDENS ABERTAS CANCELADAS',
                                                                  response.json())
                                                            print(
                                                                'Dia de loss == C+ ==')
                                                            print(
                                                                '\nFIM DA EXECUÇÃO')
                                                            break
                                                        else:
                                                            print("\033c")
                                                            print(
                                                                'stop loss == C+ == nao preenchido', high_price, 'quantidade =', quantidade2)
# ---------------------------------------------------------------------------------------------------------------------------------------------------------
                                                        buy_order_status_payload_c = {
                                                            'symbol': SYMBOL,
                                                            'orderId': buy_order_response_c.json()['orderId'],
                                                            'timestamp': int(time.time() * 1000),
                                                            'recvWindow': 5000
                                                        }
                                                        signature_c = hmac.new(SECRET_KEY.encode(), urlencode(
                                                            buy_order_status_payload_c).encode(), hashlib.sha256).hexdigest()
                                                        buy_order_status_payload_c['signature'] = signature_c
                                                        buy_order_status_response_c = requests.get(
                                                            'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_status_payload_c)

                                                        if buy_order_status_response_c.json()['status'] == 'FILLED':
                                                            print('Ordem de compra executada:',
                                                                  buy_order_status_response_c.json())
                                                            print(
                                                                'dia de lucro == c ==')

                                                            params = {
                                                                'symbol': SYMBOL,
                                                                'timestamp': int(time.time() * 1000),
                                                                'recvWindow': 5000
                                                            }
                                                            signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                params).encode(), hashlib.sha256).hexdigest()
                                                            params['signature'] = signature
                                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                                            response = requests.delete(
                                                                'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                                            print('ORDENS ABERTAS CANCELADAS',
                                                                  response.json())
                                                            print(
                                                                '\nFIM DA EXECUÇÃO')
                                                            break
                                                        else:
                                                            print(
                                                                'take profit == c< == nao preenchido', take_venda1, 'quantidade =', quantidade2)
                                                            print(
                                                                'preco_atual', preco_atual1)

                                                    except ValueError as e:
                                                        print(
                                                            "Uma exceção ValueError ocorreu:", e)
                                                    except Exception as e:
                                                        print(
                                                            "Uma exceção ocorreu, mas não é um ValueError:", e)
                                                    time.sleep(5)
                                                break
                                            else:
                                                print(
                                                    "Ocorreu um erro ao cancelar a ordem.")
                                        else:
                                            print(
                                                'STOP LOSS DE COMPRA NÃO PREENCHIDA :', low_price, ' quantidade =', quantidade1 + quantidade2)
                                            print('NOVA MAXIMA', high_price)
                                            print('preco_atual', preco_atual1)
                                            print('preco_de_compra',
                                                  preco_de_compra)
                                    except ValueError as e:
                                        print(
                                            "Uma exceção ValueError ocorreu:", e)
                                    except Exception as e:
                                        print(
                                            "Uma exceção ocorreu, mas não é um ValueError:", e)
                                    time.sleep(10)
# ********************************************************************************************************************************#
#                                       SE ORDEM 2 DE VENDA FOR ACIONADA
                            else:
                                if sell_order_status_response_2.json()['status'] == 'FILLED':
                                    while True:
                                        try:
                                            now = datetime.datetime.now()
                                            if now.hour == 7:
                                                print(
                                                    'NEM TAKE NEM STOP DE VENDA FORAM ACIONADOS \nTENPO ESGOTADO')

                                                buy_order_payload = {
                                                    'symbol': SYMBOL,
                                                    'side': 'BUY',
                                                    'type': 'MARKET',
                                                    'quantity': quantidade1,
                                                    'recvWindow': 5000,
                                                    'timestamp': int(time.time() * 1000)
                                                }
                                                signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                    buy_order_payload).encode(), hashlib.sha256).hexdigest()
                                                buy_order_payload['signature'] = signature
                                                buy_order_response = requests.post(
                                                    'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_payload)

                                                if buy_order_response.status_code == 200:
                                                    print(
                                                        'POSIÇAO ZERADA COM SUCESSO')
                                                else:
                                                    print(
                                                        'Erro ao executar ZERAGEM a mercado')
                                                params = {
                                                    'symbol': SYMBOL,
                                                    'timestamp': int(time.time() * 1000),
                                                    'recvWindow': 5000
                                                }
                                                signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                    params).encode(), hashlib.sha256).hexdigest()
                                                params['signature'] = signature
                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                                response = requests.delete(
                                                    'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                                print('ORDENS ABERTAS CANCELADAS',
                                                      response.json())
                                                break

                                            response = requests.get(
                                                ENDPOINT, params=payload, headers=headers)
                                            data = json.loads(response.text)
                                            nova_minima = float(data[0][3])
                                            preco_atual2 = float(data[0][4])
                                            if nova_minima < minima:
                                                minima = nova_minima
                                                low_price = "{:.2f}".format(
                                                    minima)
                                            n00 = float(
                                                maxima+(maxima - minima))
                                            take_compra2 = float(
                                                "{:.2f}".format(n00))

                                            buy_order_status_payload_b = {
                                                'symbol': SYMBOL,
                                                'orderId': buy_order_response_b.json()['orderId'],
                                                'timestamp': int(time.time() * 1000),
                                                'recvWindow': 5000
                                            }
                                            signature_b = hmac.new(SECRET_KEY.encode(), urlencode(
                                                buy_order_status_payload_b).encode(), hashlib.sha256).hexdigest()
                                            buy_order_status_payload_b['signature'] = signature_b
                                            buy_order_status_response_b = requests.get(
                                                'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_status_payload_b)
                                            if buy_order_status_response_b.json()['status'] == 'FILLED':
                                                print('Ordem de compra executada:',
                                                      buy_order_status_response_b.json())
                                                print(
                                                    'ORDEN DE COMPRA TAKE PROFIT == b ==PREENCHIDA\nENCERRANDO OPERAÇÕES....')
                                                params = {
                                                    'symbol': SYMBOL,
                                                    'timestamp': int(time.time() * 1000),
                                                    'recvWindow': 5000
                                                }
                                                signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                    params).encode(), hashlib.sha256).hexdigest()
                                                params['signature'] = signature
                                        # Enviar a solicitação para cancelar todas as ordens abertas
                                                response = requests.delete(
                                                    'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                                print('ORDENS ABERTAS CANCELADAS',
                                                      response.json())
                                                print('dia de lucro == b ==')
                                                print('\nFIM DA EXECUÇÃO')
                                                break
                                            else:
                                                print("\033c")
                                                print(
                                                    'TAKE PROFIT NÂO PREENCHIDO == b ==', take_venda, 'quantidade =', quantidade1)
# **************************************************************************************************************************************
#                                  ACRESCENTA NOVAS ORDENS STOP LOSS E TAKE PROFIT
                                            buy_order_status_payload_B = {
                                                'symbol': SYMBOL,
                                                'orderId': buy_order_response_B.json()['orderId'],
                                                'timestamp': int(time.time() * 1000),
                                                'recvWindow': 5000
                                            }
                                            signature_B = hmac.new(SECRET_KEY.encode(), urlencode(
                                                buy_order_status_payload_B).encode(), hashlib.sha256).hexdigest()
                                            buy_order_status_payload_B['signature'] = signature_B
                                            buy_order_status_response_B = requests.get(
                                                'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=buy_order_status_payload_B)

                                            if buy_order_status_response_B.json()['status'] == 'FILLED':
                                                print('STOP LOSS DE VENDA PREENCHIDO:',
                                                      buy_order_status_response_B.json())
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                                    # CANCELA A ORDEM TAKE PROFIT DE COMPRA caso seja stopado
                                                order_id = buy_order_response_b.json()[
                                                    'orderId']
                                                cancel_order_payload_b = {
                                                    'symbol': SYMBOL,
                                                    'orderId': order_id,
                                                    'recvWindow': 5000,
                                                    'timestamp': int(time.time() * 1000)
                                                }
                                                signature_b = hmac.new(SECRET_KEY.encode(), urlencode(
                                                    cancel_order_payload_b).encode(), hashlib.sha256).hexdigest()
                                                cancel_order_payload_b['signature'] = signature_b
                                                cancel_order_response_b = requests.delete(
                                                    'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=cancel_order_payload_b)
                                        # Verificar se a ordem foi cancelada com sucesso
                                                if cancel_order_response_b.json()['status'] == 'CANCELED':
                                                    print(
                                                        f" TAKE PROFIT DE VENDA FOI CANCELADO ID:{order_id}.")
                                                    print(
                                                        'STOP LOSS FOI ACIONADO')
                                                    print('')
                                                    print(
                                                        'NOVAS ORDENS SENDO ACRESCENTANDA == D ==')
# *************************************************************************************************************************************
#                                           ACRECENTA NOVAS ORDENS STOP loss
                                                    sell_order_payload_D = {
                                                        'symbol': SYMBOL,
                                                        'side': 'SELL',
                                                        'type': 'STOP_MARKET',
                                                        'stopPrice': low_price,
                                                        'quantity': quantidade2,
                                                        'recvWindow': 5000,
                                                        'timestamp': int(time.time() * 1000)
                                                    }
                                                    signature_D = hmac.new(SECRET_KEY.encode(), urlencode(
                                                        sell_order_payload_D).encode(), hashlib.sha256).hexdigest()
                                                    sell_order_payload_D['signature'] = signature_D
                                                    sell_order_response_D = requests.post(
                                                        'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_payload_D)
# =========================================================================================================================
                                        #   Adicionando uma ordem para take profit de venda
                                                    sell_order_payload_d = {
                                                        'symbol': SYMBOL,
                                                        'side': 'SELL',
                                                        'type': 'LIMIT',
                                                        'timeInForce': 'GTC',
                                                        'quantity': quantidade2,
                                                        'price': take_compra2,  # preço definido para a venda
                                                        'recvWindow': 5000,
                                                        'timestamp': int(time.time() * 1000)
                                                    }
                                                    signature_d = hmac.new(SECRET_KEY.encode(), urlencode(
                                                        sell_order_payload_d).encode(), hashlib.sha256).hexdigest()
                                                    sell_order_payload_d['signature'] = signature_d
                                                    sell_order_response_d = requests.post(
                                                        'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_payload_d)
                                                    print(
                                                        'Nova ordem de compra criada:')
                                                    print('stop loss = ',
                                                          high_price, 'quantidade =', quantidade2)
                                                    print(
                                                        'Nova ordem de compra criada:')
                                                    print(
                                                        'take profit =', take_venda, 'quantidade =', quantidade2)
# --------------------------------------------------------------------------------------------------------------------------------
                                                    # MONITORA AS NOVAS ORDENS STOPS
                                                    while True:
                                                        try:
                                                            now = datetime.datetime.now()
                                                            if now.hour == 7:
                                                                print(
                                                                    'TENPO ESGOTADO')
                                                                sell_order_payload = {
                                                                    'symbol': SYMBOL,
                                                                    'side': 'SELL',
                                                                    'type': 'MARKET',
                                                                    'quantity': quantidade2,
                                                                    'recvWindow': 5000,
                                                                    'timestamp': int(time.time() * 1000)
                                                                }
                                                                signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                    sell_order_payload).encode(), hashlib.sha256).hexdigest()
                                                                sell_order_payload['signature'] = signature
                                                                sell_order_response = requests.post(
                                                                    'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_payload)

                                                                if sell_order_response.status_code == 200:
                                                                    print(
                                                                        'POSIÇAO ZERADA COM SUCESSO')
                                                                else:
                                                                    print(
                                                                        'Erro ao executar ZERAGEM a mercado')
                                                                params = {
                                                                    'symbol': SYMBOL,
                                                                    'timestamp': int(time.time() * 1000),
                                                                    'recvWindow': 5000
                                                                }
                                                                signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                    params).encode(), hashlib.sha256).hexdigest()
                                                                params['signature'] = signature
                                                        # Enviar a solicitação para cancelar todas as ordens abertas
                                                                response = requests.delete(
                                                                    'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                                                print('ORDENS ABERTAS CANCELADAS',
                                                                      response.json())
                                                                print(
                                                                    'ORDENS ABERTAS CANCELADAS')
                                                                break

                                                            sell_order_status_payload_D = {
                                                                'symbol': SYMBOL,
                                                                'orderId': sell_order_response_D.json()['orderId'],
                                                                'timestamp': int(time.time() * 1000),
                                                                'recvWindow': 5000
                                                            }
                                                            signature_D = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                sell_order_status_payload_D).encode(), hashlib.sha256).hexdigest()
                                                            sell_order_status_payload_D['signature'] = signature_D
                                                            sell_order_status_response_D = requests.get(
                                                                'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_status_payload_D)

                                                            if sell_order_status_response_D.json()['status'] == 'FILLED':
                                                                print('Ordem de venda executada:',
                                                                      sell_order_status_response_D.json())
                                                                print(
                                                                    'dia de loss == D ==')

                                                                params = {
                                                                    'symbol': SYMBOL,
                                                                    'timestamp': int(time.time() * 1000),
                                                                    'recvWindow': 5000
                                                                }
                                                                signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                    params).encode(), hashlib.sha256).hexdigest()
                                                                params['signature'] = signature
                                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                                                response = requests.delete(
                                                                    'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                                                print('ORDENS ABERTAS CANCELADAS',
                                                                      response.json())
                                                                print(
                                                                    '\nFIM DA EXECUÇÃO == D ==')
                                                                break
                                                            else:
                                                                print("\033c")
                                                                print(
                                                                    'stop loss == D == nao preenchido', low_price, 'quantidade =', quantidade2)

                                                            sell_order_status_payload_d = {
                                                                'symbol': SYMBOL,
                                                                'orderId': sell_order_response_d.json()['orderId'],
                                                                'timestamp': int(time.time() * 1000),
                                                                'recvWindow': 5000
                                                            }
                                                            signature_d = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                sell_order_status_payload_d).encode(), hashlib.sha256).hexdigest()
                                                            sell_order_status_payload_d['signature'] = signature_d
                                                            sell_order_status_response_d = requests.get(
                                                                'https://testnet.binancefuture.com/fapi/v1/order', headers=headers, params=sell_order_status_payload_d)

                                                            if sell_order_status_response_d.json()['status'] == 'FILLED':
                                                                print('Ordem de compra executada:',
                                                                      sell_order_status_response_d.json())

                                                                params = {
                                                                    'symbol': SYMBOL,
                                                                    'timestamp': int(time.time() * 1000),
                                                                    'recvWindow': 5000
                                                                }
                                                                signature = hmac.new(SECRET_KEY.encode(), urlencode(
                                                                    params).encode(), hashlib.sha256).hexdigest()
                                                                params['signature'] = signature
                                                    # Enviar a solicitação para cancelar todas as ordens abertas
                                                                response = requests.delete(
                                                                    'https://testnet.binancefuture.com/fapi/v1/allOpenOrders', headers=headers, params=params)
                                                                print('ORDENS ABERTAS CANCELADAS',
                                                                      response.json())
                                                                print('dia de lucro == d ==',
                                                                      take_compra2)
                                                                print(
                                                                    '\nFIM DA EXECUÇÃO == d ==')
                                                                break
                                                            else:
                                                                print(
                                                                    'take profit == d< == nao preenchido', take_compra2, ' quantidade', quantidade2)
                                                                print(
                                                                    'preco_atual', preco_atual2)
                                                        except ValueError as e:
                                                            # Lidar com exceções do tipo ValueError
                                                            print(
                                                                "Uma exceção ValueError ocorreu:", e)
                                                        except Exception as e:
                                                            print(
                                                                "Uma exceção ocorreu, mas não é um ValueError:", e)
                                                        time.sleep(5)
                                                    break
                                                else:
                                                    print(
                                                        "Ocorreu um erro ao cancelar a ordem.")
                                            else:
                                                print(
                                                    'STOP LOSS  DE VENDA AINDA NÃO PREENCHIDA == B ==:', high_price, ' quantidade =', quantidade1+quantidade2)
                                                print('NOVA MINIMA', low_price)
                                                print('preco_atual',
                                                      preco_atual2)
                                                print('preco_de_venda',
                                                      preco_de_venda)
                                        except ValueError as e:
                                            # Lidar com exceções do tipo ValueError
                                            print(
                                                "Uma exceção ValueError ocorreu:", e)
                                        except Exception as e:
                                            print(
                                                "Uma exceção ocorreu, mas não é um ValueError:", e)
                                        time.sleep(10)
                            break
                        # se ordem de venda nao for colocada
                        else:
                            print('Ordem de venda nao foi colocada')
                        time.sleep(3)
                    break
    # *********************************************
            # se ordem de compra nao for colocada
                else:
                    print('Ordem de compra nao foi colocada')
            except ValueError as e:
                print(
                    "Uma exceção ValueError ocorreu:", e)
            except Exception as e:
                print(
                    "Uma exceção ocorreu, mas não é um ValueError:", e)
                break
            time.sleep(3)
# ======================================================================================================================
#               ENCERRAMENTO DO CODIGO PARA RENICIALO
        print('FIM DAS OPERAÇOES DE HOJE....')
    else:
        print("\033c")
        print('Aguardando chegada da hora...1')

    while datetime.datetime.now().hour == now.hour and datetime.datetime.now().minute == now.minute:
        time.sleep(10)
