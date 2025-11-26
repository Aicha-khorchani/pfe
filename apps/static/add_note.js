document.addEventListener("DOMContentLoaded", function () {
    // Elements for add/edit note forms
    const addNoteForm = document.getElementById("AddNoteForm");
    const editNoteForm = document.getElementById("editNoteForm");

    // Helper function: clear validation errors
    function clearErrors(form) {
        form.querySelectorAll(".is-invalid").forEach((field) => {
            field.classList.remove("is-invalid");
            const feedback = field.parentElement.querySelector(".invalid-feedback");
            if (feedback) feedback.remove();
        });
    }

    // Helper function: show error on a field
    function showError(field, message) {
        field.classList.add("is-invalid");
        const errorDiv = document.createElement("div");
        errorDiv.classList.add("invalid-feedback");
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }

    // Function to handle customer-command logic
    function setupCustomerCommandForm(form, customerFieldId, commandFieldId, fetchUrlBase) {
        const customerField = document.getElementById(customerFieldId);
        const commandField = document.getElementById(commandFieldId);

        if (!customerField || !commandField) return;

        // Fetch commands for selected customer
        customerField.addEventListener("change", function () {
            const customerId = this.value;
            commandField.innerHTML = '<option value="" disabled selected>Loading...</option>';

            if (customerId) {
                fetch(`${fetchUrlBase}${customerId}/`)
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
                        console.error("Error fetching commands:", error);
                        showError(customerField, "Network error. Please try again.");
                    });
            }
        });

        // Optional: fetch commands if customer pre-selected
        if (customerField.value) {
            customerField.dispatchEvent(new Event("change"));
        }

        // Form validation before submit
        form.addEventListener("submit", function (event) {
            clearErrors(form);
            let hasErrors = false;

            if (!customerField.value) {
                showError(customerField, "Please select a customer.");
                hasErrors = true;
            }

            if (!commandField.value) {
                showError(commandField, "Please select a command.");
                hasErrors = true;
            }

            if (hasErrors) event.preventDefault();
        });
    }

    // Setup both forms
    if (addNoteForm) {
        setupCustomerCommandForm(addNoteForm, "customer_id", "command_id", "/apps/add_note/?customer_id=");
    }

    if (editNoteForm) {
        setupCustomerCommandForm(editNoteForm, "customer_id", "command", "/apps/get_commands_by_customer/");
    }
});
