# AvalIA

Demonstração pública e anonimizada do projeto de aplicação, correção e análise de
provas digitais desenvolvido por Gregory Kim Almeida da Silva para a Atividade
Extensionista III do curso de Engenharia de Software.

## O que pode ser comprovado

- aplicação web funcional sem dependência do Power BI;
- API documentada em `/docs`;
- banco relacional com avaliações e resultados;
- regra automática de aprovado/reprovado;
- filtros e indicadores consolidados;
- importação validada de dados em CSV;
- implantação reproduzível com Docker Compose.

Todos os nomes de participantes e clientes desta versão são fictícios ou codificados.
O relatório corporativo original e seus dados não são publicados.

## Executar localmente

Requer Python 3.12 ou superior.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt pytest httpx
.venv\Scripts\python -m uvicorn backend.app:app --reload
```

Acesse `http://localhost:8000`. A documentação da API estará em
`http://localhost:8000/docs`.

## Importar respostas anonimizadas

O formato esperado está em `database/exemplo_respostas.csv`.

```powershell
.venv\Scripts\python scripts\import_csv.py database\exemplo_respostas.csv
```

## Publicar com Docker

No servidor, copie `.env.example` para `.env`, gere senhas seguras e ajuste
`SITE_ADDRESS`. Depois execute:

```bash
docker compose up -d --build
```

Com um domínio apontado para o servidor, o Caddy provisiona HTTPS automaticamente.
Sem domínio próprio, use um endereço sslip.io (ex.: `SITE_ADDRESS=avalia.46-224-183-60.sslip.io`,
sem `http://`), que resolve para o IP do servidor e permite HTTPS automático via Let's Encrypt.

O site está publicado em https://avalia.46-224-183-60.sslip.io/

## Configurar links do Forms

Os URLs públicos ficam na coluna `form_url` da tabela `assessments`. Somente cópias
demonstrativas configuradas para acesso externo devem ser usadas.

Copie `config/forms.example.json` para `config/forms.json`, substitua os endereços e
execute:

```powershell
.venv\Scripts\python scripts\set_form_links.py config\forms.json
```

## Documentação

- [Arquitetura](docs/ARQUITETURA.md)
- [Schema PostgreSQL](database/schema.sql)
- [Exemplo de importação](database/exemplo_respostas.csv)
