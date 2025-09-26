# Cantina Sem Fila

O Cantina Sem Fila é um portal web desenvolvido em Python, utilizando Django Wagtail, criado para modernizar e facilitar a gestão do consumo dos alunos em cantinas escolares.  

A plataforma permite que os pais ou responsáveis administrem a conta dos alunos, visualizem o histórico de presença e consumo, e adicionem créditos de forma prática e segura.

---

## Funcionalidades

- Gestão de contas dos pais e alunos  
- Histórico de presença e consumo  
- Adição de crédito online  
- Autenticação e segurança  
- Administração via Wagtail Admin

---

## Tecnologias Utilizadas

- Linguagem: Python 3.11+  
- Framework: Django + Wagtail CMS   
- Banco de Dados: PostgreSQL  
- Frontend: HTML5, CSS3, JavaScript (com Bootstrap)  
- Outros: Docker, Mailjet (envio de emails), OpenCV (captura de imagens)  

---

## Estrutura do Projeto

```text
cantina-sem-fila/
│── backend/           # Aplicação principal Django + Wagtail
│── flask_services/    # Módulos Flask para captura/processamento
│── static/            # Arquivos estáticos (CSS, JS, imagens)
│── templates/         # Templates HTML
│── docs/              # Documentação do projeto
│── README.md          # Documentação principal
```

## Como Executar o Projeto

### 1. Clonar o repositório

`git clone https://github.com/renatofk/cantina-sem-fila.git cd cantina-sem-fila` 

### 2. Criar e ativar o ambiente virtual

`python -m venv venv source venv/bin/activate # Linux/Mac venv\Scripts\activate `

### 3. Instalar as dependências

`pip install -r requirements.txt` 

### 4. Configurar o banco de dados

No arquivo `.env`, adicione suas variáveis de ambiente:

`DATABASE_URL=postgres://usuario:senha@localhost:5432/cantina SECRET_KEY=sua_chave_secreta DEBUG=True` 

### 5. Rodar as migrações

`python manage.py migrate` 

### 6. Iniciar o servidor Django

`python manage.py runserver` 

# Deploy 

- Atualizar o codigo
`git pull in /root/cantina-sem-fio`

- Entrar na pasta do app
`cd cantinaSF/`

- Atualizar imagem docker e rodar o container atualizado
`docker-compose up -d --build`

- Mostrar log de transações
`docker-compose logs -f web`

----------

## Roadmap

-   Integração com reconhecimento facial para registro automático de presença
    
-   Dashboard com gráficos de consumo por aluno
    
-   Aplicativo mobile para pais e alunos
    
-   Notificações por email/SMS sobre saldo e consumo
    

----------

## Contribuição

Contribuições são bem-vindas.

1.  Faça um fork do projeto
    
2.  Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
    
3.  Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
    
4.  Envie para o repositório (`git push origin feature/nova-funcionalidade`)
    
5.  Abra um Pull Request
