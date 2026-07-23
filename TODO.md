# TODO — Orçamentos NEWA

Backlog de melhorias e correções. Marque `[x]` ao concluir.

## Bugfixes / melhorias do assistente de conferência (v0.1 → v0.2)

- [ ] **1. Zoom no modo "Destaque na página"** — adicionar lupa / zoom intuitivo ao
      passar o mouse (ou clicar) sobre a página de origem, para ler os valores sem
      depender do tamanho fixo da miniatura. Ref.: etapa "Informações do Veículo e
      Condutor" no modo *Destaque na página*.

- [ ] **2. Formatação do aviso amarelo "texto do modelo"** — o alerta nas etapas de
      Capa e Observações está com o negrito/quebra fora de lugar ("Este bloco **é**
      **texto do modelo** — não vem dos PDFs. Ajuste o conteúdo padrão em **Editar
      modelo**"). Corrigir o HTML/CSS para uma frase corrida e legível.

- [ ] **3. Recortes aparecendo em branco (modo "Recortes")** — em algumas páginas os
      crops saem vazios/brancos (falha ao posicionar o `background-image` da imagem
      da página; provável divergência de escala/resolução entre o bbox e a imagem
      raster quando a página não é a página 1, ou a imagem ainda não carregou).
      Garantir carregamento da imagem antes de calcular o recorte e revisar o cálculo
      de `background-size`/`background-position` por página.

- [ ] **4. Destacar o botão "Preencher vazios"** — hoje é um botão fantasma discreto no
      rodapé; dar mais destaque visual (estilo secundário/pílula) já que é a ação que
      resolve as pendências que bloqueiam a geração.

- [ ] **5. Cabeçalho de identificação das seguradoras no topo do assistente** — adicionar
      uma faixa mostrando **as duas seguradoras** da proposta (logo completo + nome),
      deixando claro "esta proposta compara X vs Y" logo no topo do wizard.

- [ ] **6. Padronizar a tela "Quantas propostas comparar?"** — fixar **2 como padrão
      absoluto**; marcar as opções 1, 3, 4 e 5 como **"Em desenvolvimento — pode
      apresentar bugs"** (aviso/badge), mantendo 2 como o fluxo garantido.

## Extração (Fase B — perfis)

- [ ] Perfil dedicado para o **layout Allianz nativo (multi-oferta)** — hoje cai no
      perfil "tradicional"/IA; precisa escolher a oferta correta.
- [ ] Autorar perfis das demais seguradoras contra os PDFs de amostra.
- [ ] Editar/gerenciar perfis pela UI (seção *Modelos de Entrada*).

## Produção (WordPress)

- [ ] Portar motor de extração + perfis para PHP (`smalot/pdfparser`).
- [ ] Login via usuários nativos do WordPress; persistência em `wp_options`.
- [ ] Empacotador `.zip` do plugin instalável.
- [ ] Modo Visual: usar Imagick quando disponível; senão, o fac-símile de fragmentos.

## Geral

- [ ] Fallback de visão (IA) para PDFs escaneados (sem texto nativo).
- [ ] Calibrar cores/logos oficiais das seguradoras.
- [ ] Refinar recorte para não capturar o cabeçalho azul das tabelas em campos
      colados ao header.
