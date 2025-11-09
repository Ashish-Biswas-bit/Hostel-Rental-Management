// UI Functionality
class UIManager {
    constructor() {
        this.initializeNavigation();
        this.initializeScrollEffects();
        this.initializeContactForm();
        this.initializeNewsletterForm();
    }

    initializeNavigation() {
        // Mobile menu toggle
        const menuBtn = document.querySelector('.menuBtn');
        const navLinks = document.querySelector('.navLinks');
        
        if(menuBtn && navLinks) {
            menuBtn.addEventListener('click', () => {
                navLinks.classList.toggle('active');
            });
        }

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if(target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                    navLinks.classList.remove('active'); // Close mobile menu
                }
            });
        });
    }

    initializeScrollEffects() {
        // Navbar scroll effect
        const navbar = document.querySelector('.navbar');
        if(navbar) {
            window.addEventListener('scroll', () => {
                if(window.scrollY > 100) {
                    navbar.style.background = 'rgba(255,255,255,0.95)';
                    navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
                } else {
                    navbar.style.background = 'white';
                    navbar.style.boxShadow = 'none';
                }
            });
        }

        // Animate elements on scroll
        const animateOnScroll = () => {
            const elements = document.querySelectorAll('.featureCard, .statItem, .adCard');
            elements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                if (elementTop < window.innerHeight - 50) {
                    element.style.opacity = '1';
                    element.style.transform = 'translateY(0)';
                }
            });
        };

        window.addEventListener('scroll', animateOnScroll);
        window.addEventListener('load', animateOnScroll);
    }

    initializeContactForm() {
        const contactForm = document.querySelector('.contactForm');
        if(contactForm) {
            contactForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                // Add contact form submission logic here
                alert('Thank you for your message. We will get back to you soon!');
                contactForm.reset();
            });
        }
    }

    initializeListingsGallery() {
        const btn = document.getElementById('listPropertyBtn');
        const gallery = document.getElementById('listingsGallery');
        const grid = document.getElementById('galleryGrid');

        const renderGallery = (ads) => {
            if(!grid) return;
            grid.innerHTML = '';
            (ads || []).forEach(ad => {
                const card = document.createElement('div');
                card.className = 'thumbCard fade-in';
                card.tabIndex = 0;
                card.innerHTML = `
                    <img src="${ad.image_path || '/static/uploads/edit.jpg'}" alt="${(ad.title||'Property')}">
                    <div class="thumbOverlay">${ad.location || 'Unknown'}</div>
                `;
                card.addEventListener('click', () => {
                    // scroll to full ads area and open modal if possible
                    const allAds = document.getElementById('adsContainer');
                    if(allAds) {
                        // find the corresponding card by title/location and focus it
                        const match = Array.from(allAds.querySelectorAll('.adCard')).find(c => (c.dataset.title||'').toLowerCase().includes((ad.title||ad.location||'').toLowerCase()));
                        if(match) {
                            match.scrollIntoView({behavior:'smooth', block:'center'});
                            try { match.focus({preventScroll:true}); } catch(e){}
                        }
                    }
                });
                grid.appendChild(card);
            });
        };

        // Populate initially from window.adsData if available
        if(window.adsData) renderGallery(window.adsData);

        // click opens the gallery section
        if(btn && gallery) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                // ensure gallery is visible
                gallery.classList.remove('hidden');
                gallery.scrollIntoView({behavior:'smooth', block:'start'});
            });
        }

        // Poll the server for updates every 15s (keeps gallery in sync when admin posts)
        const fetchAds = async () => {
            try {
                const res = await fetch('/api/ads');
                if(!res.ok) return;
                const data = await res.json();
                if(!Array.isArray(data)) return;
                // check for changes (simple length check + first id)
                const current = window.adsData || [];
                if(data.length !== current.length || (data[0] && current[0] && data[0].id !== current[0].id)) {
                    window.adsData = data;
                    // refresh full listings if available
                    if(window.listingsManager && typeof window.listingsManager.refresh === 'function') {
                        window.listingsManager.refresh(data);
                    }
                    renderGallery(data);
                }
            } catch (err) {
                // silent
            }
        };
        // start polling
        setInterval(fetchAds, 15000);
    }

    initializeNewsletterForm() {
        const newsletter = document.querySelector('.newsletter');
        if(newsletter) {
            newsletter.addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = newsletter.querySelector('input[type="email"]').value;
                // Add newsletter subscription logic here
                alert('Thank you for subscribing to our newsletter!');
                newsletter.reset();
            });
        }
    }
}

// Initialize UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const uiManager = new UIManager();
    // initialize the listings gallery feature (List Property button)
    if(typeof uiManager.initializeListingsGallery === 'function') uiManager.initializeListingsGallery();
});