server = 'http://172.17.01:5000'

playerId = null;

document.addEventListener('DOMContentLoaded', () => {
    joinGame();
    getGameInfo();
});

async function joinGame() {
    try {
        const response = await fetch(`${server}/join-game`);
        const data = await response.json();
        console.log("My player id is: " + data.data);
    } catch (error) {
        console.error("Failed to join game.");
    }
}

async function getGameInfo() {

}