// Event listener for the form submission
const form = document.getElementById('conversion-form');

form.addEventListener('submit', function(event) {
    event.preventDefault();

    // Collect values from the form
    const fromSystem = document.getElementById('from-system').value;
    const toSystem = document.getElementById('to-system').value;
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);

    // Prepare the data for the POST request
    const bodyData = JSON.stringify({ fromSystem, toSystem, latitude, longitude });

    // Send the data to the Flask backend
    fetch('/converter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: bodyData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error during conversion');
        }        
        return response.json();
    })
    .then(data => {
        console.log(data);
        // Call the backend to get the maps with the new coordinates
        if (data.from_coords && data.to_coords) {

            try {
                const longResult = document.getElementById('result-longitude');
                longResult.innerHTML = data.to_coords.longitude;

                const latResult = document.getElementById('result-latitude');
                latResult.innerHTML = data.to_coords.latitude;
            } catch (e) {
                console.error(e);
            }

            fillMap('from-map', data.from_coords.longitude, data.from_coords.latitude, data.from_coords.projection)
            fillMap('to-map', data.to_coords.longitude, data.to_coords.latitude, data.to_coords.projection)
        } else {
            alert('Invalid conversion results.');
        }
    })
    .catch(error => {
        console.error('Conversion error:', error);
        alert('An error occurred while converting coordinates.');
    });
});

function fillMap(mapId, longitude, latitude, projection) {
    fetch(`/map?longitude=${longitude}&latitude=${latitude}&projection=${projection}`)
    .then((response) => response.text())
    .then((html) => {
        const mapIframe = document.getElementById(mapId);
        mapIframe.srcdoc = html; // Set the HTML content directly in the iframe
    })
    .catch((error) => console.error("Error loading map:", error));
}
