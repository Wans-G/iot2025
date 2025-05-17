server = 'http://127.0.0.1:8000';
const playerId = localStorage.getItem('playerId');

async function save() {
    const response = await fetch(`${server}/save`);
}

async function load() {
    const response = await fetch(`${server}/load`);
}

async function start() {
    const response = await fetch(`${server}/start-game`);
}

document.addEventListener('DOMContentLoaded', () => {
    // Display Player ID
    const playerInfoElement = document.getElementById('player-identity');
    if (playerId !== null) {
        if (playerInfoElement) {
            playerInfoElement.textContent = `You are Player ${playerId}`;
        } else {
            console.warn("Element with ID 'player-identity' not found.");
        }
    } else {
        if (playerInfoElement) {
            playerInfoElement.textContent = "Error: Player ID not found. Please join again.";
        }
        console.error("Player ID not found in localStorage.");
        // Optionally redirect back to index.html or show an error message
        // window.location.href = "index.html"; 
        return; // Stop further initialization if ID is missing
    }

    // Add listener for end-turn button (if it wasn't added already)
    const endTurnButton = document.getElementById('end-turn');
    if (endTurnButton) {
        endTurnButton.addEventListener('click', endTurn);
    } else {
        // It seems the 'end-turn' button is missing from game.html based on the provided file.
        // We should add it to game.html or remove this listener logic.
        console.warn("Element with ID 'end-turn' not found."); 
    }

    getGameInfo();

    // Add listener for refresh button
    const refreshButton = document.getElementById('refresh-game');
    if (refreshButton) {
        refreshButton.addEventListener('click', getGameInfo);
    } else {
        console.warn("Element with ID 'refresh-game' not found.");
    }
});

document.getElementById('buy-dev-card').addEventListener('click', devCard);
document.getElementById('build-road').addEventListener('click', buildRoad);
document.getElementById('build-settlement').addEventListener('click', buildSettlement);
document.getElementById('build-city').addEventListener('click', buildCity);
document.getElementById('end-turn').addEventListener('click', endTurn);

document.querySelectorAll(".dev-card").forEach(btn => {
    btn.addEventListener("click", async () => {
        const card = parseInt(btn.dataset.card);

        let args = [];

        if (card === 3) {
            // Year of Plenty
            const r1 = prompt("Choose first resource (brick, lumber, ore, grain, wool):");
            const r2 = prompt("Choose second resource:");
            args = [resourceNameToIndex(r1), resourceNameToIndex(r2)];
        } else if (card === 4) {
            // Monopoly
            const res = prompt("Choose resource to monopolize:");
            args = [resourceNameToIndex(res)];
        }

        await useDevCard(card, args);
    });
});

function resourceNameToIndex(name) {
    const map = {
        "wood": 0,
        "lumber": 0,
        "sheep": 1,
        "wool": 1,
        "wheat": 2,
        "grain": 2,
        "brick": 3,
        "ore": 4
    };
    return map[name.toLowerCase()];
}

async function getGameInfo() {
    try {
        const response = await fetch(`${server}/game-info`);
        const data = await response.json();
        console.log("Received game data:", JSON.stringify(data, null, 2));

        // Update dice roll
        document.getElementById("dice-result").textContent = data.roll ?? '--'; // Use nullish coalescing

        // Update player list
        const playerList = document.getElementById("player-list");
        playerList.innerHTML = "";

        data.players.forEach(player => {
            const li = document.createElement("li");
            li.textContent = `Player ${player.color} - Victory Points: ${player.victoryPoints}`;
            playerList.appendChild(li);

            // If this is *you*, update your resource UI
            if (player.id == playerId) {
                updateResourcesDisplay(player.hand);
                if (player.cards) {
                    updateDevCards(player.cards);
                } else {
                    console.warn("No dev cards found for player", player.id);
                }
            }
        });

    } catch (error) {
        console.error("Failed to get game info:", error);
    }
}

async function useDevCard(card, args = []) {
    try {
        let url = `${server}/use-dev-card/${card}/${playerId}`;

        if (args.length > 0) {
            url += `?args=${args.join(",")}`;
        }

        const response = await fetch(url);
        const result = await response.json();
        console.log("Dev card used:", result);

        await getGameInfo(); // refresh counts/resources

    } catch (err) {
        console.error("Failed to use dev card:", err);
    }
}

function updateResourcesDisplay(resourceData) {
    document.querySelectorAll(".resource").forEach(div => {
        const resource = div.dataset.resource.toLowerCase();
        // Get the value from resourceData, default to 0 if null or undefined
        const value = resourceData?.[resource] ?? 0;
        div.querySelector("span").textContent = value;
    });
}

function updateDevCards(devCardData) {
    document.querySelectorAll(".dev-card").forEach(btn => {
        const card = btn.dataset.card;
        const count = devCardData[card] || 0;
        btn.querySelector("span").textContent = count;

        if (card === "1") {
            btn.disabled = true; // Point card is never clickable
        } else {
            btn.disabled = count === 0;
        }
    });
}

async function buildRoad(){
    try{
        const response = await fetch(`${server}/build-road/${playerId}`);
        const data = await response.json();
        
        
        getGameInfo();

    
    }catch(error){
        console.error("Failed to build road");
    }
}


async function buildSettlement(){
    try{
        const response = await fetch(`${server}/build-house/${playerId}`);
        const data = await response.json();
        
        
        getGameInfo();

    
    }catch(error){
        console.error("Failed to build road");
    }
}

async function buildCity(){
    try{
        const response = await fetch(`${server}/build-city/${playerId}`);
        const data = await response.json();
        
        getGameInfo();

    
    }catch(error){
        console.error("Failed to build road");
    }
}

async function devCard(){
    try{
        const response = await fetch(`${server}/buy-dev-card/${playerId}`);
        getGameInfo();
    }catch(error){
        console.error("failed to buy dev card");
    }
}

async function endTurn(){
    try{
        const response = await fetch(`${server}/end-turn/${playerId}`);
        
        await getGameInfo();


    }catch(error){
        console.error("Failed to end turn");
    }
}

async function updateResources(){
    try {
        const response = await fetch(`${server}/update-resources/${playerId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const resources = data.resources;
        console.log("Received resources:", resources);

        const adaptedResources = {
            lumber: resources["lumber"] == undefined ? 0 : resources["lumber"],
            wool: resources["wool"] == undefined ? 0 : resources["wool"],
            grain: resources["grain"] == undefined ? 0 : resources["grain"],
            brick: resources["brick"] == undefined ? 0 : resources["brick"],
            ore: resources["ore"] == undefined ? 0 : resources["ore"]
        };

        updateResourcesDisplay(adaptedResources);
    } catch (error) {
        console.error("Failed to update resources:", error);
    }
}
