const LOCALITIES = ['BTM', 'Banashankari', 'Banaswadi', 'Bannerghatta Road', 'Basavanagudi', 'Basaveshwara Nagar', 'Bellandur', 'Bommanahalli', 'Brigade Road', 'Brookefield', 'CV Raman Nagar', 'Central Bangalore', 'Church Street', 'City Market', 'Commercial Street', 'Cunningham Road', 'Domlur', 'East Bangalore', 'Ejipura', 'Electronic City', 'Frazer Town', 'HBR Layout', 'HSR', 'Hebbal', 'Hennur', 'Hosur Road', 'ITPL Main Road, Whitefield', 'Indiranagar', 'Infantry Road', 'JP Nagar', 'Jakkur', 'Jalahalli', 'Jayanagar', 'Jeevan Bhima Nagar', 'KR Puram', 'Kaggadasapura', 'Kalyan Nagar', 'Kammanahalli', 'Kanakapura Road', 'Kengeri', 'Koramangala', 'Koramangala 1st Block', 'Koramangala 2nd Block', 'Koramangala 3rd Block', 'Koramangala 4th Block', 'Koramangala 5th Block', 'Koramangala 6th Block', 'Koramangala 7th Block', 'Koramangala 8th Block', 'Kumaraswamy Layout', 'Langford Town', 'Lavelle Road', 'MG Road', 'Magadi Road', 'Majestic', 'Malleshwaram', 'Marathahalli', 'Mysore Road', 'Nagarbhavi', 'Nagawara', 'New BEL Road', 'North Bangalore', 'Old Airport Road', 'Old Madras Road', 'Peenya', 'RT Nagar', 'Race Course Road', 'Rajajinagar', 'Rajarajeshwari Nagar', 'Rammurthy Nagar', 'Residency Road', 'Richmond Road', 'Sadashiv Nagar', 'Sahakara Nagar', 'Sanjay Nagar', 'Sankey Road', 'Sarjapur Road', 'Seshadripuram', 'Shanti Nagar', 'Shivajinagar', 'South Bangalore', 'St. Marks Road', 'Thippasandra', 'Ulsoor', 'Unknown', 'Uttarahalli', 'Varthur Main Road, Whitefield', 'Vasanth Nagar', 'Vijay Nagar', 'West Bangalore', 'Whitefield', 'Wilson Garden', 'Yelahanka', 'Yeshwantpur'];
const CUISINES = ['Afghan', 'Afghani', 'African', 'American', 'Andhra', 'Arabian', 'Asian', 'Assamese', 'Australian', 'Awadhi', 'BBQ', 'Bakery', 'Bar Food', 'Belgian', 'Bengali', 'Beverages', 'Bihari', 'Biryani', 'Bohri', 'British', 'Bubble Tea', 'Burger', 'Burmese', 'Cafe', 'Cantonese', 'Charcoal Chicken', 'Chettinad', 'Chinese', 'Coffee', 'Continental', 'Desserts', 'Drinks Only', 'European', 'Fast Food', 'Finger Food', 'French', 'German', 'Goan', 'Greek', 'Grill', 'Gujarati', 'Healthy Food', 'Hot dogs', 'Hyderabadi', 'Ice Cream', 'Indian', 'Indonesian', 'Iranian', 'Italian', 'Japanese', 'Jewish', 'Juices', 'Kashmiri', 'Kebab', 'Kerala', 'Konkan', 'Korean', 'Lebanese', 'Lucknowi', 'Maharashtrian', 'Malaysian', 'Malwani', 'Mangalorean', 'Mediterranean', 'Mexican', 'Middle Eastern', 'Mithai', 'Modern Indian', 'Momos', 'Mongolian', 'Mughlai', 'N Naga', 'Nepalese', 'North Eastern', 'North Indian', 'Oriya', 'Other', 'Paan', 'Pan Asian', 'Parsi', 'Pizza', 'Portuguese', 'Rajasthani', 'Raw Meats', 'Roast Chicken', 'Rolls', 'Russian', 'Salad', 'Sandwich', 'Seafood', 'Sindhi', 'Singaporean', 'South American', 'South Indian', 'Spanish', 'Sri Lankan', 'Steak', 'Street Food', 'Sushi', 'Tamil', 'Tea', 'Tex-Mex', 'Thai', 'Tibetan', 'Turkish', 'Vegan', 'Vietnamese', 'Wraps'];

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const localitySelect = document.getElementById('localitySelect');
    const priceSelect = document.getElementById('priceSelect');
    const cuisineSelect = document.getElementById('cuisineSelect');
    const selectedCuisinesContainer = document.getElementById('selectedCuisines');
    const ratingDisplay = document.getElementById('ratingDisplay');
    const minusRating = document.getElementById('minusRating');
    const plusRating = document.getElementById('plusRating');
    const recommendBtn = document.getElementById('recommendBtn');
    const loader = document.getElementById('loader');
    const resultBox = document.getElementById('resultBox');
    const resultContent = document.getElementById('resultContent');
    const cuisineChips = document.querySelectorAll('.chip');
    const resultsGrid = document.getElementById('resultsGrid');
    const similarityHeader = document.getElementById('similarityHeader');
    const similarityContext = document.getElementById('similarityContext');
    const backBtn = document.getElementById('backBtn');

    let currentRating = 4.0;
    let selectedCuisines = new Set();
    let originalResultsHTML = ''; // To store state for "Back" button

    // Populate Localities
    LOCALITIES.forEach(loc => {
        const opt = document.createElement('option');
        opt.value = loc;
        opt.textContent = loc;
        localitySelect.appendChild(opt);
    });

    // Populate Cuisines Dropdown
    CUISINES.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        cuisineSelect.appendChild(opt);
    });

    // Tag Management
    const addCuisineTag = (val) => {
        if (!val || selectedCuisines.has(val)) return;

        selectedCuisines.add(val);

        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.innerHTML = `${val} <i class="fa-solid fa-xmark"></i>`;
        tag.querySelector('i').onclick = () => removeCuisineTag(val, tag);

        selectedCuisinesContainer.appendChild(tag);

        // Update chip if exists
        const chip = Array.from(cuisineChips).find(c => c.getAttribute('data-val') === val);
        if (chip) chip.classList.add('active');
    };

    const removeCuisineTag = (val, tagElement) => {
        selectedCuisines.delete(val);
        tagElement.remove();

        // Update chip if exists
        const chip = Array.from(cuisineChips).find(c => c.getAttribute('data-val') === val);
        if (chip) chip.classList.remove('active');
    };

    // Cuisine Dropdown Event
    cuisineSelect.addEventListener('change', (e) => {
        addCuisineTag(e.target.value);
        e.target.value = ''; // Reset select
    });

    // Cuisine Chips Logic
    cuisineChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const val = chip.getAttribute('data-val');
            if (chip.classList.contains('active')) {
                const tagElement = Array.from(selectedCuisinesContainer.children).find(el => el.textContent.trim() === val);
                if (tagElement) removeCuisineTag(val, tagElement);
            } else {
                addCuisineTag(val);
            }
        });
    });

    // Rating Stepper Logic
    minusRating.addEventListener('click', () => {
        if (currentRating > 0) {
            currentRating = parseFloat((currentRating - 0.5).toFixed(1));
            ratingDisplay.textContent = currentRating.toFixed(1);
        }
    });

    plusRating.addEventListener('click', () => {
        if (currentRating < 5.0) {
            currentRating = parseFloat((currentRating + 0.5).toFixed(1));
            ratingDisplay.textContent = currentRating.toFixed(1);
        }
    });

    // Render Card
    const createFlashCard = (res, isSimilarView = false) => {
        const card = document.createElement('div');
        card.className = 'flash-card';
        card.innerHTML = `
            <div class="card-header">
                <div class="header-main">
                    <h4>${res.name}</h4>
                    <div class="match-score">${res.match_score}% ${isSimilarView ? 'Similarity' : 'Match'}</div>
                </div>
                <div class="ai-summary-line">${res.ai_summary}</div>
            </div>
            <div class="card-meta">
                <span><i class="fa-solid fa-star"></i> ${res.rating}</span>
                <span><i class="fa-solid fa-rupiah-sign"></i> ₹${res.cost} for two</span>
                <span><i class="fa-solid fa-location-dot"></i> ${res.location}</span>
            </div>
            <div class="card-meta">
                <span><i class="fa-solid fa-utensils"></i> ${res.cuisines}</span>
            </div>
            <div class="why-this-box">
                <b>${isSimilarView ? 'Similarity Reason' : 'Why This Recommendation'}</b>
                ${res.why_this}
            </div>
            <div class="card-actions">
                <button class="action-btn save-btn">
                    <i class="fa-regular fa-star"></i> Save
                </button>
                <button class="action-btn similar-btn">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Similar
                </button>
            </div>
        `;

        // Save Logic
        const saveBtn = card.querySelector('.save-btn');
        saveBtn.onclick = () => {
            saveBtn.classList.toggle('saved');
            saveBtn.innerHTML = saveBtn.classList.contains('saved') ?
                `<i class="fa-solid fa-star"></i> Saved` : `<i class="fa-regular fa-star"></i> Save`;
        };

        // Similar Logic
        card.querySelector('.similar-btn').onclick = () => showSimilar(res);

        return card;
    };

    const showSimilar = async (refRes) => {
        // Save current state if not already in similar view
        if (similarityHeader.style.display === 'none') {
            originalResultsHTML = resultsGrid.innerHTML;
        }

        resultsGrid.innerHTML = '';
        similarityHeader.style.display = 'block';
        similarityContext.innerText = `Similar to ${refRes.name} — based on cuisine, price, and rating.`;
        loader.style.display = 'flex';
        resultBox.scrollIntoView({ behavior: 'smooth' });

        try {
            const response = await fetch('/similar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(refRes)
            });

            const data = await response.json();
            const payload = JSON.parse(data.recommendation);

            if (payload.recommendations && payload.recommendations.length > 0) {
                payload.recommendations.forEach(res => {
                    resultsGrid.appendChild(createFlashCard(res, true));
                });
            } else {
                resultsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-gray)">No similar restaurants found nearby.</p>';
            }
        } catch (e) {
            resultsGrid.innerHTML = `<p style="grid-column: 1/-1; color: #ff4d4d; text-align: center;">Error: ${e.message}</p>`;
        } finally {
            loader.style.display = 'none';
        }
    };

    backBtn.onclick = () => {
        resultsGrid.innerHTML = originalResultsHTML;
        similarityHeader.style.display = 'none';
        resultBox.scrollIntoView({ behavior: 'smooth' });
    };

    // Recommendations Logic
    const getRecommendations = async () => {
        const locality = localitySelect.value;
        const price = priceSelect.value;
        const rating = currentRating;
        const cuisines = Array.from(selectedCuisines).join(', ');

        if (!locality) {
            alert("Please select a locality!");
            localitySelect.focus();
            return;
        }

        similarityHeader.style.display = 'none';
        resultsGrid.innerHTML = '';
        resultBox.classList.remove('active');
        loader.style.display = 'flex';
        recommendBtn.disabled = true;

        let queryParts = [];
        if (cuisines) queryParts.push(`${cuisines} food`);
        queryParts.push(`in ${locality}`);
        queryParts.push(`with a minimum rating of ${rating}`);

        if (price === 'cheap') queryParts.push("under 500 rupees");
        else if (price === 'moderate') queryParts.push("between 500 and 1500 rupees");
        else if (price === 'expensive') queryParts.push("above 1500 rupees");

        const synthesizedQuery = "I want " + queryParts.join(" ");

        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: synthesizedQuery })
            });

            if (!response.ok) throw new Error("Server communication failed.");

            const data = await response.json();
            const payload = JSON.parse(data.recommendation);

            if (payload.recommendations && payload.recommendations.length > 0) {
                payload.recommendations.forEach(res => {
                    resultsGrid.appendChild(createFlashCard(res));
                });
                resultBox.classList.add('active');
                resultBox.scrollIntoView({ behavior: 'smooth' });
            } else {
                resultsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-gray)">No perfect matches found. Try relaxing your filters!</p>';
                resultBox.classList.add('active');
            }

        } catch (error) {
            resultsGrid.innerHTML = `<p style="grid-column: 1/-1; color: #ff4d4d; text-align: center;">Error: ${error.message}</p>`;
            resultBox.classList.add('active');
        } finally {
            loader.style.display = 'none';
            recommendBtn.disabled = false;
        }
    };

    recommendBtn.addEventListener('click', getRecommendations);
});
