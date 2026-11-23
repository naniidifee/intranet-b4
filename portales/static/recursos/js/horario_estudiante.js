document.addEventListener("DOMContentLoaded", function () {
    const enlacesMenu = document.querySelectorAll("[data-seccion]");
    const paneles = document.querySelectorAll(".pagina-estudiante");

    enlacesMenu.forEach(function (enlace) {
        enlace.addEventListener("click", function (evento) {
            evento.preventDefault();

            const idSeccion = enlace.dataset.seccion;
            const panelDestino = document.getElementById(idSeccion);

            if (!panelDestino) {
                return;
            }

            paneles.forEach(function (panel) {
                panel.classList.remove("activa");
            });

            enlacesMenu.forEach(function (item) {
                item.classList.remove("activo");
            });

            panelDestino.classList.add("activa");
            enlace.classList.add("activo");
        });
    });
    
});