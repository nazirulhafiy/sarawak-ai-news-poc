(() => {
  const filter = document.querySelector("[data-category-filter]");
  const storyList = document.querySelector("[data-story-list]");

  if (!filter || !storyList) return;

  const buttons = Array.from(filter.querySelectorAll("[data-section-filter]"));
  const stories = Array.from(storyList.querySelectorAll(".story-card"));
  const status = filter.querySelector("[data-filter-status]");

  function applyFilter(section) {
    const activeButton = buttons.find((button) => button.dataset.sectionFilter === section);
    if (!activeButton) return;

    let visibleCount = 0;
    stories.forEach((story) => {
      const isVisible = section === "all" || story.dataset.section === section;
      story.hidden = !isVisible;

      if (isVisible) {
        visibleCount += 1;
        const rank = story.querySelector(".story-rank");
        if (rank) {
          rank.textContent = String(visibleCount);
          rank.setAttribute("aria-label", section === "all" ? `Chronological item ${visibleCount}` : `Filtered item ${visibleCount}`);
        }
      }
    });

    buttons.forEach((button) => {
      const isActive = button === activeButton;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });

    if (status) {
      status.textContent = section === "all"
        ? `Showing all ${visibleCount} stories`
        : `Showing ${visibleCount} ${activeButton.dataset.filterLabel} stories`;
    }
  }

  filter.hidden = false;
  filter.addEventListener("click", (event) => {
    const button = event.target.closest("[data-section-filter]");
    if (button && filter.contains(button)) applyFilter(button.dataset.sectionFilter);
  });
  applyFilter("all");
})();
