server = 'http://127.0.0.1:5000';
const playerId = localStorage.getItem('playerId');

document.addEventListener('DOMContentLoaded', () => {
    getGameInfo();
});

document.getElementById('buy-dev-card').addEventListener('click', devCard);
document.getElementById('build-road').addEventListener('click', buildRoad);
document.getElementById('build-settlement').addEventListener('click', buildSettlement);
document.getElementById('build-city').addEventListener('click', buildCity);

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

        // Update dice roll
        document.getElementById("dice-result").textContent = data.roll;

        // Update player list
        const playerList = document.getElementById("player-list");
        playerList.innerHTML = "";

        data.players.forEach(player => {
            const li = document.createElement("li");
            li.textContent = `Player ${player.id} - Victory Points: ${player.victoryPoints}`;
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
        if (resource in resourceData) {
            div.querySelector("span").textContent = resourceData[resource];
        }
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
        
        
        await updateResources();

    
    }catch(error){
        console.error("Failed to build road");
    }
}


async function buildSettlement(){
    try{
        const response = await fetch(`${server}/build-house/${playerId}`);
        const data = await response.json();
        
        
        await updateResources();

    
    }catch(error){
        console.error("Failed to build road");
    }
}

async function buildCity(){
    try{
        const response = await fetch(`${server}/build-city/${playerId}`);
        const data = await response.json();
        await updateResources();

    
    }catch(error){
        console.error("Failed to build road");
    }
}

async function devCard(){
    try{
        const response = await fetch(`${server}/buy-dev-card/${playerId}`);
    }catch(error){
        console.error("failed to buy dev card");
    }
}

async function endTurn(){
    try{
        const response = await fetch(`${server}/end-turn/${playerId}`);
        
        await updateResources();


    }catch(error){
        console.error("Failed to end turn");
    }
}

async function updateResources(){
    console.log("updated resources");
}

