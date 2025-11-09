// Property listings functionality
class ListingsManager {
    constructor(adsData) {
        this.adsData = adsData;
        this.container = document.getElementById("adsContainer");
        this.searchInput = document.getElementById("searchInput");
        this.filterSelect = document.getElementById("filterSelect");
        
        this.initializeListings();
        this.initializeFilters();
        this.updateStats();
    }

    initializeListings() {
        this.adsData.forEach(ad => {
            const card = this.createAdCard(ad);
            this.container.appendChild(card);
        });
    }

    createAdCard(ad) {
        const card = document.createElement("article");
        card.className = "adCard";
        card.tabIndex = 0;
        // Set searchable data attributes
        card.dataset.title = ((ad.title || '') + ' ' + (ad.location || '')).trim();
        card.dataset.type = (ad.type || '').toLowerCase();
    card.dataset.location = (ad.location || '');
    // keep original location string for highlighting/reset
    card.dataset.originalLocation = (ad.location || '');
        card.dataset.category = (ad.category || '').toLowerCase();
        card.dataset.gender = (ad.gender || '').toLowerCase();

        card.innerHTML = `
            <img class="adImage" src="${ad.image_path}" alt="${ad.title}">
            <div class="adBody">
                <div class="cardRow">
                    <div>
                        <h3 class="adTitle">${ad.title}</h3>
                        <div class="adMeta smallMeta">${ad.type || ''} • ${ad.category || ''} • <span class="genderTag">${ad.gender ? (ad.gender.charAt(0).toUpperCase() + ad.gender.slice(1)) : 'Any'}</span></div>
                    </div>
                    <div class="priceBadge">৳${ad.rent}</div>
                </div>
                <div class="adMeta adLocation">${ad.location || ''}</div>
                <p class="adDescription">${(ad.description || '').slice(0,120)}${(ad.description||'').length>120? '...':''}</p>
            </div>
        `;

        // Handle image fallback
        const imgEl = card.querySelector('.adImage');
        if(imgEl) {
            imgEl.onerror = function() {
                this.onerror = null;
                this.src = '/static/uploads/edit.jpg';
            }
        }

        // Add click handlers
        card.addEventListener("click", () => bookingManager.openModal(ad));
        card.addEventListener("keydown", (e) => {
            if(e.key === 'Enter') bookingManager.openModal(ad);
        });

        return card;
    }

    initializeFilters() {
        // debounce helper so we don't run filter on every single keystroke
        const debounce = (fn, wait = 250) => {
            let t = null;
            return (...args) => {
                if (t) clearTimeout(t);
                t = setTimeout(() => fn(...args), wait);
            };
        };

        const applyFilters = (opts = {}) => {
            const doScroll = !!opts.scroll;
            const query = (this.searchInput.value || '').toLowerCase().trim();
            const selectedType = (this.filterSelect.value || '').toLowerCase();
            const genderSelect = document.getElementById('genderSelect');
            const selectedGender = genderSelect ? genderSelect.value.toLowerCase() : '';
            let visibleCount = 0;
            const cards = Array.from(document.querySelectorAll('.adCard'));
            cards.forEach(card => {
                // Get all searchable data
                const title = (card.querySelector('.adTitle')?.textContent || '').toLowerCase();
                const description = (card.querySelector('.adDescription')?.textContent || '').toLowerCase();
                const location = (card.dataset.location || '').toLowerCase();
                const category = (card.dataset.category || '').toLowerCase();
                const type = (card.dataset.type || '').toLowerCase();
                const rent = (card.querySelector('.priceBadge')?.textContent || '').toLowerCase();
                const gender = (card.dataset.gender || '').toLowerCase();

                // Utility: detect if user query looks like an address (has digits or common address tokens)
                const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const isAddressLike = (q) => {
                    if (!q || q.length < 2) return false;
                    if (/\d/.test(q)) return true; // contains a number
                    // common address words (st, street, rd, road, lane, near, opp, block, sector, house)
                    if (/\b(st|street|rd|road|lane|near|opp|opposite|block|sector|house|avenue|ave|bazar)\b/.test(q)) return true;
                    return false;
                };

                const addressQuery = isAddressLike(query);

                // Check if any field matches the search query
                let matchesQuery = false;
                if (query === '') {
                    matchesQuery = true;
                } else if (addressQuery) {
                    // when query looks like an address, only match against location
                    matchesQuery = location.includes(query);
                } else {
                    // general search across many fields (include gender)
                    matchesQuery = title.includes(query) || 
                        description.includes(query) ||
                        location.includes(query) || 
                        category.includes(query) ||
                        type.includes(query) ||
                        rent.includes(query) ||
                        gender.includes(query);
                }

                // Check if type matches filter
                const matchesType = selectedType === '' || type === selectedType;
                // Check if gender matches filter
                const matchesGender = selectedGender === '' || gender === selectedGender || gender === 'any';

                // Show/hide card based on all conditions
                const shouldShow = matchesQuery && matchesType && matchesGender;
                card.style.display = shouldShow ? '' : 'none';
                if (shouldShow) {
                    visibleCount++;
                    // If this was an address-like query, highlight the matching substring in the location element
                    const locationEl = card.querySelector('.adLocation');
                    if (locationEl) {
                        const original = card.dataset.originalLocation || (card.dataset.location || '');
                        if (addressQuery && query !== '') {
                            try {
                                const re = new RegExp(escapeRegExp(query), 'ig');
                                const highlighted = original.replace(re, (m) => `<mark class="search-highlight">${m}</mark>`);
                                locationEl.innerHTML = highlighted;
                            } catch (e) {
                                locationEl.textContent = original; // fallback
                            }
                        } else {
                            // reset to original location text when not addressing
                            locationEl.textContent = original;
                        }
                    }
                }
            });

            // Show message if no results
            let noResultsMsg = document.getElementById('noResultsMessage');
            if (visibleCount === 0) {
                if (!noResultsMsg) {
                    noResultsMsg = document.createElement('div');
                    noResultsMsg.id = 'noResultsMessage';
                    noResultsMsg.className = 'no-results';
                    noResultsMsg.innerHTML = `
                        <div class="no-results-content">
                            <i class="fas fa-search" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                            <h3>No Results Found</h3>
                            <p>Try adjusting your search or filter to find what you're looking for.</p>
                        </div>
                    `;
                    this.container.appendChild(noResultsMsg);
                }
                noResultsMsg.style.display = 'block';

                // Scroll no-results message into view only if caller requested scroll
                if (doScroll) {
                    setTimeout(() => {
                        noResultsMsg.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 50);
                }
            } else {
                if (noResultsMsg) noResultsMsg.style.display = 'none';

                // Scroll the first visible card into view so user doesn't have to scroll
                const firstVisible = cards.find(c => c.style.display !== 'none');
                if (firstVisible && doScroll) {
                    // Small timeout to allow layout changes to settle
                    setTimeout(() => {
                        const navbarOffset = document.querySelector('.navbar') ? document.querySelector('.navbar').offsetHeight + 12 : 12;
                        const rect = firstVisible.getBoundingClientRect();
                        const absoluteTop = window.pageYOffset + rect.top - navbarOffset;
                        window.scrollTo({ top: absoluteTop, behavior: 'smooth' });
                        try { firstVisible.focus({ preventScroll: true }); } catch(e) {}
                    }, 60);
                }
            }
        };

    // Use debounced input so results appear after user pauses typing
    const debouncedApply = debounce(() => applyFilters({ scroll: false }), 300);
    this.searchInput.addEventListener('input', debouncedApply);
    // Also apply and scroll when user presses Enter
    this.searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') applyFilters({ scroll: true }); });
        this.filterSelect.addEventListener('change', applyFilters);

    // Search button (if present) should apply filters and scroll
    const searchBtn = document.querySelector('.searchBtn');
    if (searchBtn) searchBtn.addEventListener('click', (e) => { e.preventDefault(); applyFilters({ scroll: true }); });

        // Run initially to ensure page state matches default filters
        setTimeout(applyFilters, 100);
    }

    updateStats() {
        // Update statistics if elements exist
        const stats = {
            totalAds: this.adsData.length,
            hostels: this.adsData.filter(a => (a.type || '').toLowerCase() === 'hostel').length,
            flats: this.adsData.filter(a => (a.type || '').toLowerCase() === 'flat').length,
            withImage: this.adsData.filter(a => a.image_path).length
        };

        Object.entries(stats).forEach(([key, value]) => {
            const el = document.getElementById(key);
            if(el) el.textContent = value;
        });
    }
}

// Initialize listings when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const listingsManager = new ListingsManager(window.adsData);
    // expose globally so other modules can refresh when data updates
    window.listingsManager = listingsManager;
    // add refresh helper for dynamic updates
    ListingsManager.prototype.refresh = function(newAds) {
        if (Array.isArray(newAds)) this.adsData = newAds;
        // clear existing cards
        this.container.innerHTML = '';
        this.initializeListings();
        this.updateStats();
    };
});