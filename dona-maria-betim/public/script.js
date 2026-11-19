/* Informações organizadas para facilitar futuras atualizações. */
const DADOS_RESTAURANTE = {
  whatsapp: "5531993270377",
  telefoneExibicao: "(31) 99327-0377",
  telefoneAntigo: "(31) 2572-1247",
  endereco: "Av. Edméia Mattos Lazzarotti, 2770 - Ingá Alto (Horto), Betim - MG, CEP 32604-446",
  instagram: "https://instagram.com/donamariabetim",
  mensagemWhatsApp: "Olá! Gostaria de reservar ou consultar o cardápio e os rodízios do Restaurante Dona Maria.",
  // Horários informados; verificar se o jantar termina às 22h30 ou às 23h.
  horarios: {
    monday: [{ abre: "11:00", fecha: "15:00" }],
    tuesday: [{ abre: "11:00", fecha: "15:00" }, { abre: "18:00", fecha: "23:00" }],
    wednesday: [{ abre: "11:00", fecha: "15:00" }, { abre: "18:00", fecha: "23:00" }],
    thursday: [{ abre: "11:00", fecha: "15:00" }, { abre: "18:00", fecha: "23:00" }],
    friday: [{ abre: "11:00", fecha: "15:00" }, { abre: "18:00", fecha: "23:00" }],
    saturday: [{ abre: "11:30", fecha: "15:30" }, { abre: "18:00", fecha: "23:00" }],
    sunday: [{ abre: "11:30", fecha: "15:30" }, { abre: "18:00", fecha: "23:00" }]
  },
  rodizios: [
    { dia: "monday", nome: "Sem rodízio noturno", preco: "Não há rodízio", inclui: "A casa funciona no almoço. Consulte pelo WhatsApp as opções à la carte disponíveis à noite." },
    { dia: "tuesday", nome: "Terçaneja", preco: "A partir de R$ 79,90", inclui: "Noite temática. Consulte a equipe para saber o que está incluído e a programação musical." },
    { dia: "wednesday", nome: "Rodízio completo", preco: "A partir de R$ 89,90", inclui: "Pode incluir churrasco, petiscos, pizzas, comida japonesa e bebidas selecionadas. A composição varia conforme o dia." },
    { dia: "thursday", nome: "Rodízio de pizza", preco: "A partir de R$ 69,90", inclui: "Variedade de pizzas. Consulte os sabores e os demais itens do rodízio." },
    { dia: "friday", nome: "Rodízio completo", preco: "R$ 99,90", inclui: "Pode incluir churrasco, petiscos, pizzas, comida japonesa e bebidas selecionadas. A composição varia conforme o dia." },
    { dia: "saturday", nome: "Rodízio completo", preco: "R$ 119,00", inclui: "Pode incluir churrasco, petiscos, pizzas, comida japonesa e bebidas selecionadas. A composição varia conforme o dia." },
    { dia: "sunday", nome: "Rodízio de pizza", preco: "A partir de R$ 69,90", inclui: "Variedade de pizzas. Consulte os sabores e os demais itens do rodízio." }
  ],
  cardapio: [
    { categoria: "Almoço", nome: "Self-service por quilo", descricao: "Pratos quentes, saladas e churrasco. Preço de referência; consulte o valor atual.", preco: "R$ 49,90/kg" },
    { categoria: "Pizzas", nome: "Pizza pequena", descricao: "Consulte os sabores disponíveis.", preco: "A partir de R$ 65,00" },
    { categoria: "Pizzas", nome: "Pizza média", descricao: "Consulte os sabores disponíveis.", preco: "A partir de R$ 75,00" },
    { categoria: "Pizzas", nome: "Pizza grande", descricao: "Consulte os sabores disponíveis.", preco: "A partir de R$ 85,00" },
    { categoria: "Porções e pratos", nome: "Bolinho de bacalhau (10 unidades)", descricao: "Porção com dez unidades.", preco: "R$ 49,00" },
    { categoria: "Porções e pratos", nome: "Linguiça artesanal", descricao: "Acompanha mandioca ou fritas.", preco: "R$ 89,00" },
    { categoria: "Porções e pratos", nome: "Espaguete à bolonhesa", descricao: "Massa com molho à bolonhesa.", preco: "R$ 49,00" },
    { categoria: "Porções e pratos", nome: "Escapole de filé ao molho roti", descricao: "Serve até duas pessoas. Nome conforme informado pelo estabelecimento.", preco: "R$ 159,00" },
    { categoria: "Bebidas", nome: "Cervejas 600 ml", descricao: "Original e Heineken.", preco: "R$ 20,00 a R$ 22,00" },
    { categoria: "Bebidas", nome: "Chopp", descricao: "Consulte os tamanhos disponíveis.", preco: "A partir de R$ 15,00" },
    { categoria: "Bebidas", nome: "Cachaças e doses", descricao: "Consulte as opções disponíveis.", preco: "R$ 10,00 a R$ 15,00" }
  ]
};

const NOMES_DIAS = {
  sunday: "Domingo",
  monday: "Segunda-feira",
  tuesday: "Terça-feira",
  wednesday: "Quarta-feira",
  thursday: "Quinta-feira",
  friday: "Sexta-feira",
  saturday: "Sábado"
};

// Obtém dia e hora no fuso de São Paulo, sem depender do fuso do aparelho.
const hojeEmBetim = () => {
  const partes = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Sao_Paulo",
    weekday: "long",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23"
  }).formatToParts(new Date());
  return Object.fromEntries(partes.map((parte) => [parte.type, parte.value]));
};

// Exibe avisos curtos, como os dados de redes sociais ainda pendentes.
function mostrarToast(mensagem) {
  const toast = document.querySelector("#toast");
  toast.textContent = mensagem;
  toast.classList.add("is-visible");
  window.clearTimeout(mostrarToast.timeout);
  mostrarToast.timeout = window.setTimeout(() => toast.classList.remove("is-visible"), 3600);
}

// Monta o link wa.me com o número e a mensagem definidos nos dados do restaurante.
function montarWhatsApp() {
  const numero = DADOS_RESTAURANTE.whatsapp.replace(/\D/g, "");
  const links = document.querySelectorAll(".js-whatsapp");

  links.forEach((link) => {
    link.href = `https://wa.me/${numero}?text=${encodeURIComponent(DADOS_RESTAURANTE.mensagemWhatsApp)}`;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });
}

// Atualiza endereço, telefone, redes sociais, mapa e indicador de funcionamento.
function montarContato() {
  const enderecoCodificado = encodeURIComponent(DADOS_RESTAURANTE.endereco);
  document.querySelector("#address-text").textContent = DADOS_RESTAURANTE.endereco;
  document.querySelector("#phone-link").textContent = DADOS_RESTAURANTE.telefoneExibicao;
  document.querySelector("#phone-link").href =
    `tel:+${DADOS_RESTAURANTE.whatsapp}`;
  document.querySelector("#old-phone-text").textContent =
    `${DADOS_RESTAURANTE.telefoneAntigo} · pode estar desatualizado; prefira o WhatsApp`;
  document.querySelectorAll(".js-instagram").forEach((link) => {
    link.href = DADOS_RESTAURANTE.instagram;
  });
  document.querySelector("#directions-link").href =
    `https://www.google.com/maps/search/?api=1&query=${enderecoCodificado}`;
  document.querySelector(".map-card iframe").src =
    `https://maps.google.com/maps?q=${enderecoCodificado}&t=&z=16&ie=UTF8&iwloc=&output=embed`;
  atualizarHorarios();
  window.setInterval(atualizarHorarios, 60000);
}

// Converte um horário HH:MM para minutos, facilitando a comparação com a hora atual.
function converterHorario(horario) {
  const correspondencia = /^([01]\d|2[0-3]):([0-5]\d)$/.exec(horario || "");
  return correspondencia ? Number(correspondencia[1]) * 60 + Number(correspondencia[2]) : null;
}

// Compara o horário atual de Betim com as faixas cadastradas para o dia.
function atualizarHorarios() {
  const status = document.querySelector("#open-status");
  const agora = hojeEmBetim();
  const diaAtual = agora.weekday.toLowerCase();
  const minutoAtual = Number(agora.hour) * 60 + Number(agora.minute);
  const faixasHoje = DADOS_RESTAURANTE.horarios[diaAtual] || [];
  const aberto = faixasHoje.some((faixa) => {
    const abertura = converterHorario(faixa.abre);
    const fechamento = converterHorario(faixa.fecha);
    return abertura !== null && fechamento !== null && minutoAtual >= abertura && minutoAtual < fechamento;
  });

  status.className = `open-status ${aberto ? "is-open" : "is-closed"}`;
  status.lastElementChild.textContent = aberto ? "Aberto agora" : "Fechado agora";
}

// Cria os sete cards e destaca o rodízio correspondente ao dia em São Paulo.
function montarRodizios() {
  const hoje = hojeEmBetim().weekday.toLowerCase();
  const lista = document.querySelector("#rodizio-list");

  lista.innerHTML = DADOS_RESTAURANTE.rodizios.map((rodizio) => {
    const hojeTem = rodizio.dia === hoje;
    return `
      <article class="rodizio-card${hojeTem ? " is-today" : ""}">
        ${hojeTem ? `<span class="today-badge">${rodizio.dia === "monday" ? "Hoje não tem" : "Hoje tem!"}</span>` : ""}
        <p class="rodizio-day">${NOMES_DIAS[rodizio.dia]}</p>
        <h3>${rodizio.nome}</h3>
        <p class="rodizio-includes">${rodizio.inclui}</p>
        <div class="rodizio-price"><span>${rodizio.dia === "monday" ? "Programação" : "por pessoa"}</span><strong>${rodizio.preco}</strong></div>
      </article>`;
  }).join("");
}

// Cria as abas e mostra apenas os produtos da categoria selecionada.
function montarCardapio() {
  const categorias = [...new Set(DADOS_RESTAURANTE.cardapio.map((item) => item.categoria))];
  const tabs = document.querySelector("#menu-tabs");
  const itens = document.querySelector("#menu-items");

  function selecionarCategoria(categoria) {
    const itensCategoria = DADOS_RESTAURANTE.cardapio.filter((item) => item.categoria === categoria);
    tabs.querySelectorAll(".menu-tab").forEach((tab) => {
      const selecionada = tab.dataset.categoria === categoria;
      tab.setAttribute("aria-selected", String(selecionada));
      tab.tabIndex = selecionada ? 0 : -1;
      if (selecionada) itens.setAttribute("aria-labelledby", tab.id);
    });
    itens.innerHTML = itensCategoria.map((item) => `
      <article class="menu-item">
        <div><h3>${item.nome}</h3><p>${item.descricao}</p></div>
        <strong>${item.preco}</strong>
      </article>`).join("");
  }

  tabs.innerHTML = categorias.map((categoria, indice) => `
    <button class="menu-tab" type="button" role="tab" id="tab-${indice}" aria-controls="menu-items"
      aria-selected="${indice === 0}" tabindex="${indice === 0 ? "0" : "-1"}" data-categoria="${categoria}">
      ${categoria}
    </button>`).join("");

  tabs.addEventListener("click", (event) => {
    const tab = event.target.closest(".menu-tab");
    if (tab) selecionarCategoria(tab.dataset.categoria);
  });

  tabs.addEventListener("keydown", (event) => {
    if (!["ArrowRight", "ArrowLeft"].includes(event.key)) return;
    const botoes = [...tabs.querySelectorAll(".menu-tab")];
    const atual = botoes.indexOf(document.activeElement);
    const deslocamento = event.key === "ArrowRight" ? 1 : -1;
    const proximo = botoes[(atual + deslocamento + botoes.length) % botoes.length];
    proximo.focus();
    selecionarCategoria(proximo.dataset.categoria);
  });

  if (categorias.length) selecionarCategoria(categorias[0]);
}

// Abre e fecha a navegação móvel e recolhe o menu após selecionar um link.
function configurarMenuMobile() {
  const botao = document.querySelector(".menu-toggle");
  const menu = document.querySelector("#menu-principal");

  function fecharMenu() {
    botao.setAttribute("aria-expanded", "false");
    botao.setAttribute("aria-label", "Abrir menu");
    menu.classList.remove("is-open");
  }

  botao.addEventListener("click", () => {
    const aberto = botao.getAttribute("aria-expanded") !== "true";
    botao.setAttribute("aria-expanded", String(aberto));
    botao.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
    menu.classList.toggle("is-open", aberto);
  });

  menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", fecharMenu));
  document.addEventListener("click", (event) => {
    if (!menu.contains(event.target) && !botao.contains(event.target)) fecharMenu();
  });
}

// Abre cada foto em um diálogo ampliado e permite fechá-lo por botão ou fundo.
function configurarGaleria() {
  const lightbox = document.querySelector("#lightbox");
  const imagem = lightbox.querySelector("img");

  document.querySelectorAll(".gallery-item").forEach((item) => {
    item.addEventListener("click", () => {
      imagem.src = item.dataset.image;
      imagem.alt = item.querySelector("img").alt;
      lightbox.showModal();
      document.body.classList.add("no-scroll");
    });
  });

  function fecharLightbox() {
    lightbox.close();
    document.body.classList.remove("no-scroll");
  }

  lightbox.querySelector(".lightbox-close").addEventListener("click", fecharLightbox);
  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) fecharLightbox();
  });
  lightbox.addEventListener("close", () => document.body.classList.remove("no-scroll"));
}

// Anima elementos quando entram na tela e respeita a preferência por menos movimento.
function configurarAnimacoes() {
  const elementos = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    elementos.forEach((elemento) => elemento.classList.add("is-visible"));
    return;
  }

  const observador = new IntersectionObserver((entradas, observer) => {
    entradas.forEach((entrada) => {
      if (entrada.isIntersecting) {
        entrada.target.classList.add("is-visible");
        observer.unobserve(entrada.target);
      }
    });
  }, { threshold: 0.12 });

  elementos.forEach((elemento) => observador.observe(elemento));
}

document.querySelector("#current-year").textContent = new Date().getFullYear();
montarWhatsApp();
montarContato();
montarRodizios();
montarCardapio();
configurarMenuMobile();
configurarGaleria();
configurarAnimacoes();
