// Booking functionality
class BookingManager {
    constructor() {
        this.currentAdId = null;
        this.modal = document.getElementById("modal");
        this.closeModal = document.getElementById("closeModal");
        this.closeModalSecondary = document.getElementById("closeModalSecondary");
        this.modalTitle = document.getElementById("modalTitle");
        this.modalImage = document.getElementById("modalImage");
        this.modalRent = document.getElementById("modalRent");
        this.modalDescription = document.getElementById("modalDescription");
        this.modalContact = document.getElementById("modalContact");
        this.bookingForm = document.getElementById("bookingForm");
        
        // Ensure modal is hidden on page load
        this.closeModalFn();
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Close modal events
        this.closeModal.addEventListener("click", () => this.closeModalFn());
        if(this.closeModalSecondary) {
            this.closeModalSecondary.addEventListener('click', () => this.closeModalFn());
        }
        window.addEventListener("click", e => {
            if(e.target === this.modal) this.closeModalFn();
        });
        window.addEventListener('keydown', e => {
            if(e.key === 'Escape') this.closeModalFn();
        });

        // Form submission
        this.bookingForm.addEventListener("submit", (e) => this.handleBookingSubmit(e));
    }

    openModal(ad) {
        this.modal.style.display = "flex";
        this.modal.setAttribute('aria-hidden', 'false');
        this.modalTitle.textContent = ad.title;
        this.modalImage.src = ad.image_path;
        this.modalRent.textContent = "Rent: ৳" + ad.rent;
        this.modalDescription.textContent = ad.description;
        // Show available contact info
        if(this.modalContact) {
            const parts = [];
            if(ad.phone) parts.push(`Phone: ${ad.phone}`);
            if(ad.email) parts.push(`Email: ${ad.email}`);
            if(ad.whatsapp) parts.push(`WhatsApp: ${ad.whatsapp}`);
            this.modalContact.textContent = parts.join(' • ') || '';
        }
        this.currentAdId = ad.id;
    }

    closeModalFn() {
        this.modal.style.display = "none";
        this.modal.setAttribute('aria-hidden', 'true');
        this.currentAdId = null;
    }

    async handleBookingSubmit(e) {
        e.preventDefault();
        if(this.currentAdId === null) {
            alert("Please select an ad first!");
            return;
        }

        const formData = {
            ad_id: this.currentAdId,
            name: document.getElementById("name").value,
            email: document.getElementById("email").value,
            phone: document.getElementById("phone").value
        };

        try {
            const response = await fetch("/book_ad", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if(data.success) {
                alert(`Thank you, ${formData.name}! Your booking has been submitted. Wait for confirmation email.`);
                this.bookingForm.reset();
                this.closeModalFn();
            } else {
                alert("Booking failed: " + data.error);
            }
        } catch(err) {
            console.error("Fetch error:", err);
            alert("An error occurred while booking.");
        }
    }
}

// Initialize booking functionality
const bookingManager = new BookingManager();