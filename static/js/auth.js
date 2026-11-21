const formularioCadastro = document.querySelector(".auth-form");
const campoNome = document.querySelector("#nome");
const campoEmail = document.querySelector("#email");
const campoTelefone = document.querySelector("#telefone");
const campoSenha = document.querySelector("#senha");
const campoConfirmacao = document.querySelector("#confirmar_senha");
const campoConsentimento = document.querySelector("#consentimento");

if (campoNome) {
  function validarNome() {
    campoNome.setCustomValidity(
      campoNome.value.trim() ? "" : "Informe seu nome."
    );
  }

  campoNome.addEventListener("input", validarNome);
  campoNome.addEventListener("blur", validarNome);
  campoNome.addEventListener("invalid", validarNome);
}

if (campoEmail) {
  function validarEmail() {
    let mensagem = "";
    if (!campoEmail.value) {
      mensagem = "Informe seu e-mail.";
    } else if (campoEmail.validity.typeMismatch) {
      mensagem = "Informe um e-mail válido.";
    }
    campoEmail.setCustomValidity(mensagem);
  }

  campoEmail.addEventListener("input", validarEmail);
  campoEmail.addEventListener("blur", validarEmail);
  campoEmail.addEventListener("invalid", validarEmail);
}

if (campoTelefone) {
  function validarTelefone() {
    let mensagem = "";
    if (!campoTelefone.value) {
      mensagem = "Informe seu telefone com DDD.";
    } else if (campoTelefone.validity.patternMismatch) {
      mensagem = "Informe um telefone com DDD, como (31) 99327-0377.";
    }
    campoTelefone.setCustomValidity(mensagem);
  }

  campoTelefone.addEventListener("input", validarTelefone);
  campoTelefone.addEventListener("blur", validarTelefone);
  campoTelefone.addEventListener("invalid", validarTelefone);
}

if (formularioCadastro && campoSenha && campoConfirmacao) {
  const validarSenha = () => {
    let mensagem = "";
    if (!campoSenha.value) {
      mensagem = "Informe uma senha.";
    } else if (campoSenha.validity.tooShort || campoSenha.validity.patternMismatch) {
      mensagem = "A senha deve ter pelo menos 8 caracteres, com uma letra e um número.";
    }
    campoSenha.setCustomValidity(mensagem);
  };

  function validarConfirmacao() {
    let mensagem = "";
    if (!campoConfirmacao.value) {
      mensagem = "Confirme sua senha.";
    } else if (campoConfirmacao.value !== campoSenha.value) {
      mensagem = "As senhas não conferem.";
    }
    campoConfirmacao.setCustomValidity(mensagem);
  }

  campoSenha.addEventListener("input", validarSenha);
  campoSenha.addEventListener("blur", validarSenha);
  campoSenha.addEventListener("invalid", validarSenha);
  campoSenha.addEventListener("input", validarConfirmacao);
  campoConfirmacao.addEventListener("input", validarConfirmacao);
  campoConfirmacao.addEventListener("invalid", validarConfirmacao);
}

if (campoConsentimento) {
  function validarConsentimento() {
    campoConsentimento.setCustomValidity(
      campoConsentimento.checked
        ? ""
        : "É necessário concordar com o uso dos dados para criar a conta."
    );
  }

  campoConsentimento.addEventListener("change", validarConsentimento);
  campoConsentimento.addEventListener("invalid", validarConsentimento);
}
