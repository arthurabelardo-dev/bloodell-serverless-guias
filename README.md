# Bloodell · Guia de transporte serverless

Uma requisição de transporte identifica o hospital e as bolsas que devem seguir para ele. A função recebe esses dados sintéticos e emite uma guia JSON. O projeto usa o Caminho A da atividade, com AWS SAM CLI, Docker Desktop e runtime Python 3.12 em contêiner. A função usa apenas a biblioteca padrão.

## Como reproduzir

Com o Docker Desktop em execução, abra o Git Bash na raiz do projeto. O build em contêiner usa a versão de Python do template. A primeira execução precisa de internet para baixar as imagens públicas.

```bash
sam --version
docker version
sam build --use-container
sam local invoke GuiaFunction -e events/pedido.json
sam local invoke GuiaFunction -e events/pedido.json
sam local start-api
```

Em outro Git Bash, rode as três chamadas e observe o campo `invocacaoNesteAmbiente`.

```bash
for i in 1 2 3; do
  curl -sS -w '\nHTTP %{http_code}\n' http://127.0.0.1:3000/guias \
    -H 'Content-Type: application/json' \
    -d '{"requisicaoId":"R-002","hospital":"H-Caruaru"}'
done
```

Encerre o servidor com Ctrl+C, rode `sam local start-api --warm-containers LAZY` e repita as três chamadas. A função responde com HTTP 201 quando emite a guia. Um corpo vazio `{}` recebe HTTP 400.

Para observar o limite de execução, envie um pedido que espera cinco segundos.

```bash
curl -sS -w '\nHTTP %{http_code}\n' http://127.0.0.1:3000/guias \
  -H 'Content-Type: application/json' \
  -d '{"requisicaoId":"R-003","demorar":true}'
```

Encerre o servidor, altere `Timeout: 3` para `Timeout: 10` em `template.yaml`, execute novamente `sam build --use-container` e `sam local start-api` e repita o pedido. O template entregue começa com 3 segundos para permitir reproduzir a falha.

## Resultados e respostas

1. **Primeira e segunda invocações.** No PC, os comandos completos levaram **13,368 s** e **7,719 s**. O relatório do emulador registrou duração de **50,95 ms** e **52,43 ms** e Init Duration de **0,05 ms** em ambos. Na fase Init, o Lambda prepara o runtime e executa o código de inicialização do módulo, incluindo a atribuição inicial do contador. O tempo do comando também inclui a CLI e a preparação local do contêiner. As medições mostram que a primeira chamada completa foi mais lenta, mas não permitem atribuir a diferença de 5,649 s ao Init. [Ciclo de vida do Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
2. **Estado entre chamadas.** Com a API local no modo padrão, as três respostas mostraram **1, 1, 1**. Com `--warm-containers LAZY`, mostraram **1, 2, 3**. O contador fica na memória de cada ambiente. Um novo ambiente começa em zero e incrementa ao receber o pedido. Um estoque, por exemplo, precisa de armazenamento persistente e compartilhado.
3. **Tempo limite.** Com limite de 3 s e espera de 5 s, o SAM registrou o timeout e a API local devolveu **HTTP 502**. Com limite de 10 s, o mesmo pedido devolveu **HTTP 201**. O limite máximo de uma execução do Lambda é **900 s (15 minutos)**. Para um trabalho divisível, é possível enfileirar etapas menores e persistir o progresso. Para uma etapa indivisível mais longa, uma opção é um job em contêiner. [Cotas do Lambda](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)
4. **Custo com os preços do enunciado.** Para 1.000.000 de execuções, 128 MB equivalem a 0,125 GB, e 100 ms equivalem a 0,1 s. O consumo é 1.000.000 × 0,125 × 0,1 = **12.500 GB-s**. A computação custa 12.500 × US$ 0,0000166667 = **US$ 0,20833375**. Somando US$ 0,20 pelas requisições, o total é **US$ 0,40833375**, aproximadamente **US$ 0,41**. Essa conta usa os valores da aula para o Lambda e desconsidera franquias e outros serviços. Os testes da atividade rodaram no PC.
5. **Aplicação no Bloodell.** Emitir uma guia a partir de uma requisição é um trabalho curto, com entrada e saída bem definidas. Acompanhar continuamente um veículo durante toda a entrega exigiria manter a execução ativa por um tempo imprevisível. Nesse fluxo, cada atualização de posição poderia gerar um evento separado, com o histórico salvo fora da função.

## Evidências

[Assistir ao vídeo da atividade no YouTube](https://youtu.be/uyRUuWm1h6E?si=dYLOQY2ODHWN0Tpa)

O [registro dos experimentos](evidencias/experimentos.txt) contém os tempos, as respostas HTTP, os contadores e os testes dos dois limites de execução.

A [gravação da demonstração local](evidencias/demonstracao.webm) mostra uma nova execução da invocação por evento, da emissão de guia por HTTP e da chamada que excede três segundos. A gravação apresenta os comandos e a saída real em uma tela dedicada, sem narração. As capturas mostram o [evento](evidencias/01-evento.png), o [HTTP 201](evidencias/02-http.png) e o [timeout](evidencias/03-timeout.png).

## Uso de IA

O Codex auxiliou na implementação da função, na configuração do SAM, na execução local, no registro das evidências e na redação das explicações. A validação usou o emulador com o evento JSON e pedidos HTTP reais, conferindo códigos, conteúdo das guias, tempos e comportamento do contador.
