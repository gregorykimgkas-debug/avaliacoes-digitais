# Arquitetura da demonstração

```text
Microsoft Forms / exportação anonimizada
                  |
                  v
      Importador CSV ou API protegida
                  |
                  v
             PostgreSQL
                  |
                  v
          FastAPI (REST/JSON)
                  |
                  v
        Dashboard web responsivo
```

## Separação do ambiente corporativo

O Power BI original permanece no tenant corporativo e não é exposto. A demonstração
pública reproduz seus principais indicadores usando apenas participantes codificados,
clientes fictícios e conteúdo autorizado. A API pública permite leitura dos indicadores,
enquanto a inclusão de resultados requer a chave `ADMIN_API_KEY`.

## Caminho para automação

1. Exportar as respostas autorizadas para CSV e remover dados identificáveis.
2. Executar `scripts/import_csv.py` para validar tipos e carregar os registros.
3. Como evolução, substituir a exportação manual por Microsoft Graph ou um fluxo
   Power Automate autorizado pela organização.

