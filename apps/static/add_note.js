document.addEventListener("DOMContentLoaded", function () {
    const customerField = document.getElementById("customer_id");
    const commandField = document.getElementById("command_id");
    const form = document.getElementById("AddNoteForm");

    // Clear previous validation errors
    function clearErrors() {
        form.querySelectorAll(".is-invalid").forEach((field) => {
            field.classList.remove("is-invalid");
            const feedback = field.parentElement.querySelector(".invalid-feedback");
            if (feedback) feedback.remove();
        });
    }

    // Show validation error for a field
    function showError(field, message) {
        field.classList.add("is-invalid");
        const errorDiv = document.createElement("div");
        errorDiv.classList.add("invalid-feedback");
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }

    // Fetch commands when customer changes
    customerField.addEventListener("change", function () {
        const customerId = this.value;
        commandField.innerHTML = '<option value="" disabled selected>Loading...</option>';

        if (customerId) {
            fetch(`/apps/add_note/?customer_id=${customerId}`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        if (data.commands.length > 0) {
                            commandField.innerHTML = '<option value="" disabled selected>Select a command</option>';
                            data.commands.forEach((command) => {
                                const option = document.createElement("option");
                                option.value = command.id;
                                option.textContent = command.label;
                                commandField.appendChild(option);
                            });
                        } else {
                            commandField.innerHTML = '<option value="" disabled>No commands available</option>';
                        }
                    } else {
                        showError(customerField, "Unable to fetch commands. Try again.");
                    }
                })
                .catch((error) => {
                    showError(customerField, "Network error. Please try again.");
                });
        }
    });

    // Form validation before submit
    form.addEventListener("submit", function (event) {
        clearErrors(); 
        let hasErrors = false;

        if (!customerField.value) {
            showError(customerField, "Please select a customer.");
            hasErrors = true;
        }

        if (!commandField.value) {
            showError(commandField, "Please select a command.");
            hasErrors = true;
        }

        if (hasErrors) {
            event.preventDefault(); 
        }
    });
});
