# projeto-vi-beauty
Projeto  Faculdade Impacta 5° semestre

## Como rodar o projeto

1. **Clone o repositório:**
   ```
   git clone <url-do-repo>
   cd <nome-da-pasta>
   ```

2. **Configure o ambiente:**
   - Certifique-se de ter o [Docker](https://www.docker.com/) e o [Docker Compose](https://docs.docker.com/compose/) instalados.

3. **Suba os containers:**
   ```
   docker-compose up -d --build
   ```

4. **Acesse a aplicação:**
   - Abra o navegador e acesse: [http://localhost:8080](http://localhost:8080)

## Funcionalidades

- Cadastro de usuário
- Login e logout

## Estrutura

- `src/` - Código fonte da aplicação Flask
- `db/` - Scripts de inicialização do banco de dados
- `docker-compose.yml` - Orquestração dos containers

## Requisitos

- Docker
- Docker Compose

## Observações

- As credenciais do banco de dados estão configuradas no `docker-compose.yml`.
- As dependências Python estão em `src/requirements.txt`.