server = 'http://127.0.0.1:5000';
playerId = null;

document.getElementById("start-btn").addEventListener("click", async () => {
    console.log("Start game clicked");
    await joinGame();
    window.location.href = "game.html";
});

async function joinGame() {
    console.log("Attempting to join game...");
    try {
        const response = await fetch(`${server}/join-game`);        
        const data = await response.json();        
        playerId = data.id;
        localStorage.setItem('playerId', playerId);
    } catch (error) {
        console.error("Failed to join game:", error);
    }
}