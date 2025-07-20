function atualizarBanco(csrfToken) {
    if (!confirm("Tem certeza que deseja atualizar o banco de dados?")) return;

    fetch("/atualizar_banco/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json"
        }
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensagem || data.erro);
    })
    .catch(error => {
        alert("Erro ao conectar com o servidor.");
        console.error(error);
    });
}