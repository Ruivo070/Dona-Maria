# 03 — Planejamento do site

**Aluno / Turma / Data:** ______________________________________________

## Objetivo

Criar uma página única para apresentar o Restaurante Dona Maria, organizar as principais informações e facilitar o contato. O site não deve inventar fatos: quando um detalhe estiver pendente, deve aparecer como uma observação para o cliente consultar a equipe.

## Estrutura e mapa das seções

1. **Início (hero):** nome, frase de apresentação, foto de destaque e botão para reservar ou pedir pelo WhatsApp.
2. **A casa:** resumo do perfil do restaurante e diferenciais: estacionamento, playground, delivery, reservas, vales e área ao ar livre. A história da Dona Maria ainda precisa ser confirmada.
3. **Rodízios:** sete cards, um por dia, com o tema, o valor informado e uma explicação sobre os itens. O card do dia recebe um destaque automático.
4. **Cardápio:** filtros para Almoço, Pizzas, Porções e pratos, e Bebidas.
5. **Galeria:** fotos de pratos, salão, área externa e espaço infantil. As imagens do protótipo são placeholders.
6. **Contato e horários:** telefone/WhatsApp, tabela de horários, aviso sobre feriados e indicador “Aberto agora / Fechado”.
7. **Localização:** mapa incorporado e botão para abrir a rota no Google Maps.
8. **Rodapé:** Instagram e direitos autorais.

## Menu de navegação

O menu fixo terá links para **A casa**, **Rodízios**, **Cardápio**, **Galeria** e **Contato**, além de um botão de WhatsApp. No celular, os links ficam dentro de um menu hambúrguer. Os links levam às seções da mesma página com rolagem suave.

## Paleta de cores

| Cor | Código | Uso e motivo |
|---|---|---|
| Vinho | `#752A1F` | Cor principal da marca; passa acolhimento e combina com a proposta de restaurante. |
| Vinho escuro | `#4E1F19` | Fundo da seção de contato e contraste com textos claros. |
| Terracota | `#A84632` | Destaques, pequenos ícones e chamadas. |
| Amarelo quente | `#E8B85B` | Botões, detalhes e destaque do rodízio de hoje. |
| Creme | `#FBF7EF` | Fundo suave para seções e cards. |
| Quase branco | `#FFFDF8` | Fundo principal, para manter o texto fácil de ler. |
| Texto escuro | `#30251F` | Cor de leitura em fundos claros. |

## Tipografia

- **Playfair Display** nos títulos, para dar personalidade e um toque acolhedor.
- **Poppins** nos textos, botões e informações, por ser legível em telas pequenas.
- As duas fontes são carregadas pelo Google Fonts. Se não houver internet, o navegador usa fontes substitutas do sistema.

## Imagens

No protótipo, serão usadas imagens temporárias do Unsplash para mostrar a organização visual. Antes da divulgação, elas devem ser trocadas por fotos autorizadas do próprio estabelecimento: fachada, salão, buffet, churrasco, pizzas, área externa e playground. Cada imagem no código tem comentário **“TROCAR pela foto real”**. A pasta `img` guarda instruções para adicionar esses arquivos.

## Organização das informações

Os dados variáveis — horários, rodízios, preços do cardápio, endereço e WhatsApp — ficam reunidos no começo de `script.js`. Assim, uma alteração pode ser feita sem procurar os dados em várias partes do código. Os valores são referências e os avisos orientam o cliente a consultar a equipe quando a informação puder mudar.

O rodízio aparece com o preço como “a partir de” quando essa foi a forma informada. A segunda-feira mostra que não há rodízio noturno. O horário de funcionamento tem uma tabela visível, e o JavaScript usa os mesmos períodos para calcular se o restaurante está aberto.

## Funcionalidades planejadas

- HTML semântico, título, descrição, idioma e textos alternativos das imagens.
- Layout responsivo, começando pelo celular.
- Menu hambúrguer, com estado acessível para leitores de tela.
- Filtros de cardápio por categoria.
- Destaque do rodízio do dia com o fuso `America/Sao_Paulo`.
- Indicador de funcionamento calculado pelos horários e atualizado durante o uso.
- Links de WhatsApp com mensagem pré-pronta e botão flutuante.
- Galeria com lightbox para ampliar as imagens.
- Mapa, rota no Google Maps e atalhos para redes sociais.
- Animações de entrada usando `IntersectionObserver`, respeitando a preferência por movimento reduzido.

## Protótipo (wireframe)

### Versão celular

```text
+--------------------------------+
| DM Dona Maria       [☰ menu]   |
+--------------------------------+
| FOTO DE DESTAQUE               |
| Comida boa, mesa cheia         |
| [Reservar pelo WhatsApp]       |
+--------------------------------+
| A CASA                         |
| Resumo + diferenciais          |
+--------------------------------+
| RODÍZIOS                       |
| [Segunda]                      |
| [Terça]                        |
| [Quarta] ...                   |
+--------------------------------+
| CARDÁPIO                       |
| [Almoço][Pizzas][Porções][...] |
| Item e preço                   |
+--------------------------------+
| GALERIA (grade de fotos)       |
+--------------------------------+
| CONTATO + horários + mapa      |
| [Como chegar]                  |
+--------------------------------+
| Rodapé e redes       [WhatsApp]|
+--------------------------------+
```

### Versão desktop

```text
+--------------------------------------------------------------+
| LOGO          A casa  Rodízios  Cardápio  Galeria  Contato   |
+--------------------------------------------------------------+
| FOTO / FRASE / BOTÃO              | imagem de destaque       |
+--------------------------------------------------------------+
| foto da casa                      | apresentação + serviços  |
+--------------------------------------------------------------+
|        7 cards de rodízio em linhas responsivas              |
+--------------------------------------------------------------+
| categorias do cardápio       | itens e preços                |
+--------------------------------------------------------------+
|       galeria em grade de fotos com ampliação                 |
+--------------------------------------------------------------+
| contato, horários e redes     | mapa                          |
+--------------------------------------------------------------+
| Rodapé                                        botão WhatsApp   |
+--------------------------------------------------------------+
```
