/**
 * Custom Tags Autocomplete
 * Handles selection of interests/technologies with custom tag creation
 */

class CustomTagsInput {
    constructor(config) {
        this.inputId = config.inputId;
        this.suggestionsId = config.suggestionsId;
        this.tagsListId = config.tagsListId;
        this.hiddenInputId = config.hiddenInputId;
        this.allTags = config.tags || [];
        this.selectedTags = new Set(config.selected || []);

        this.input = document.getElementById(this.inputId);
        this.suggestionsList = document.getElementById(this.suggestionsId);
        this.tagsList = document.getElementById(this.tagsListId);
        this.hiddenInput = document.getElementById(this.hiddenInputId);

        this.init();
    }

    init() {
        if (!this.input) return;

        // Zobraz existující vybrané tagy
        this.renderTags();
        // Aktualizuj skryté pole s dříve vybranými tagy
        this.updateHiddenInput();

        // Autocomplete na input
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    handleInput(e) {
        const value = e.target.value.trim().toLowerCase();

        if (!value) {
            this.suggestionsList.style.display = 'none';
            return;
        }

        // Filtruj tagy
        const matches = this.allTags.filter(tag =>
            tag.name.toLowerCase().includes(value) &&
            !this.selectedTags.has(tag.name)
        );

        if (matches.length === 0 && value.length > 0) {
            // Nabídni vytvoření nového tagu
            this.showSuggestions([{ name: `+ Vytvořit "${value}"`, isNew: true, originalName: value }]);
        } else {
            this.showSuggestions(matches);
        }
    }

    handleKeydown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const value = this.input.value.trim();

            if (value) {
                this.addTag(value);
                this.input.value = '';
                this.suggestionsList.style.display = 'none';
            }
        }

        if (e.key === 'Escape') {
            this.suggestionsList.style.display = 'none';
        }
    }

    showSuggestions(tags) {
        this.suggestionsList.innerHTML = '';

        if (tags.length === 0) {
            this.suggestionsList.style.display = 'none';
            return;
        }

        tags.forEach(tag => {
            const suggestion = document.createElement('div');
            suggestion.className = 'suggestion-item p-2 cursor-pointer';
            suggestion.textContent = tag.name;

            if (tag.isNew) {
                suggestion.classList.add('bg-info', 'text-white');
            } else {
                suggestion.classList.add('border-bottom');
                // Zobraz typ tagu (SYSTEM nebo USER)
                const type = document.createElement('small');
                type.className = 'ms-2 text-muted';
                type.textContent = `(${tag.type || 'SYSTEM'})`;
                suggestion.appendChild(type);
            }

            suggestion.addEventListener('click', () => {
                const tagName = tag.isNew ? tag.originalName : tag.name;
                this.addTag(tagName);
                this.input.value = '';
                this.suggestionsList.style.display = 'none';
            });

            this.suggestionsList.appendChild(suggestion);
        });

        this.suggestionsList.style.display = 'block';
    }

    addTag(tagName) {
        if (!tagName || this.selectedTags.has(tagName)) {
            return;
        }

        this.selectedTags.add(tagName);
        this.renderTags();
        this.updateHiddenInput();
    }

    removeTag(tagName) {
        this.selectedTags.delete(tagName);
        this.renderTags();
        this.updateHiddenInput();
    }

    renderTags() {
        this.tagsList.innerHTML = '';

        this.selectedTags.forEach(tagName => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-primary me-2 mb-2 p-2';

            const text = document.createElement('span');
            text.textContent = tagName;

            const closeBtn = document.createElement('button');
            closeBtn.type = 'button';
            closeBtn.className = 'btn-close btn-close-white ms-2';
            closeBtn.style.fontSize = '0.8rem';
            closeBtn.setAttribute('aria-label', 'Odebrat');
            closeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.removeTag(tagName);
            });

            badge.appendChild(text);
            badge.appendChild(closeBtn);
            this.tagsList.appendChild(badge);
        });
    }

    updateHiddenInput() {
        this.hiddenInput.value = Array.from(this.selectedTags).join(',');
    }
}

// Inicializace při načtení stránky
document.addEventListener('DOMContentLoaded', function() {
    // Inicializuj interests
    const interestsConfig = window.interestsConfig;
    if (interestsConfig && document.getElementById(interestsConfig.inputId)) {
        window.interestsInput = new CustomTagsInput(interestsConfig);
    }

    // Inicializuj technologies
    const technologiesConfig = window.technologiesConfig;
    if (technologiesConfig && document.getElementById(technologiesConfig.inputId)) {
        window.technologiesInput = new CustomTagsInput(technologiesConfig);
    }
});
