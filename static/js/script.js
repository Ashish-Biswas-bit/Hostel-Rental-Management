const container = document.getElementById("adsContainer");
const modal = document.getElementById("modal");
const closeModal = document.getElementById("closeModal");
const closeModalSecondary = document.getElementById("closeModalSecondary");
const modalTitle = document.getElementById("modalTitle");
const modalImage = document.getElementById("modalImage");
const modalRent = document.getElementById("modalRent");
const modalDescription = document.getElementById("modalDescription");
const bookingForm = document.getElementById("bookingForm");

// Global variable to track selected ad
let currentAdId = null;

// Render ads into styled cards
adsData.forEach(ad => {
    const card = document.createElement("article");
    card.className = "adCard";
    card.tabIndex = 0;
    // include title and location in searchable dataset, normalize type to lowercase
    card.dataset.title = ((ad.title || '') + ' ' + (ad.location || '')).trim();
    card.dataset.type = (ad.type || '').toLowerCase();
    card.dataset.location = (ad.location || '');
    card.dataset.category = (ad.category || '').toLowerCase();

    card.innerHTML = `
        <img class="adImage" src="${ad.image_path}" alt="${ad.title}">
        <div class="adBody">
            <div class="cardRow">
                <h3 class="adTitle">${ad.title}</h3>
                <div class="priceBadge">৳${ad.rent}</div>
            </div>
            <div class="adMeta">${ad.location || ''}</div>
            <p class="adDescription">${(ad.description || '').slice(0,120)}${(ad.description||'').length>120? '...':''}</p>
        </div>
    `;

    // If image fails to load, fall back to a known upload or a generic image
    const imgEl = card.querySelector('.adImage');
    if(imgEl){
        imgEl.onerror = function(){
            this.onerror = null;
            this.src = '/static/uploads/edit.jpg';
        }
    }

    // open modal on click or Enter
    function openModal() {
        modal.style.display = "flex";
        modal.setAttribute('aria-hidden','false');
        modalTitle.textContent = ad.title;
        modalImage.src = ad.image_path;
        modalRent.textContent = "Rent: ৳" + ad.rent;
        modalDescription.textContent = ad.description;

        currentAdId = ad.id; // Track which ad is clicked
    }

    card.addEventListener("click", openModal);
    card.addEventListener("keydown", (e) => { if(e.key === 'Enter') openModal(); });

    container.appendChild(card);
});

// Close modal
function closeModalFn(){
    modal.style.display = "none";
    modal.setAttribute('aria-hidden','true');
    currentAdId = null;
}

closeModal.addEventListener("click", closeModalFn);
if(closeModalSecondary) closeModalSecondary.addEventListener('click', closeModalFn);
window.addEventListener("click", e => { if(e.target === modal) closeModalFn(); });
window.addEventListener('keydown', e => { if(e.key === 'Escape') closeModalFn(); });

// Booking form submit
bookingForm.addEventListener("submit", e => {
    e.preventDefault();
    console.log("Submitting booking...");

    if(currentAdId === null) {
        alert("Please select an ad first!");
        return;
    }

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;
    console.log({ ad_id: currentAdId, name, email, phone });

    fetch("/book_ad", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ad_id: currentAdId, name, email, phone })
    })
    .then(res => {
        console.log("Server responded with status:", res.status);
        return res.json();
    })
    .then(data => {
        console.log("Response JSON:", data);
        if(data.success) {
            alert(`Thank you, ${name}! Your booking has been submitted.`);
            bookingForm.reset();
            modal.style.display = "none";
            currentAdId = null;
        } else {
            alert("Booking failed: " + data.error);
        }
    })
    .catch(err => {
        console.error("Fetch error:", err);
        alert("An error occurred while booking.");
    });
});
