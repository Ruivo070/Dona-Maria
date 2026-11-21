const campoDataReserva = document.querySelector("#data_reserva");
const campoHorarioReserva = document.querySelector("#horario");

const horariosPorDia = {
  0: [["11:30", "15:30"], ["18:00", "23:00"]],
  1: [["11:00", "15:00"]],
  2: [["11:00", "15:00"], ["18:00", "23:00"]],
  3: [["11:00", "15:00"], ["18:00", "23:00"]],
  4: [["11:00", "15:00"], ["18:00", "23:00"]],
  5: [["11:00", "15:00"], ["18:00", "23:00"]],
  6: [["11:30", "15:30"], ["18:00", "23:00"]]
};

function minutosDoHorario(horario) {
  const [hora, minuto] = horario.split(":").map(Number);
  return hora * 60 + minuto;
}

if (campoDataReserva && campoHorarioReserva) {
  function validarDataReserva() {
    campoDataReserva.setCustomValidity(
      campoDataReserva.validity.rangeUnderflow
        ? "A data da reserva não pode estar no passado."
        : ""
    );
    validarHorarioReserva();
  }

  function validarHorarioReserva() {
    let mensagem = "";
    if (campoDataReserva.value && campoHorarioReserva.value) {
      const diaDaSemana = new Date(`${campoDataReserva.value}T12:00:00`).getDay();
      const minuto = minutosDoHorario(campoHorarioReserva.value);
      const dentroDoFuncionamento = (horariosPorDia[diaDaSemana] || []).some(
        ([abertura, fechamento]) =>
          minuto >= minutosDoHorario(abertura) &&
          minuto < minutosDoHorario(fechamento)
      );
      if (!dentroDoFuncionamento) {
        mensagem = "Escolha um horário dentro do funcionamento do restaurante.";
      }
    }
    campoHorarioReserva.setCustomValidity(mensagem);
  }

  campoDataReserva.addEventListener("input", validarDataReserva);
  campoDataReserva.addEventListener("change", validarDataReserva);
  campoDataReserva.addEventListener("invalid", validarDataReserva);
  campoHorarioReserva.addEventListener("input", validarHorarioReserva);
  campoHorarioReserva.addEventListener("change", validarHorarioReserva);
}
