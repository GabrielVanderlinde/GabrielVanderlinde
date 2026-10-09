# PROMPT — Criar um GitHub Profile README animado com retrato ASCII e terminal Tactical Green

Quero que você desenvolva um perfil GitHub visualmente impressionante, minimalista, profissional e personalizado, inspirado diretamente no projeto de referência:

**Repositório de referência:**  
https://github.com/GabrielVanderlinde/GabrielVanderlinde

**Meu objetivo:** criar uma versão com a mesma proposta visual, nível de acabamento, estilo de animação e organização desse projeto, mas usando minha própria identidade, meu retrato, minhas tecnologias, meus projetos e minhas estatísticas do GitHub.

Você deve trabalhar diretamente no meu repositório de perfil GitHub, caso tenha acesso a ele. Não quero apenas instruções ou exemplos de código: quero que implemente a solução, valide-a e deixe o projeto funcionando.

## 1. Antes de começar: analise a referência

Inspecione o repositório de referência e seus arquivos, especialmente:

- `README.md`
- `gerar_gif.py`
- `assets/portrait.txt`
- `assets/terminal_profile.gif`
- `.github/workflows/generate-terminal-profile.yml`

Entenda como o retrato ASCII é criado, como a animação do terminal é renderizada, como as cores são aplicadas, como as estatísticas do GitHub são consultadas e como o GIF é atualizado automaticamente pelo GitHub Actions.

Use essa análise para reproduzir a abordagem técnica e visual. Não copie os dados pessoais, os projetos, o retrato, os links ou as informações profissionais do proprietário da referência.

Antes de fazer alterações, inspecione meu repositório e preserve todos os arquivos e funcionalidades que não estejam relacionados a esse projeto.

## 2. Conceito visual

Crie uma composição única, com proporção vertical próxima de 1100 × 1340 pixels, contendo duas partes integradas:

### Parte superior — Retrato ASCII

- Um retrato detalhado meu, criado a partir de uma fotografia minha fornecida por mim ou de uma imagem minha que eu autorize utilizar.
- Aparência de arte ASCII real, formada por caracteres e diferentes intensidades de cinza.
- Fidelidade às características visuais da fotografia original, sem inventar ou modificar minha aparência.
- Posicionamento centralizado, com boa definição e contraste.
- Estética monocromática, com tons de cinza sobre fundo preto.
- Pequeno identificador discreto, como `ASCII PORTRAIT / GRAYSCALE RENDER`.

### Parte inferior — Terminal animado

- Uma janela de terminal estilizada, posicionada abaixo do retrato.
- Aparência de um terminal Linux moderno, com bordas discretas e detalhes minimalistas.
- Texto monoespaçado, hierarquia tipográfica consistente e bom espaçamento.
- Animação de digitação progressiva, como se os comandos estivessem sendo executados em tempo real.
- Cursor piscando, comandos, indicadores de status, pausas naturais e transições entre seções.
- Painel lateral compacto com informações técnicas e status.
- Animação contínua, em loop infinito.

O resultado deve parecer um terminal de verdade, não apenas uma imagem estática com textos coloridos.

## 3. Regra fundamental de cores

Utilize a paleta **Tactical Green**, mantendo as cores estritamente limitadas à interface da janela do terminal.

Paleta principal:

- Preto carvão: `#111411`
- Verde militar: `#567A46`
- Verde oliva claro: `#A3B18A`
- Cinza claro: `#D2D5CE`

A regra mais importante é:

> **Somente a janela do terminal deve utilizar cores da paleta verde.**

Fora da janela do terminal, mantenha o fundo, as bordas externas, as linhas decorativas, os textos externos e o retrato em tons neutros de preto, branco e cinza.

O retrato deve permanecer totalmente monocromático, sem tonalidade verde, filtros coloridos ou alterações cromáticas.

Dentro do terminal, utilize o preto carvão como fundo e aplique o verde militar e o verde oliva em comandos, títulos, indicadores de status e pequenos detalhes. Use o cinza claro nos textos informativos.

Não use azul, roxo, vermelho, ciano ou outras cores de destaque. Evite neon excessivo, gradientes chamativos, efeitos exagerados ou estética gamer. A aparência deve ser sóbria, masculina, elegante, técnica e profissional.

## 4. Personalização com minhas informações reais

Identifique meu usuário do GitHub e examine meu perfil público e meus repositórios para reunir informações relevantes.

Use somente informações reais e verificáveis. Não invente experiência profissional, domínio de tecnologias, quantidade de projetos, estrelas, certificações ou contribuições.

Personalize o conteúdo com base nos dados disponíveis, incluindo:

- Meu nome ou nome profissional.
- Minha função atual ou área de atuação.
- Minha localização, somente se estiver publicamente disponível e for apropriado.
- Minhas principais tecnologias.
- Meus projetos mais relevantes.
- Meus interesses profissionais e objetivos de desenvolvimento, quando forem conhecidos.
- Meus links públicos relevantes.

Se uma informação pessoal não estiver disponível, omita-a em vez de inventá-la.

Organize a animação em seções de terminal, adaptadas à minha realidade, como:

- **SYSTEM BOOT** — inicialização visual do terminal e carregamento dos módulos.
- **PROFILE** — apresentação profissional resumida.
- **TECH STACK** — tecnologias efetivamente utilizadas nos meus projetos ou comprovadas pelo perfil.
- **FEATURED PROJECTS** — seleção dos meus projetos públicos mais relevantes, com descrições curtas e verdadeiras.
- **LIVE GITHUB STATS** — estatísticas públicas atuais do meu perfil e dos meus repositórios.
- **CURRENT MISSION** — foco técnico, áreas de estudo e objetivos profissionais que possam ser confirmados.

Adapte ou remova seções quando não houver dados suficientes. Não apresente conteúdo genérico como se fosse informação pessoal confirmada.

## 5. Estatísticas do GitHub

Implemente uma consulta à API pública do GitHub para buscar dados atualizados durante a geração do GIF.

Quando os dados estiverem disponíveis, exiba informações como:

- Quantidade de repositórios públicos.
- Soma de estrelas nos projetos próprios elegíveis, explicando o critério utilizado.
- Linguagens predominantes nos repositórios.
- Projeto atualizado mais recentemente.
- Data do último envio de alterações, quando disponível.

Filtre repositórios arquivados ou forks quando isso fizer sentido para o indicador exibido. Evite duplicações e deixe os critérios claros.

Não coloque tokens ou credenciais pessoais diretamente no código. Se uma variável `GITHUB_TOKEN` for necessária, use os mecanismos seguros do GitHub Actions.

A consulta deve possuir timeout e tratamento de erros. Caso a API esteja indisponível, a geração do GIF deverá continuar normalmente, exibindo uma mensagem discreta de indisponibilidade, sem inventar números ou interromper todo o workflow.

## 6. Arquitetura e arquivos

Adote uma estrutura equivalente à da referência, adaptando-a à organização que já existir no meu repositório.

Como base, utilize:

```text
MEU-USUARIO/
├── README.md
├── gerar_gif.py
├── assets/
│   ├── portrait.txt
│   └── terminal_profile.gif
└── .github/
    └── workflows/
        └── generate-terminal-profile.yml
```

Os arquivos devem cumprir estas funções:

### `README.md`

Deve conter somente a composição visual do perfil: um único GIF animado, centralizado e ocupando praticamente toda a largura disponível. Não adicione cartões de estatísticas, listas de habilidades, badges, textos introdutórios ou outras imagens abaixo dele. A proposta é manter o README visualmente limpo.

Use texto alternativo acessível e, se necessário, um parâmetro de versão na URL da imagem para evitar que o cache do GitHub continue mostrando uma versão antiga.

### `gerar_gif.py`

Deve conter a lógica completa de geração do retrato ASCII, composição visual, terminal, digitação animada, consulta às estatísticas, tratamento de erros e exportação do GIF.

Use Python com Pillow, ou uma alternativa técnica equivalente se houver uma boa justificativa. O código deve ser organizado, legível, modular e fácil de manter.

### `assets/portrait.txt`

Deve conter o mapa de caracteres utilizado para renderizar o retrato ASCII. Ele precisa ser derivado da minha imagem autorizada, respeitando suas proporções e suas características visuais.

Não reutilize o retrato ASCII pertencente ao dono do repositório de referência.

### `assets/terminal_profile.gif`

Deve ser o GIF final realmente gerado pelo código, não um arquivo estático, uma imagem ilustrativa ou uma versão fictícia.

### `.github/workflows/generate-terminal-profile.yml`

Deve automatizar a geração e a publicação do GIF.

## 7. Automação com GitHub Actions

Configure um workflow que:

- Execute quando os arquivos relevantes do gerador, do mapa do retrato ou do workflow forem modificados na branch principal.
- Permita execução manual pelo GitHub Actions.
- Execute uma atualização periódica semanal.
- Instale as dependências necessárias.
- Execute o gerador.
- Valide o arquivo produzido.
- Publique o GIF atualizado no repositório automaticamente.

Use permissões mínimas e seguras, concedendo escrita em conteúdo somente quando necessária.

Evite loops de execução causados pelo próprio commit gerado. Se houver concorrência entre execuções ou conflitos de push, implemente um fluxo seguro de sincronização e novas tentativas.

A atualização periódica não deve tornar o projeto instável nem sobrescrever alterações de código feitas por mim.

## 8. Qualidade e desempenho da animação

O GIF deve apresentar boa qualidade visual e movimento fluido, mantendo o estilo de terminal com digitação progressiva.

Critérios:

- Dimensões aproximadas de 1100 × 1340 pixels, ajustáveis se necessário.
- Retrato com resolução visual suficiente para reconhecer os traços da fotografia autorizada.
- Janela de terminal legível, com textos sem sobreposições ou cortes.
- Todas as seções devem caber na área disponível.
- Loop infinito.
- Pausas naturais entre seções.
- Tamanho do arquivo otimizado, sem destruir a qualidade visual.
- Uso de otimização de GIF, como `gifsicle`, quando disponível.
- Quantidade de quadros suficiente para uma animação agradável, sem gerar desnecessariamente um arquivo enorme.

Priorize qualidade, legibilidade e bom desempenho em vez de criar milhares de quadros apenas por efeito visual.

## 9. Testes obrigatórios

Antes de concluir, valide o resultado de verdade:

1. Verifique se o código executa sem erros.
2. Gere o GIF no ambiente disponível ou por meio do GitHub Actions.
3. Confirme as dimensões, a quantidade de quadros, o loop infinito e a existência do arquivo final.
4. Verifique visualmente quadros representativos da animação para detectar textos cortados, sobreposições, erros de alinhamento ou problemas no retrato.
5. Confirme que o retrato e todo o exterior da janela continuam em preto, branco e cinza.
6. Confirme que as cores Tactical Green aparecem exclusivamente dentro da janela do terminal.
7. Confira se as informações exibidas pertencem realmente ao meu perfil.
8. Verifique se o README aponta para o GIF correto.
9. Execute o workflow e confirme se ele terminou com sucesso e publicou o GIF atualizado.
10. Verifique a versão efetivamente publicada, não apenas o código-fonte.

Se não for possível executar algum teste por falta de permissões, fotografia ou outra dependência, informe claramente a limitação. Não alegue que algo foi testado quando não foi.

## 10. Limites e cuidados

- Não altere meu nome de usuário, minha identidade ou minhas informações pessoais para imitar as do projeto de referência.
- Não reutilize o retrato do proprietário da referência.
- Não sobrescreva arquivos não relacionados ao projeto.
- Não exclua funcionalidades que já existam no repositório.
- Não exponha segredos, tokens ou informações privadas.
- Não inclua estatísticas inventadas ou dados não verificados.
- Não deixe a solução dependendo de um arquivo presente apenas no computador local.
- Não substitua o GIF por uma imagem gerada estaticamente.
- Não encerre o trabalho logo após editar o código: faça a geração e valide a publicação sempre que as permissões permitirem.

## 11. Resultado esperado

Quero um perfil GitHub de alto nível, com aparência de projeto feito sob medida:

- Retrato ASCII personalizado em tons de cinza na parte superior.
- Terminal animado na parte inferior.
- Paleta Tactical Green restrita exclusivamente à janela do terminal.
- Digitação progressiva, cursor, comandos e seções organizadas.
- Informações profissionais e projetos reais.
- Estatísticas obtidas da API pública do GitHub.
- README composto por um único GIF.
- Geração e atualização automatizadas via GitHub Actions.
- Código-fonte organizado e documentação mínima necessária para manutenção.

Use o repositório `GabrielVanderlinde/GabrielVanderlinde` como referência visual e técnica, mas crie uma implementação personalizada para o meu perfil.

**Comece inspecionando meu repositório e a referência. Em seguida, implemente, teste, gere, publique e valide o resultado. Ao final, apresente um resumo dos arquivos criados ou modificados, a URL do GIF publicado e o resultado real dos testes e do GitHub Actions.**
