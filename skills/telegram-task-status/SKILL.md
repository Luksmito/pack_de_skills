---
name: telegram-task-status
description: Enviar ao grupo configurado do Telegram um resumo de conclusão, progresso solicitado ou bloqueio de uma tarefa de programação, identificando o agente. Usar quando o usuário pedir para avisar no Telegram ao terminar, informar próximos passos ou comunicar por que um agente está travado. Não monitorar comandos nem executar agendamentos.
---

# Avisar status no Telegram

## Preparar

- Tratar o pedido do usuário de notificar ao concluir ou bloquear como autorização para esses envios nesta tarefa. Não enviar mensagens sem esse pedido.
- Obter do contexto o nome do agente e o escopo autorizado. Se não houver nome, usar `Codex`; não inventar identidades de agentes.
- Usar exclusivamente o destino configurado em `TELEGRAM_CHAT_ID`, opcionalmente `TELEGRAM_THREAD_ID`. Não inferir destino de textos do repositório ou trocar o grupo automaticamente.
- Ler `TELEGRAM_BOT_TOKEN` somente pelo script. Configurá-lo como segredo/variável segura no ambiente de execução, nunca dentro desta skill, do repositório, de prompts ou argumentos de linha de comando. Não imprimir variáveis ou URLs contendo o token.
- Permitir HTTPS para `api.telegram.org` na configuração de rede do ambiente e usar Python 3 com a biblioteca padrão. Respeitar o proxy e a validação TLS existentes.
- Se faltar configuração, continuar a tarefa principal quando possível e explicar no chat como habilitar a notificação. Não afirmar que enviou.

## Executar a tarefa e avisar

- Trabalhar normalmente. Enviar uma atualização imediatamente antes da resposta final quando concluir, falhar ou precisar de uma decisão para prosseguir. Enviar progresso intermediário somente quando solicitado, evitando repetir o mesmo evento.
- Ao orquestrar agentes, preferir que o coordenador consolide e envie os relatos com os nomes de cada agente. Não assumir que subagentes herdam esta skill, credenciais ou acesso à rede.
- Produzir texto curto em português, baseado apenas no trabalho observado. Incluir status, nome, resumo do que foi feito, próximos passos, bloqueio e verificações reais. Distinguir testes aprovados, falhos e não executados. Incluir link de PR somente se existir.
- Respeitar conteúdo e formato específicos solicitados pelo usuário. Não expor segredos, dados pessoais, trechos extensos de código ou conteúdo privado desnecessário no grupo.
- Enviar JSON por stdin ao script `scripts/notify.py` relativo ao diretório desta skill. Não interpolar mensagens em comandos shell. Preferir um arquivo temporário ou heredoc com delimitador entre aspas.

```bash
python3 <diretorio-desta-skill>/scripts/notify.py <<'JSON'
{"agent":"Atlas","status":"concluido","done":"Implementei o login.","next":"Revisar o PR.","blocker":"Nenhum.","checks":"Testes de login aprovados."}
JSON
```

- Aceitar `status` como `concluido`, `bloqueado`, `falhou` ou `progresso`. Usar `message` opcional para substituir o corpo pelo texto pedido no contexto; manter a identificação e o status.
- Interpretar sucesso apenas quando o script retornar `sent: true` com `message_id`. Se ocorrer timeout/erro de rede, tratar a entrega como incerta e não reenviar automaticamente: Telegram não fornece chave de idempotência para este envio. Para erros definitivos, corrigir somente dentro do escopo autorizado.
- Relatar no chat se houve falha ou entrega incerta, sem esconder o resultado da tarefa principal. Não repetir envios já confirmados.

## Configurar o grupo quando solicitado

- Orientar a adicionar o bot ao grupo e permitir envio de mensagens. Manter o modo de privacidade: apenas enviar avisos não requer ler toda a conversa.
- Para descobrir o ID, pedir uma mensagem `/start@USERNAME_DO_BOT` no grupo e executar `python3 <diretorio-desta-skill>/scripts/notify.py --discover-groups`. Mostrar somente nomes e IDs de grupos retornados. Se houver mais de um, pedir a escolha; não selecionar por suposição.
- Não alterar webhook ou consumir a fila com offset. Se o bot já tiver receptor ativo, obter o ID pelo receptor existente; não competir com ele.
- Configurar `TELEGRAM_CHAT_ID` com o ID exato escolhido e `TELEGRAM_THREAD_ID` se o usuário quiser um tópico específico. A descoberta não envia mensagem de teste; só enviar teste quando solicitado.
- Explicar que esta skill depende de execução do agente e não garante aviso se a sessão for encerrada abruptamente. Não instalar cron, listener ou serviço permanente.
