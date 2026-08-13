# Deploy 

## Integração CaraPassa

O CaraPassa é responsável pela biometria. O Django recebe somente eventos de
reconhecimento e continua responsável por refeição, presença, saldo e cobrança.
O Django não armazena fotografias nem embeddings.

Variáveis obrigatórias/recomendadas:

```env
CARAPASSA_ENABLED=true
CARAPASSA_WEBHOOK_SECRET=troque-por-um-segredo-forte
CARAPASSA_TIMESTAMP_TOLERANCE_SECONDS=300
CARAPASSA_APP_URL=http://localhost:8001
CARAPASSA_API_KEY=cp_substitua_pela_chave_do_dispositivo
CARAPASSA_FACE_STATUS_URL=http://localhost:8001/v1/subjects/face-status
CARAPASSA_FACE_STATUS_TIMEOUT_SECONDS=15
CARAPASSA_DELETE_SUBJECT_URL=http://localhost:8001/v1/subjects/{subject_id}
CARAPASSA_DELETE_TIMEOUT_SECONDS=30
```

`CARAPASSA_API_KEY` é usada pelo atalho de cadastro facial e nunca deve ser
versionada. O envio por query string deve ser limitado ao desenvolvimento;
em produção, prefira uma sessão de cadastro curta e descartável.

O dashboard administrativo exibe **Iniciar reconhecimento** somente para
operadores que não pertençam ao grupo de responsáveis. A tela raiz do
CaraPassa reconhece o aluno e publica o webhook configurado em
`DJANGO_WEBHOOK_URL`. No CaraPassa, use:

```env
DJANGO_WEBHOOK_URL=http://localhost:8000/api/carapassa/webhook/
DJANGO_WEBHOOK_SECRET=o-mesmo-valor-de-CARAPASSA_WEBHOOK_SECRET
```

O dispositivo associado à API key deve estar cadastrado no Django em
**Dispositivos CaraPassa**, com os mesmos `tenant_id`, `school_id` e
`device_id`. Sem esse mapeamento o evento será auditado, mas não haverá débito.

Cadastre cada câmera em **Dispositivos CaraPassa** no Wagtail Admin, usando os
UUIDs de tenant, escola e dispositivo fornecidos pelo CaraPassa. O
`Student.integration_id` é o `subject_id` que deve ser cadastrado no CaraPassa.

A lista de alunos consulta o status facial em lote e abre a captura em uma
popup. Ao concluir, o CaraPassa deve notificar a janela de origem e fechar:

```javascript
window.opener?.postMessage({
  type: "carapassa.face_registered",
  subject_id: subjectId,
  success: true
}, "https://portal.cantinasemfila.com.br");
window.close();
```

Ao excluir um aluno, o portal chama `DELETE /v1/subjects/{subject_id}` antes
da exclusão local. Respostas `2xx` e `404` são consideradas sucesso; qualquer
outra resposta bloqueia a exclusão local para não deixar biometria órfã.

Webhook:

```text
POST /api/carapassa/webhook/
X-CaraPassa-Timestamp: timestamp ISO-8601 UTC
X-CaraPassa-Signature: sha256=<HMAC hexadecimal>
```

A assinatura é HMAC-SHA256 de `timestamp + "." + JSON canônico`. Eventos são
idempotentes por `event_id`; uma segunda proteção impede mais de um consumo do
mesmo aluno na mesma refeição e data. Resultados de regra de negócio retornam
HTTP 200 e ficam auditáveis em **Eventos CaraPassa**.

Antes do deploy, execute:

```bash
python manage.py migrate
python manage.py test cantinaSF
```

- Atualizar o codigo
git pull in /root/cantina-sem-fio

- Entrar na pasta do app
cd cantinaSF/

- Atualizar imagem docker e rodar o container atualizado
docker-compose up -d --build

- Mostrar log de transações
docker-compose logs -f web
