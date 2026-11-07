/**
 * Apex Federal Bank - Interactive Client-Side Utilities
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Auto-format card number inputs with 4-digit hyphens
    const cardInputs = document.querySelectorAll(".card-formatter");
    cardInputs.forEach(input => {
        input.addEventListener("input", (e) => {
            let val = e.target.value.replace(/\D/g, "");
            val = val.substring(0, 16);
            let formatted = val.match(/.{1,4}/g)?.join("-") || val;
            e.target.value = formatted;
        });
    });

    // 2. Click to copy account numbers
    const copyBtns = document.querySelectorAll(".btn-copy");
    copyBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const textToCopy = btn.getAttribute("data-copy");
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const originalText = btn.innerHTML;
                    btn.innerHTML = "✔ Copied!";
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                    }, 2000);
                });
            }
        });
    });

    // 3. Quick preset transfer buttons
    const presetPills = document.querySelectorAll(".preset-amount-pill");
    const amountField = document.getElementById("transfer-amount-input");
    if (presetPills && amountField) {
        presetPills.forEach(pill => {
            pill.addEventListener("click", () => {
                const amt = pill.getAttribute("data-amt");
                amountField.value = amt;
            });
        });
    }

    // 4. Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = "0";
            alert.style.transition = "opacity 0.5s ease";
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });
});
