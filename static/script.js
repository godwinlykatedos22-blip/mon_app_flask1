// ==============================
// SCRIPT GLOBAL
// ==============================

// Confirmation avant suppression d’un élément
document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".btn-danger");

    deleteButtons.forEach((btn) => {
        btn.addEventListener("click", function (event) {
            const confirmDelete = confirm("Voulez-vous vraiment supprimer cet élément ?");
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });

    // Disparition automatique des alertes après 4 secondes
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length) {
        setTimeout(() => {
            alerts.forEach(alert => alert.remove());
        }, 4000);
    }
});
