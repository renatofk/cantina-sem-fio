# Deploy 

- Atualizar o codigo
git pull in /root/cantina-sem-fio

- Entrar na pasta do app
cd cantinaSF/

- Atualizar imagem docker e rodar o container atualizado
docker-compose up -d --build

- Mostrar log de transações
docker-compose logs -f web