document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("fileInput");
  const executeButton = document.getElementById("executeButton");
  const fileName = document.getElementById("fileName");
  const loadingSection = document.querySelector(".loading-section");
  const resultsSection = document.querySelector(".results-section");
  const resultsTableBody = document.getElementById("resultsTableBody");
  const fileInputWrapper = document.querySelector(".file-input-wrapper");
  const progressFill = document.querySelector(".progress-fill");

  // Animacija za hero sekciju
  const heroTitle = document.querySelector(".hero-title");
  if (heroTitle) {
    heroTitle.style.opacity = "0";
    heroTitle.style.transform = "translateY(20px)";
    setTimeout(() => {
      heroTitle.style.transition =
        "opacity 0.8s ease-out, transform 0.8s ease-out";
      heroTitle.style.opacity = "1";
      heroTitle.style.transform = "translateY(0)";
    }, 100);
  }

  // Drag and drop funkcionalnost
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    fileInputWrapper.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    fileInputWrapper.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    fileInputWrapper.addEventListener(eventName, unhighlight, false);
  });

  function highlight(e) {
    fileInputWrapper.classList.add("highlight");
  }

  function unhighlight(e) {
    fileInputWrapper.classList.remove("highlight");
  }

  fileInputWrapper.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const file = dt.files[0];
    handleFile(file);
  }

  function handleFile(file) {
    if (file) {
      if (file.name.endsWith(".mp3") || file.name.endsWith(".mp4")) {
        executeButton.disabled = false;
        fileName.textContent = `Izabran fajl: ${file.name}`;
        fileInput.files = new DataTransfer().files;
      } else {
        alert("Molimo izaberite MP3 ili MP4 fajl.");
        executeButton.disabled = true;
        fileName.textContent = "";
      }
    }
  }

  fileInput.addEventListener("change", function (e) {
    const file = e.target.files[0];
    handleFile(file);
  });

  executeButton.addEventListener("click", async function () {
    const file = fileInput.files[0];
    if (!file) return;

    document.querySelector(".upload-section").style.display = "none";
    loadingSection.style.display = "block";
    resultsSection.style.display = "none";

    // Simulacija progresa
    let progress = 0;
    const progressInterval = setInterval(() => {
      progress += 1;
      progressFill.style.width = `${progress}%`;
      if (progress >= 100) {
        clearInterval(progressInterval);

        // Primer podataka
        const results = [
          { pitanje: "Prvo pitanje?", odgovor: "Prvi odgovor" },
          { pitanje: "Drugo pitanje?", odgovor: "Drugi odgovor" },
        ];

        resultsTableBody.innerHTML = "";
        results.forEach((result) => {
          const row = document.createElement("tr");
          row.innerHTML = `
                        <td>${result.pitanje}</td>
                        <td>${result.odgovor}</td>
                    `;
          resultsTableBody.appendChild(row);
        });

        setTimeout(() => {
          loadingSection.style.display = "none";
          resultsSection.style.display = "block";
        }, 500);
      }
    }, 30);
  });

  // Remove the old carousel functionality since we're using Swiper
  // Carousel functionality
  /*
  const container = document.querySelector(".blog-cards-container");
  if (container) {
    const cards = document.querySelector(".blog-cards");
    const cardWidth = 300; // Width of each card
    const gap = 32; // Gap between cards (2rem = 32px)
    const visibleCards = 3; // Number of visible cards
    const totalCards = document.querySelectorAll(".blog-card").length; // Get actual number of cards
    let currentIndex = 0;

    // Create navigation buttons
    const prevButton = document.createElement("button");
    prevButton.className = "carousel-button prev";
    prevButton.innerHTML =
      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>';

    const nextButton = document.createElement("button");
    nextButton.className = "carousel-button next";
    nextButton.innerHTML =
      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>';

    // Update carousel position
    function updateCarousel() {
      const cards = document.querySelectorAll(".blog-card");
      const offset =
        -currentIndex *
        (cards[0].offsetWidth +
          parseFloat(getComputedStyle(cards[0]).marginRight));

      // Prvo dodamo klasu hiding karticama koje će biti sakrivene
      cards.forEach((card, index) => {
        if (card.classList.contains("visible")) {
          if (index < currentIndex) {
            card.classList.add("hiding-right");
          } else if (index >= currentIndex + 3) {
            card.classList.add("hiding");
          }
          card.classList.remove("visible");
        }
      });

      // Sačekamo da se završi animacija sakrivanja
      setTimeout(() => {
        // Uklonimo hiding klase i dodamo visible za nove kartice
        cards.forEach((card, index) => {
          card.classList.remove("hiding");
          card.classList.remove("hiding-right");
          if (index >= currentIndex && index < currentIndex + 3) {
            card.classList.add("visible");
          }
        });

        document.querySelector(
          ".blog-cards"
        ).style.transform = `translateX(${offset}px)`;
      }, 300);

      // Ažuriramo stanje dugmadi
      prevButton.classList.toggle("disabled", currentIndex === 0);
      nextButton.classList.toggle("disabled", currentIndex >= totalCards - 3);
    }

    // Add click handlers
    prevButton.addEventListener("click", () => {
      if (!prevButton.classList.contains("disabled")) {
        currentIndex = Math.max(0, currentIndex - 1);
        updateCarousel();
      }
    });

    nextButton.addEventListener("click", () => {
      if (!nextButton.classList.contains("disabled")) {
        currentIndex = Math.min(totalCards - visibleCards, currentIndex + 1);
        updateCarousel();
      }
    });

    // Add buttons to container
    container.appendChild(prevButton);
    container.appendChild(nextButton);

    // Initial setup
    updateCarousel();
  }
  */

  // Initialize Swiper with proper settings
  var swiper = new Swiper(".multiple-slide-carousel", {
    loop: false,
    slidesPerView: 1,
    spaceBetween: 20,
    centeredSlides: true,
    effect: "slide",
    speed: 600,
    autoHeight: true,
    grabCursor: true,
    navigation: {
      nextEl: "#slider-button-right",
      prevEl: "#slider-button-left",
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
    breakpoints: {
      // When window width is >= 576px
      576: {
        slidesPerView: 1,
        spaceBetween: 20,
        centeredSlides: true,
      },
      // When window width is >= 768px
      768: {
        slidesPerView: 2,
        spaceBetween: 20,
        centeredSlides: false,
      },
      // When window width is >= 1024px
      1024: {
        slidesPerView: 3,
        spaceBetween: 30,
        centeredSlides: false,
      },
    },
    on: {
      init: function () {
        // Make sure all slides are visible on init
        document.querySelectorAll(".swiper-slide").forEach((slide) => {
          slide.style.visibility = "visible";
          slide.style.opacity = "1";
        });
      },
      resize: function () {
        // Update swiper on window resize
        this.update();
      },
    },
  });

  // Funkcija za postavljanje aktivne stavke u mobilnom meniju
  function setActiveMobileNavItem() {
    // Dobijanje trenutne putanje
    const currentPath = window.location.pathname;

    // Uklanjanje klase 'active' sa svih stavki mobilnog menija
    const mobileNavItems = document.querySelectorAll(".mobile-nav-item");
    mobileNavItems.forEach((item) => {
      item.classList.remove("active");
    });

    // Postavljanje klase 'active' na odgovarajuću stavku na osnovu trenutne stranice
    if (
      currentPath.includes("fact_check") ||
      currentPath.endsWith("fact_check.html")
    ) {
      document
        .querySelector('.mobile-nav-item[href*="fact_check"]')
        ?.classList.add("active");
    } else if (
      currentPath.includes("consistency") ||
      currentPath.endsWith("consistency.html")
    ) {
      document
        .querySelector('.mobile-nav-item[href*="consistency"]')
        ?.classList.add("active");
    } else if (
      currentPath.includes("about") ||
      currentPath.endsWith("about.html")
    ) {
      document
        .querySelector('.mobile-nav-item[href*="about"]')
        ?.classList.add("active");
    } else {
      // Podrazumevano za index stranicu
      document
        .querySelector(
          '.mobile-nav-item[href="./index.html"], .mobile-nav-item[href="./"], .mobile-nav-item[href="/"]'
        )
        ?.classList.add("active");
    }
  }

  // Postavljanje aktivne stavke u mobilnom meniju
  setActiveMobileNavItem();

  // Pozivanje funkcije kada se promeni stanje istorije (za SPA navigaciju ako postoji)
  window.addEventListener("popstate", setActiveMobileNavItem);

  // Funkcija za proveru činjenica na osnovu CSV fajla
  function factCheck(fileName) {
    console.log(`Provera činjenica za fajl: ${fileName}`);

    // Ovde možete dodati logiku za preusmeravanje na fact_check stranicu
    // sa parametrom za učitavanje određenog fajla

    // Primer preusmeravanja na fact_check stranicu sa parametrom
    window.location.href = `fact_check.html?file=${encodeURIComponent(
      fileName
    )}`;
  }
});

// Globalna funkcija factCheck koja se može pozivati iz HTML-a
window.factCheck = function (fileName) {
  console.log(`Provera činjenica za fajl: ${fileName}`);

  // Preusmeravanje na fact_check stranicu sa parametrom
  window.location.href = `fact_check.html?file=${encodeURIComponent(fileName)}`;
};
