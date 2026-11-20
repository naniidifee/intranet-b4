function cargarNoticiasLiceo() {
  const grid = document.getElementById('liceo-news-grid');
  if (!grid) return;

  let noticias = [];
  try {
    noticias = JSON.parse(localStorage.getItem('avb_news') || '[]');
  } catch (e) {
    noticias = [];
  }

  // Filtrar solo las publicadas (ignora borradores)
  const publicadas = noticias.filter(n => n.estado === 'publicada');

  // Si aún no hay noticias guardadas, cargamos unas por defecto del Liceo
  if (publicadas.length === 0) {
    publicadas.push(
      {
        id: 1,
        titulo: 'Liceo AVB obtiene reconocimiento regional por excelencia técnica',
        categoria: 'Logros Institucionales',
        descripcion: 'Nuestra institución fue distinguida por el Servicio Local de Educación Pública "Chinchorro" por los destacados resultados en las pruebas de certificación técnica.',
        contenido: 'La comunidad educativa del Liceo Bicentenario Antonio Varas de la Barra celebra este importante reconocimiento fruto del compromiso de docentes y estudiantes.',
        fecha: '2026-11-10',
        destacada: 'si',
        img: 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800&q=80',
        autor: 'Prof. Carla Flores M.'
      },
      {
        id: 2,
        titulo: 'Estudiantes de Gastronomía representan a Arica en concurso nacional',
        categoria: 'Gastronomía',
        descripcion: 'Cuatro alumnos de 4° Medio compitieron con una propuesta de cocina andina fusión que cautivó al jurado.',
        contenido: 'Nuestros estudiantes demostraron todo lo aprendido en los talleres de especialidad rescatando productos típicos de la región de Arica y Parinacota.',
        fecha: '2026-11-05',
        destacada: 'no',
        img: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80',
        autor: 'Prof. Carla Flores M.'
      },
      {
        id: 3,
        titulo: 'Feria Técnico Profesional AVB conecta a estudiantes con empresas locales',
        categoria: 'Administración',
        descripcion: 'Más de 20 empresas e instituciones de educación superior participaron en la jornada de orientación y prácticas.',
        contenido: 'Una exitosa jornada vivieron los estudiantes de 3° y 4° medio al conocer de primera fuente las oportunidades de práctica profesional.',
        fecha: '2026-10-28',
        destacada: 'no',
        img: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&q=80',
        autor: 'Prof. Carla Flores M.'
      },
      {
        id: 4,
        titulo: 'Olimpiadas de Programación y Robótica reúnen a jóvenes talentos del liceo',
        categoria: 'Programación',
        descripcion: 'Equipos de Informática y Electrónica presentaron prototipos tecnológicos desarrollados durante el semestre.',
        contenido: 'Los proyectos destacados abordaron soluciones de automatización y desarrollo web creadas íntegramente en los laboratorios del establecimiento.',
        fecha: '2026-10-15',
        destacada: 'no',
        img: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80',
        autor: 'Prof. Carla Flores M.'
      }
    );
  }

  // Buscar la marcada como destacada ('si'), o tomar la más reciente
  const destacada = publicadas.find(n => n.destacada === 'si') || publicadas[0];
  // Tomar hasta 3 noticias secundarias distintas a la destacada
  const secundarias = publicadas.filter(n => n.id !== destacada.id).slice(0, 3);

  // Renderizar columna izquierda (Destacada) + columna derecha (3 tarjetas)
  grid.innerHTML = `
    <article class="news-featured-card" data-id="${destacada.id}">
      <img src="${destacada.img}" alt="${destacada.titulo}" class="news-featured-img">
      <h3 class="news-featured-title">${destacada.titulo}</h3>
      <p class="news-featured-desc">${destacada.descripcion}</p>
    </article>

    <div class="news-side-list">
      ${secundarias.map(n => `
        <article class="news-side-card" data-id="${n.id}">
          <img src="${n.img}" alt="${n.titulo}" class="news-side-img">
          <div class="news-side-body">
            <h4 class="news-side-title">${n.titulo}</h4>
            <span class="news-ver-mas">Ver más &rsaquo;</span>
          </div>
        </article>
      `).join('')}
    </div>
  `;

  // Asignar eventos de clic sin usar onclick en el HTML
  grid.querySelectorAll('[data-id]').forEach(card => {
    card.addEventListener('click', () => {
      const id = Number(card.getAttribute('data-id'));
      abrirDetalleNoticia(id, publicadas);
    });
  });
}

function abrirDetalleNoticia(id, lista) {
  const n = lista.find(item => item.id === id);
  if (!n) return;

  document.getElementById('modalNewsImg').src = n.img;
  document.getElementById('modalNewsCat').textContent = n.categoria || 'Noticias AVB';
  document.getElementById('modalNewsDate').innerHTML = `<i class="fa-regular fa-calendar"></i> ${n.fecha}`;
  document.getElementById('modalNewsAuthor').innerHTML = `<i class="fa-regular fa-user"></i> ${n.autor || 'Comunicaciones AVB'}`;
  document.getElementById('modalNewsTitle').textContent = n.titulo;
  document.getElementById('modalNewsDesc').textContent = n.descripcion;
  document.getElementById('modalNewsContent').textContent = n.contenido || n.descripcion;

  document.getElementById('newsModal').classList.add('open');
}

function cerrarModalNoticia() {
  const modal = document.getElementById('newsModal');
  if (modal) modal.classList.remove('open');
}

// Inicializar eventos al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
  cargarNoticiasLiceo();

  // Cerrar modal al hacer clic en el fondo oscuro o en la X
  const modal = document.getElementById('newsModal');
  const btnClose = document.getElementById('closeNewsModal');
  
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) cerrarModalNoticia();
    });
  }
  if (btnClose) {
    btnClose.addEventListener('click', cerrarModalNoticia);
  }
});

// Actualizar en vivo si se publica desde comunicaciones.html en otra pestaña
window.addEventListener('storage', (e) => {
  if (e.key === 'avb_news') cargarNoticiasLiceo();
});