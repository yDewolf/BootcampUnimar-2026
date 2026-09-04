# BootcampUnimar-2026
Projeto do Bootcamp Unimar 2026

## Sobre o projeto:
**Codei** é uma mini plataforma de exercícios de códigos que foi desenvolvida durante uma semana e meia para o **Bootcamp Unimar 2026**.

A ideia do projeto é implementar a principal funcionalidade desse tipo de plataforma que é a resolução de exercícios, além da possibilidade de administradores adicionarem e editarem exercícios.

## Como rodar o projeto:
Primeiro **instale o projeto** usando ``pip``
```
pip install -e .
```
Depois **execute o main** do client:
```
python src/leety/client/main.py
```

## Sobre a implementação:
###### Nessa seção vou deixar registrado meus comentários sobre a implementação do projeto (incluindo opiniões pessoais)
Eu comecei a desenvolver esse projeto no dia 24 de agosto, mas eu já tinha diversas ideias de como implementar. A única coisa que eu não tinha certeza de como seria implementada era a execução de código dos usuários (já que é uma questão de segurança).
### Arquitetura do projeto:
O projeto foi inicialmente desenvolvido pensando apenas no [servidor](/src/leety/server) e depois eu acabei desenvolvendo uma interface usando o tkinter conforme proposto nas aulas.
#### Estrutura de pastas
`OBS: leety era o nome do projeto até hoje (04/09/2026), eu já tinha pensado em codei, mas acabei mantendo as pastas como leety`
```
src/
    leety/
        client/ 
            -> Tudo que é especifico da interface gráfica (coisas do tkinter, etc)
        common/ 
            -> Tudo que é compartilhado entre o servidor e o client
            -> por exemplo: o sistema de banco de dados, FieldModels, etc
        server/
            -> Tudo que é específico do servidor
            -> por exemplo: sandbox_controller, controllers para acessar o banco, etc
```
#### Implementação do banco de dados:
Eu, particularmente, gostei muito da minha implementação do banco de dados. A ideia era fazer uma versão melhorada do meu "primeiro banco de dados" (implementado no [Bootcamp de 2024](https://github.com/yDewolf/Windy)), como aquele banco era baseado em arquivos .csv, eu mantive a mesma ideia só que explorei mais os conceitos que aprendi sobre typesafety e tipagem em python.
As principais classes do banco são:
- **[Field](src/leety/common/internals/database/protocols/model/field_model.py):** que **descreve um campo de um modelo** (`FieldModel`). Nele tem alguns overloads do `__get__` e `__set__` para gerenciar corretamente o acesso das informações e manter os auto complete do VS Code, etc.
- **[FieldModel](src/leety/common/internals/database/protocols/model/field_model.py):** **armazena os dados dos `Fields`** que são atribuídos dentro dele (na variável `_data` como `{field_name: value, ...}`). Essa é meio que uma classe abstrata que deve ser herdada para criar os `Fields` específicos do seu modelo. (Exemplos: [UserModel](src/leety/common/database/models/user_model.py) e [ExerciseModel](src/leety/common/database/models/exercise_model.py))
- **[IndexableFieldModel](src/leety/common/internals/database/protocols/model/default_models.py):** é uma classe que herda `FieldModel` e **implementa coisas relacionadas à indexação**, basicamente tem alguns dicionários que são utilizados para não ter que fazer um `for field in self.header_keys()` toda vez que fosse procurar um field ou algo do tipo.
- **[Table](src/leety/common/internals/database/protocols/csv_table.py):** é outra classe "abstrata" que deve ser instanciada usando anotação (`Table[ModelType]`). As `Table`s **armazenam vários modelos do tipo `ModelType`** dentro de uma lista, além de fazer outras coisas úteis como implementar funções de `get` (chamado de `match_linear` dentro do código), `to_csv_str`
- **[IndexableTable](src/leety/common/internals/database/protocols/csv_table.py):** é que semelhante ao `IndexableFieldModel`, uma classe que herda `Table` para implementar **funções baseada em indexação de valores**. Essa classe oferece funções como: `get_field_by_id`, `match_searchable_fields`, entre outras.
- **[Database](src/leety/common/internals/database/csvbase.py):** é uma classe semelhante ao `FieldModel` no que tange a funcionalidades, basicamente ela **armazena tabelas** que são descritas em subclasses (que herdam `_Database`).
###### (`SearchableField` é uma classe que não implementa nada e só é usada para checar se um `Field` deve ser indexado como "pesquisável") 

