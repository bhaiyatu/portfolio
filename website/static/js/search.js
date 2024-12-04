document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchProjects');
    const clearButton = document.getElementById('clearSearch');
    const projectCards = document.querySelectorAll('.project-card');

    if (searchInput && projectCards.length > 0) {
        function performSearch() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            let hasResults = false;

            projectCards.forEach(card => {
                const projectContainer = card.closest('.col-md-4');
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const description = card.querySelector('.card-text').textContent.toLowerCase();
                const technologies = Array.from(card.querySelectorAll('.badge'))
                    .map(badge => badge.textContent.toLowerCase());

                const matches = title.includes(searchTerm) || 
                              description.includes(searchTerm) || 
                              technologies.some(tech => tech.includes(searchTerm));

                // Apply animation classes
                if (matches) {
                    projectContainer.style.display = 'block';
                    card.style.opacity = '1';
                    card.style.transform = 'scale(1)';
                    hasResults = true;
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        projectContainer.style.display = 'none';
                    }, 300); // Match this with CSS transition duration
                }
            });

            // Show/hide no results message with animation
            const noResultsMsg = document.getElementById('noResultsMessage');
            if (noResultsMsg) {
                if (!hasResults && searchTerm !== '') {
                    noResultsMsg.style.display = 'block';
                    setTimeout(() => {
                        noResultsMsg.style.opacity = '1';
                    }, 10);
                } else {
                    noResultsMsg.style.opacity = '0';
                    setTimeout(() => {
                        noResultsMsg.style.display = 'none';
                    }, 300);
                }
            }
        }

        // Add event listeners
        searchInput.addEventListener('input', performSearch);

        if (clearButton) {
            clearButton.addEventListener('click', function() {
                searchInput.value = '';
                performSearch();
                searchInput.focus();
            });
        }
    }
}); 