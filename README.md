# Aventura da Rotina

Organizador de tarefas em Python para acompanhar estudos e prazos pelo terminal.
Projeto educacional criado com assistência de IA, disponível para estudo e evolução.

## Funcionalidades

- Cadastro com título, prazo e prioridade (1 é a mais alta).
- Listagem ordenada por prazo e prioridade, com filtros de status.
- Conclusão de tarefas e resumo com contagem de atrasos.
- Persistência em SQLite e exportação CSV sem sobrescrever arquivos existentes.
- Validação de entradas, consultas parametrizadas e testes automatizados.

## Executar

Requer Python 3.10 ou superior. Não precisa instalar pacotes.
No Windows, substitua `python` por `py` se necessário.

```sh
python rotina.py adicionar "Revisar banco de dados" --prazo 2026-12-01 --prioridade 1
python rotina.py listar
python rotina.py concluir 1
python rotina.py listar --status all
python rotina.py resumo
python rotina.py exportar tarefas.csv
```

Os comandos usam `rotina.db` na pasta atual. Para escolher outro banco:
`python rotina.py --db meus-estudos.db listar`.
Datas de exemplo devem ser ajustadas ao usar o projeto.

## Testes

```sh
python -m unittest discover -s tests -v
```

Os testes usam bancos temporários e não alteram seus dados.

## Estrutura e decisões

`rotina.py` separa operações de banco e interface de terminal em funções.
SQLite mantém os dados em um arquivo, sem exigir um servidor.
As datas são armazenadas no formato ISO para permitir ordenação cronológica.
Títulos exportados que poderiam ser fórmulas recebem um apóstrofo de proteção.

## Limitações e próximos passos

É um aplicativo local de usuário único, sem login, sincronização ou lembretes.
Próximas melhorias possíveis: edição de tarefas, categorias e uma interface web.
Os testes não substituem a revisão do código antes de utilizar dados importantes.

## Para estudar e apresentar

Explique como o SQLite persiste os dados, por que os parâmetros SQL usam `?`
e como os testes garantem que uma tarefa concluída sai da lista de pendentes.
Adapte uma funcionalidade e seus testes antes de apresentar o projeto em entrevistas.
