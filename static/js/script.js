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

// Destaca o rodízio do dia sem reconstruir o conteúdo vindo do banco.
function montarRodizios() {
  const hoje = hojeEmBetim().weekday.toLowerCase();
  document.querySelectorAll(".rodizio-card").forEach((cartao) => {
    const hojeTem = cartao.dataset.dia === hoje;
    cartao.classList.toggle("is-today", hojeTem);
    if (!hojeTem) return;

    const selo = document.createElement("span");
    selo.className = "today-badge";
    selo.textContent = hoje === "monday" ? "Hoje não tem" : "Hoje tem!";
    cartao.prepend(selo);
  });
}

// Filtra os itens já renderizados pelo servidor para manter a saída escapada.
function montarCardapio() {
  const tabs = document.querySelector("#menu-tabs");
  const itens = document.querySelector("#menu-items");
  const botoes = [...tabs.querySelectorAll(".menu-tab")];
  const produtos = [...itens.querySelectorAll(".menu-item")];

  function selecionarCategoria(categoria) {
    botoes.forEach((tab) => {
      const selecionada = tab.dataset.categoria === categoria;
      tab.setAttribute("aria-selected", String(selecionada));
      tab.tabIndex = selecionada ? 0 : -1;
      if (selecionada) itens.setAttribute("aria-labelledby", tab.id);
    });
    produtos.forEach((produto) => {
      produto.hidden = produto.dataset.categoria !== categoria;
    });
  }

  tabs.addEventListener("click", (event) => {
    const tab = event.target.closest(".menu-tab");
    if (tab) selecionarCategoria(tab.dataset.categoria);
  });

  tabs.addEventListener("keydown", (event) => {
    if (!["ArrowRight", "ArrowLeft"].includes(event.key)) return;
    const atual = botoes.indexOf(document.activeElement);
    if (atual < 0 || !botoes.length) return;
    const deslocamento = event.key === "ArrowRight" ? 1 : -1;
    const proximo = botoes[(atual + deslocamento + botoes.length) % botoes.length];
    proximo.focus();
    selecionarCategoria(proximo.dataset.categoria);
  });

  if (botoes.length) selecionarCategoria(botoes[0].dataset.categoria);
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
