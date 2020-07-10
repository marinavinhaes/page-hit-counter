# Tech 360 - AWS + CI + COPS 

## Exercício CI

Faça um fork desse repositório no namespace do seu usuário para continuar 

### Job de teste

Crie o arquivo `.gitlab-ci.yml` na raíz do projeto. É nesse arquivo que definiremos
as configurações de CI para nossa aplicação

.gitlab-ci.yml:
```yml
# Essa será a imagem docker utilizada por padrão em nosso pipeline
# No Gitlab da OLX temos acesso tanto a imagens publicas do Docker Hub
# quanto imagens do nosso registry interno (registry.olxbr.io:5000)
image: python:3

# Aqui definimos a ordem em que os stages serão executados
# Cada stage pode conter múltiplos jobs.
# Eles serão executados em paralelo
# O pipeline só passará para o próximo stage quando
# todos os jobs do stage atual forem executados com sucesso
stages:
  - test

# Nesse exemplo, estamos executando 2 testes (fakes)
# em paralelo:
unit_test:
  stage: test
  tags:
    - autoscale_preprod
  script:
    - echo "All tests passing"

integration_test:
  stage: test
  tags:
    - autoscale_preprod
  script:
    - echo "All tests passing"
```

Após fazer push dessas alterações, na página do seu projeto no Gitlab acesse 
*CI/CD > Pipelines* no menu lateral para ver o pipeline rodando.

Note que usamos a *tag* `autoscale_preprod`, para utilizar o runner autoscaled do
ambiente `preprod`

### Build da imagem

Vamos agora fazer build da imagem docker da aplicação, e push para nosso registry:

.gitlab-ci.yml:
```yaml

# A ordem em que os stages são definidos aqui é a ordem em que 
# eles serão executados no pipeline
stages:
  - test
  - docker

# ...


publish-image:
  image: docker:19.03-git # Nesse job vamos sobrescrever a imagem padrão com uma que contém o binário do docker
  stage: docker
  tags:
    - autoscale_preprod
  only:
    - tags # Queremos executar esse job apenas quando uma tag de versão for gerada no nosso repositório
  script:
    - docker build -t registry.olxbr.io:5000/treinamento-devops/$CI_PROJECT_NAMESPACE:$CI_COMMIT_TAG .
    - docker push registry.olxbr.io:5000/treinamento-devops/$CI_PROJECT_NAMESPACE:$CI_COMMIT_TAG
```

O nome da imagem que estamos criando utiliza as variáveis de ambiente `CI_PROJECT_NAMESPACE` e `CI_COMMIT_TAG`.
Essas são variáveis predefinidas do Gitlab CI, e ajudam a facilitar nosso build. Você pode conferir todas elas na 
[documentação oficial](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)

Após fazer o push dessa alteração repare que o pipeline executou apenas o stage de teste.
Isso acontece porque definimos uma condição do job ser executado apenas quando uma tag git for lançada, com a instrução

```
only:
  - tags
```

`only`/`except` são um recurso simples e poderoso do Gitlab CI/CD, que aceita tanto expressões regulares quanto [valores pré-definidos](https://docs.gitlab.com/ee/ci/yaml/#onlyexcept-basic)

Podemos criar uma tag no nosso repositório facilmente pela interface utilizando o menu lateral *Repository > Tags > New Tag*

Agora sim, o pipeline executado para a nova tag deve conter tanto o stage de teste quanto o novo stage de build e push da imagem

### Deploy para o COPS

Vamos finalmente fazer deploy da imagem criada para o [COPS](http://beta.cops.preprod.olxbr.cloud/)

No dashboard da sua aplicação no COPS, em *Deployment > COPS API* temos um exemplo de como atualizar a aplicação com uma nova imagem utilizando um comando `curl`.
Nós já temos esse pequeno script no nosso projeto, em `.buildscripts/deploy`.

Vamos definir um job no pipeline para executar esse script:

.gitlab-ci.yml:
```yaml
stages:
  - test
  - docker
  - deploy

# ...

deploy-cops:
  image: curlimages/curl:7.70.0 # Mais uma vez vamos sobrescrever o job com uma imagem que contém as dependencias que preciamos
  stage: deploy
  tags:
    - autoscale_preprod
  only:
    - tags
  when: manual
  script:
    - ./.buildscripts/deploy
```

A única coisa que estamos parametrizando nesse script é a URL da aplicação no COPS. Para adicionar uma variável customizada acesse *Settings > CI/CD* no menu lateral

Expanda a sessão **Variables** e adicione uma nova variável `COPS_URL` com a URL da sua aplicação.
Desabilite a opção *Masked* caso ela esteja habilitada, e não se esqueça de salvar as alterações.

Crie uma nova tag de versão, e confira os pipelines

O último job **não** será executado automaticamente. Apenas quando um usuário clicar no botão **play**

Isso acontece porque esse novo job contém uma nova instrução:

```
when: manual
```

Esse parâmetro define que o job só será executado dessa maneira, permitindo um controle maior de deployment (CD)

Confira na [documentação](https://docs.gitlab.com/ee/ci/yaml/#when) os possíveis valores para o parâmetro `when`

### Acessando a aplicação

No dashboard da aplicação no COPS, na aba *Containers*, um novo container deve ser provisionado com a nova versão que lançamos da aplicação.
Espere o *Status* mudar para **running**, e acesse a aplicação (*Overview > Exposed Ports*)

Se tudo ocorreu bem, você verá uma simples página com um contador de visitas

Se não, hora de debuggar :D 

