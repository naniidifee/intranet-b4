document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("newsSearchInput");
  const cards = document.querySelectorAll(".avb-news-row-card");
  const noResultsMsg = document.getElementById("noSearchResults");

  if (!searchInput) return;

  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase().trim();
    let visibleCount = 0;

    cards.forEach((card) => {
      const title = card.getAttribute("data-title") || "";
      const matches = title.includes(query);
      card.style.display = matches ? "flex" : "none";
      if (matches) visibleCount++;
    });

    if (noResultsMsg && cards.length > 0) {
      noResultsMsg.classList.toggle("is-hidden", visibleCount > 0);
    }
  });
});