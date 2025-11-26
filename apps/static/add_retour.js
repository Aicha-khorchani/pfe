document.addEventListener("DOMContentLoaded", function () {
    const factureSelect = document.getElementById("factureSelect");
    const commandSelect = document.getElementById("commandSelect");
    const submitButton = document.querySelector("button[type='submit']");
    const reasonInput = document.getElementById("raison_retour");
    const dateInput = document.getElementById("date_retour");
    const supplierSelect = document.getElementById("supplier");
    const deliveryPersonSelect = document.getElementById("livreur");
    const additionalInfoTextarea = document.getElementById("informations_supp");

    const errorContainer = document.createElement("div");
    errorContainer.className = "alert alert-danger mt-3";
    errorContainer.style.display = "none";
    document.getElementById("retourForm").prepend(errorContainer);

    factureSelect.addEventListener("change", function () {
        const factureId = this.value;
        commandSelect.innerHTML = '<option value="" disabled>Loading commands...</option>';

        if (factureId) {
            fetch(`/apps/get_commands/${factureId}/`)
                .then(response => response.json())
                .then(data => {
                    commandSelect.innerHTML = "";
                    data.commands.forEach(command => {
                        const option = document.createElement("option");
                        option.value = command.id;
                        option.textContent = `Command ${command.id} - ${command.description}`;
                        commandSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error("Error fetching commands:", error);
                    commandSelect.innerHTML = '<option value="" disabled>Error loading commands</option>';
                });
        }
    });

    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.style.display = "block";
    }

    function clearError() {
        errorContainer.style.display = "none";
        errorContainer.textContent = "";
    }

    submitButton.addEventListener("click", function (event) {
        event.preventDefault();
        clearError();

        if (!factureSelect.value) { showError("Please select a facture."); return; }
        if (Array.from(commandSelect.selectedOptions).length === 0) { showError("Please select at least one command."); return; }
        if (!supplierSelect.value) { showError("Please select a supplier."); return; }
        if (!reasonInput.value.trim()) { showError("Please provide a reason for the return."); return; }
        if (!dateInput.value) { showError("Please select a return date."); return; }
        if (!deliveryPersonSelect.value) { showError("Please select a delivery person."); return; }

        const payload = {
            facture: factureSelect.value,
            selected_commands: Array.from(commandSelect.selectedOptions).map(o => o.value),
            supplier: supplierSelect.value,
            raison_retour: reasonInput.value.trim(),
            date_retour: dateInput.value,
            livreur: deliveryPersonSelect.value,
            informations_supp: additionalInfoTextarea.value.trim(),
        };

        fetch("/apps/add_retour", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify(payload),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) alert("Return processed successfully.");
            else showError(`Error: ${data.message}`);
        })
        .catch(error => { console.error("Error submitting the form:", error); });
    });
});
