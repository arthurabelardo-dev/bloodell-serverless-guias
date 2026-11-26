import json
import time


invocacoes = 0


def responder(status, dados):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(dados, ensure_ascii=False),
    }


def lambda_handler(event, context):
    global invocacoes
    invocacoes += 1
    try:
        pedido = json.loads(event.get("body") or "{}")
    except (TypeError, ValueError):
        return responder(400, {"erro": "JSON inválido"})

    identificador = pedido.get("requisicaoId") if isinstance(pedido, dict) else None
    if not isinstance(identificador, str) or not identificador.strip():
        return responder(400, {"erro": "requisicaoId obrigatório"})
    if pedido.get("demorar") is True:
        time.sleep(5)

    return responder(201, {
        "guia": f"G-{identificador.strip()}",
        "hospital": pedido.get("hospital"),
        "bolsas": pedido.get("bolsas", []),
        "invocacaoNesteAmbiente": invocacoes,
    })
