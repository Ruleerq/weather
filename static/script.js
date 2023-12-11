// Function to get the user's current location
function getUserLocation() {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        position => {
          resolve({
            lat: 52.232361,//position.coords.latitude,
            lng: 21.002769//position.coords.longitude
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
const knownCoordinates = { lat: 53.428543, lng: 	14.552812 }; // Latitude and Longitude
const knownPixelPosition = { x: 190, y: 405 }; // Pixel position

// Rzeszow positions
const newKnownCoordinates = { lat: 50.041187, lng: 21.999121 }; // Latitude and Longitude
const newPixelPosition = { x: 1088, y: 1050 }; // Pixel position

// Calculate the pixel and coordinate differences between two known points
const knownPixelDifference = {
    x: newPixelPosition.x - knownPixelPosition.x,
    y: newPixelPosition.y - knownPixelPosition.y
};

const knownCoordDifference = {
    lat: newKnownCoordinates.lat - knownCoordinates.lat,
    lng: newKnownCoordinates.lng - knownCoordinates.lng
};

// Calculate the map scale in pixels per degree
const mapScale = {
    x: knownPixelDifference.x / knownCoordDifference.lng,
    y: knownPixelDifference.y / knownCoordDifference.lat
};

// Function to calculate the pixel position from geographical coordinates
function calculatePixelPosition(userCoordinates) {
  const pixelDifference = {
    x: (userCoordinates.lng - knownCoordinates.lng) * mapScale.x,
    y: (userCoordinates.lat - knownCoordinates.lat) * mapScale.y
  };

  return {
    x: knownPixelPosition.x + pixelDifference.x,
    y: knownPixelPosition.y + pixelDifference.y * 1.10
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
