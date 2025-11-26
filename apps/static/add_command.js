document.addEventListener("DOMContentLoaded", function () {
    const variantData = JSON.parse(document.getElementById("commandForm").dataset.variantData);
    const orderLinesContainer = document.getElementById("orderLinesContainer");
    const addRowButton = document.getElementById("addRowButton");
    const removeRowButton = document.getElementById("removeRowButton");
    const variantCombinationsInput = document.getElementById("variant_combinations");

    let rowCount = 0;

    function renderVariantOptions(productId, rowId) {
        const variantGroup = document.getElementById(`variant_group_${rowId}`);
        variantGroup.innerHTML = "";

        const variants = variantData[productId];
        if (variants) {
            Object.entries(variants).forEach(([variantName, variantValues]) => {
                const label = document.createElement("label");
                label.textContent = `Select ${variantName}:`;
                label.classList.add("form-label");

                const select = document.createElement("select");
                select.classList.add("form-select", "mb-2");
                select.setAttribute("data-variant-name", variantName);
                select.innerHTML = '<option value="" disabled selected>Choose an option</option>';

                variantValues.forEach(value => {
                    const option = document.createElement("option");
                    option.value = value;
                    option.textContent = value;
                    select.appendChild(option);
                });

                variantGroup.appendChild(label);
                variantGroup.appendChild(select);
            });
        } else {
            variantGroup.innerHTML = '<p class="text-muted">No variants available for this product.</p>';
        }
    }

    function addRow() {
        const rowId = rowCount++;
        const row = document.createElement("div");
        row.classList.add("order-line-row", "mb-3");
        row.id = `row_${rowId}`;

        row.innerHTML = `
            <label for="product_${rowId}" class="form-label">Product:</label>
            <select id="product_${rowId}" class="form-select mb-3" name="product_${rowId}" required>
                <option value="" disabled selected>Choose a product</option>
                {% for product in items %}
                <option value="{{ product.pk }}">{{ product.product_name }}</option>
                {% endfor %}
            </select>

            <div id="variant_group_${rowId}" class="variant-group mb-3"></div>

            <label for="quantity_${rowId}" class="form-label">Quantity:</label>
            <input type="number" id="quantity_${rowId}" class="form-control mb-3" name="quantity_${rowId}" min="1" required>
        `;

        orderLinesContainer.appendChild(row);

        document.getElementById(`product_${rowId}`).addEventListener("change", function () {
            renderVariantOptions(this.value, rowId);
        });
    }

    function removeRow() {
        if (rowCount > 0) {
            rowCount--;
            const lastRow = orderLinesContainer.lastElementChild;
            if (lastRow) orderLinesContainer.removeChild(lastRow);
        }
    }

    function updateVariantCombinations() {
        const combinations = [];
        document.querySelectorAll(".order-line-row").forEach(row => {
            const rowId = row.id.split("_")[1];
            const productId = document.getElementById(`product_${rowId}`).value;
            const quantity = document.getElementById(`quantity_${rowId}`).value;
            const variants = {};

            row.querySelectorAll("select[data-variant-name]").forEach(select => {
                const variantName = select.getAttribute("data-variant-name");
                const variantValue = select.value;
                if (variantName && variantValue) variants[variantName] = variantValue;
            });

            if (productId && quantity) {
                combinations.push({
                    product: productId,
                    quantity: parseInt(quantity),
                    variant_combination: variants,
                });
            }
        });

        variantCombinationsInput.value = JSON.stringify(combinations);
    }

    addRowButton.addEventListener("click", addRow);
    removeRowButton.addEventListener("click", removeRow);
    document.getElementById("commandForm").addEventListener("change", updateVariantCombinations);
});
