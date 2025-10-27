const container = document.getElementById("adsContainer");
const modal = document.getElementById("modal");
const closeModal = document.getElementById("closeModal");
const modalTitle = document.getElementById("modalTitle");
const modalImage = document.getElementById("modalImage");
const modalRent = document.getElementById("modalRent");
const modalDescription = document.getElementById("modalDescription");
const bookingForm = document.getElementById("bookingForm");

// Global variable to track selected ad
let currentAdId = null;

// Render ads
adsData.forEach(ad => {
    const card = document.createElement("div");
    card.className = "adCard";
    card.innerHTML = `
        <img src="${ad.image_path}" alt="${ad.title}">
        <h3>${ad.title}</h3>
        <p>Rent: ৳${ad.rent}</p>
    `;

    card.addEventListener("click", () => {
        modal.style.display = "flex";
        modalTitle.textContent = ad.title;
        modalImage.src = ad.image_path;
        modalRent.textContent = "Rent: ৳" + ad.rent;
        modalDescription.textContent = ad.description;

        currentAdId = ad.id; // Track which ad is clicked
    });

    container.appendChild(card);
});

// Close modal
closeModal.addEventListener("click", () => modal.style.display = "none");
window.addEventListener("click", e => { if(e.target === modal) modal.style.display = "none"; });

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
