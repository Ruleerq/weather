// Function to get the user's current location
function getUserLocation() {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        position => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude
            //Warsaw coordinates
            // lat: 52.232361,
            // lng: 21.002769
          });
        },
        err => {
          reject(err);
        }
      );
    } else {
      reject(new Error("Geolocation is not supported by this browser."));
    }
  });
}

// Szczecin positions
const SzczecinCoordinates = { lat: 53.428543, lng: 14.552812 }; // Latitude and Longitude
const szczecinPixels = { x: 190, y: 405 }; // Pixel position

// Rzeszow positions
const RzeszowCoordinates = { lat: 50.041187, lng: 21.999121 }; // Latitude and Longitude
const RzeszowPixels = { x: 1088, y: 1050 }; // Pixel position

// Calculate the pixel and coordinate differences between two known points
const knownPixelDifference = {
    x: RzeszowPixels.x - szczecinPixels.x,
    y: RzeszowPixels.y - szczecinPixels.y
};

const knownCoordDifference = {
    lat: RzeszowCoordinates.lat - SzczecinCoordinates.lat,
    lng: RzeszowCoordinates.lng - SzczecinCoordinates.lng
};

// Calculate the map scale in pixels per degree
const mapScale = {
    x: knownPixelDifference.x / knownCoordDifference.lng,
    y: knownPixelDifference.y / knownCoordDifference.lat
};

// Calculate the pixel position from geographical coordinates
function calculatePixelPosition(userCoordinates) {
  const pixelDifference = {
    x: (userCoordinates.lng - SzczecinCoordinates.lng) * mapScale.x,
    y: (userCoordinates.lat - SzczecinCoordinates.lat) * mapScale.y
  };

  return {
    x: szczecinPixels.x + pixelDifference.x,
    y: szczecinPixels.y + pixelDifference.y * 1.10
  };
}

// Get user location and calculate the pixel position
getUserLocation().then(userCoordinates => {
  const userPixelPosition = calculatePixelPosition(userCoordinates);
  console.log('User Coordinates:', userCoordinates);
  console.log('User Pixel Position:', userPixelPosition);

  // Update the position of the map pin
  const mapPin = document.getElementById('mapPin');
  mapPin.style.left = `${userPixelPosition.x}px`;
  mapPin.style.top = `${userPixelPosition.y}px`;

}).catch(error => {
  console.error('Error getting user location:', error);
});
