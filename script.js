document.getElementById('recommendation-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    let brand = document.getElementById('brand').value;
    let ram = document.getElementById('ram').value;
    let storage = document.getElementById('storage').value;
    
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ brand: brand, ram: ram, storage: storage })
    })
    .then(response => response.json())
    .then(data => {
        let recommendationsDiv = document.getElementById('recommendations');
        recommendationsDiv.innerHTML = '';
        if (data.recommendations) {
            data.recommendations.forEach(rec => {
                let recDiv = document.createElement('div');
                recDiv.innerHTML = `
                    <h3>${rec.name}</h3>
                    <p>Rating: ${rec.ratings}</p>
                    <p>Price: ${rec.price}</p>
                    <img src="${rec.imgURL}" alt="${rec.name}" />
                    <p>${rec.corpus}</p>
                `;
                recommendationsDiv.appendChild(recDiv);
            });
        } else {
            recommendationsDiv.innerHTML = `<p>${data.error}</p>`;
        }
    })
    .catch(error => console.error('Error:', error));
});
