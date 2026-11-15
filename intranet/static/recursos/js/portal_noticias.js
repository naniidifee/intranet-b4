document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('newsSearchInput');
  const filterButtons = document.querySelectorAll('.filter-pill');
  const grid = document.getElementById('liceo-news-grid');
  const noMsg = document.getElementById('noNewsMessage');

  if (!searchInput || !grid) return;

  let activeCategory = 'todas';

  function filtrarTarjetas() {
    const query = searchInput.value.toLowerCase().trim();
    const cards = grid.children;
    let visibleCount = 0;

    Array.from(cards).forEach(card => {
      const text = card.innerText.toLowerCase();
      const matchesSearch = text.includes(query);
      const matchesCat = activeCategory === 'todas' || text.includes(activeCategory.toLowerCase());

      if (matchesSearch && matchesCat) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (noMsg) {
      noMsg.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  searchInput.addEventListener('input', filtrarTarjetas);

  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.dataset.category;
      filtrarTarjetas();
    });
  });
});