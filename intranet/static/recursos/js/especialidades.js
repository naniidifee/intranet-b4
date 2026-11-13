// Función para controlar las pestañas (tabs) de la vista de especialidades
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  
  // Ocultar todos los contenidos de las pestañas
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].classList.remove("active");
  }
  
  // Quitar la clase 'active' de todos los botones de las pestañas
  tablinks = document.getElementsByClassName("tab-btn");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove("active");
  }
  
  // Mostrar la pestaña actual y activar su botón correspondiente
  document.getElementById(tabName).classList.add("active");
  evt.currentTarget.classList.add("active");
}