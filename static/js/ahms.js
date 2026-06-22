(function () {
    "use strict";

    function initToasts() {
        document.querySelectorAll(".toast").forEach(function (toastElement) {
            var toast = bootstrap.Toast.getOrCreateInstance(toastElement, {
                autohide: true,
                delay: 4000
            });
            toast.show();
        });
    }

    function confirmDelete(url, name) {
        var modalElement = document.getElementById("confirmActionModal");
        var form = document.getElementById("confirmActionForm");
        var nameElement = document.getElementById("confirmActionName");

        if (!modalElement || !form) {
            return;
        }

        form.setAttribute("action", url);
        if (nameElement) {
            nameElement.textContent = name || "this item";
        }

        bootstrap.Modal.getOrCreateInstance(modalElement).show();
    }

    function debounce(fn, wait) {
        var timeoutId;
        return function () {
            var context = this;
            var args = arguments;
            window.clearTimeout(timeoutId);
            timeoutId = window.setTimeout(function () {
                fn.apply(context, args);
            }, wait || 300);
        };
    }

    function formatCurrency(n) {
        var value = Number(n || 0);
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }

    document.addEventListener("DOMContentLoaded", initToasts);

    window.AHMS = window.AHMS || {};
    window.AHMS.initToasts = initToasts;
    window.AHMS.confirmDelete = confirmDelete;
    window.AHMS.debounce = debounce;
    window.AHMS.formatCurrency = formatCurrency;

    window.initToasts = initToasts;
    window.confirmDelete = confirmDelete;
    window.debounce = debounce;
    window.formatCurrency = formatCurrency;
})();
