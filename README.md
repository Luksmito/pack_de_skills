# Pack de skills

Coleção pessoal de skills reutilizáveis para agentes de programação.

## Skills

- [telegram-task-status](skills/telegram-task-status/SKILL.md): enviar ao Telegram resumos de conclusão, próximos passos e bloqueios, identificando o agente.

## Usar a skill do Telegram

Copie a pasta `skills/telegram-task-status` para `.agents/skills/telegram-task-status` no projeto em que deseja usá-la, preservando seus arquivos e subpastas.

Configure no ambiente de execução:

- `TELEGRAM_BOT_TOKEN`: token do bot, armazenado como segredo.
- `TELEGRAM_CHAT_ID`: ID exato do grupo de destino.
- `TELEGRAM_THREAD_ID`: opcional, para um tópico específico.
- Acesso HTTPS a `api.telegram.org` e Python 3.

Adicione o bot ao grupo e permita o envio de mensagens. Para descobrir o ID, envie `/start@USERNAME_DO_BOT` no grupo e peça ao agente para executar `scripts/notify.py --discover-groups`. Se já houver um receptor ativo, obtenha o ID por ele.

Exemplo de pedido:

> Use $telegram-task-status. Seu nome é Atlas. Ao concluir esta tarefa ou encontrar um bloqueio, envie ao grupo configurado um resumo do que fez, verificações, próximos passos e o que precisa de mim. Autorizo esses envios para esta tarefa.

A skill envia avisos durante a execução do agente. Não monitora comandos, não instala cron e não garante notificação se a sessão for encerrada abruptamente.

Nunca adicione tokens, senhas ou arquivos `.env` com credenciais a este repositório.
