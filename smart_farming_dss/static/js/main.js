// KrishiMitra Main Javascript Interface

document.addEventListener('DOMContentLoaded', function () {
    // 1. Tooltips & Popovers initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. Alert auto-dismiss after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 3. Animate circular gauges (confidence gauge + hero soil-reading rings)
    document.querySelectorAll('[data-percent]').forEach(function (gauge) {
        const circle = gauge.querySelector('circle.arc');
        if (!circle) return;
        const pct = Math.max(0, Math.min(100, parseFloat(gauge.getAttribute('data-percent')) || 0));
        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        circle.style.strokeDasharray = circumference;
        circle.style.strokeDashoffset = circumference;
        requestAnimationFrame(function () {
            setTimeout(function () {
                circle.style.strokeDashoffset = circumference - (pct / 100) * circumference;
            }, 150);
        });
    });

    // 4. Animate horizontal bar fills (top-crop ranking, feature importance)
    document.querySelectorAll('[data-width]').forEach(function (bar) {
        const target = bar.getAttribute('data-width');
        requestAnimationFrame(function () {
            setTimeout(function () { bar.style.width = target + '%'; }, 150);
        });
    });

    // 5. Scroll-triggered reveal animation
    const revealEls = document.querySelectorAll('.reveal');
    if (revealEls.length && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
        revealEls.forEach(function (el) { observer.observe(el); });
    } else {
        revealEls.forEach(function (el) { el.classList.add('is-visible'); });
    }
});

/**
 * Renders an NPK Chart comparing soil levels to predicted crop target averages.
 */
function renderNPKChart(canvasId, userN, userP, userK, targetN, targetP, targetK, userLabel = "Your Soil", targetLabel = "Target Soil") {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'],
            datasets: [
                {
                    label: userLabel,
                    data: [userN, userP, userK],
                    backgroundColor: 'rgba(64, 145, 108, 0.75)',
                    borderColor: '#40916c',
                    borderWidth: 2,
                    borderRadius: 6
                },
                {
                    label: targetLabel,
                    data: [targetN, targetP, targetK],
                    backgroundColor: 'rgba(27, 67, 50, 0.25)',
                    borderColor: '#1b4332',
                    borderWidth: 2,
                    borderRadius: 6,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            family: 'Outfit',
                            size: 13,
                            weight: 'bold'
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Nutrient Value (ppm)',
                        font: {
                            family: 'Outfit',
                            weight: 'bold'
                        }
                    }
                },
                x: {
                    title: {
                        font: {
                            family: 'Outfit',
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

/**
 * Attempts to automatically fill location coordinates or names using Browser Geolocation.
 */
function autofillLocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            // Query reverse geocoding to retrieve district
            fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`)
                .then(response => response.json())
                .then(data => {
                    const districtInput = document.getElementById('district');
                    const stateInput = document.getElementById('state');
                    
                    if (districtInput && data.city) {
                        districtInput.value = data.city.replace(" District", "");
                    }
                    if (stateInput && data.principalSubdivision) {
                        stateInput.value = data.principalSubdivision;
                    }
                })
                .catch(err => console.log("Reverse Geocoding failed:", err));
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}
