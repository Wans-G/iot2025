server = 'http://127.0.0.1:5000';

playerId = null;

document.addEventListener('DOMContentLoaded', () => {
    joinGame();
    //getGameInfo();
});

document.getElementById('buy-dev-card').addEventListener('click', devCard);
document.getElementById('build-road').addEventListener('click', buildRoad);
document.getElementById('build-settlement').addEventListener('click', buildSettlement);
document.getElementById('build-city').addEventListener('click', buildCity);


async function joinGame() {
    try {
        const response = await fetch(`${server}/join-game`);
        const data = await response.json();
        console.log("My player id is: " + data.id);
        playerId = data.id;
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

