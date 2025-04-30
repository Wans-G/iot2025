server = 'http://127.0.0.1:5000'

playerId = null;

document.addEventListener('DOMContentLoaded', () => {
    joinGame();
    getGameInfo();
});

async function joinGame() {
    try {
        const response = await fetch(`${server}/join-game`);
        const data = await response.json();
        console.log("My player id is: " + data.id);
        playerId = data.id
    } catch (error) {
        console.error("Failed to join game.");
    }
}

async function getGameInfo() {
    try{
        const response = await fetch(`${server}/game-info`);
        

    } catch (error){
        console.error("Failed to get game info");
    }

}