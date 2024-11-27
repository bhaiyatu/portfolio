document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchProjects');
    const clearButton = document.getElementById('clearSearch');
    const projectCards = document.querySelectorAll('.project-card').length > 0;

    if (searchInput && projectCards) {
        function performSearch() {
            const searchTerm = searchInput.value.toLowerCase();
            const projects = document.querySelectorAll('.project-card');
            let hasResults = false;

            projects.forEach(project => {
                const projectContainer = project.closest('.col-md-6');
                const title = project.querySelector('.card-title').textContent.toLowerCase();
                const description = project.querySelector('.card-text').textContent.toLowerCase();
                const technologies = Array.from(project.querySelectorAll('.badge'))
                    .map(badge => badge.textContent.toLowerCase());

                const matches = title.includes(searchTerm) || 
                              description.includes(searchTerm) || 
                              technologies.some(tech => tech.includes(searchTerm));

                projectContainer.style.display = matches ? 'block' : 'none';
                if (matches) hasResults = true;
            });

            // Show/hide no results message
            const noResultsMsg = document.getElementById('noResultsMessage');
            if (noResultsMsg) {
                noResultsMsg.style.display = hasResults ? 'none' : 'block';
            }
        }

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