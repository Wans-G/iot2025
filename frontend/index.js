server = 'http://127.0.0.1:8000';
playerId = null;



//const socket = io(`${server}`);



document.addEventListener('DOMContentLoaded', () => {
    joinGame();
    //getGameInfo();
    document.getElementById('buy-dev-card').addEventListener('click', devCard);
    document.getElementById('build-road').addEventListener('click', buildRoad);
    document.getElementById('build-settlement').addEventListener('click', buildSettlement);
    document.getElementById('build-city').addEventListener('click', buildCity);
    

});
    document.getElementById('end-turn').addEventListener('click', endTurn);
    document.getElementById('update').addEventListener('click', update);

/*
socket.on('resource-update', async function(data){
    if(data.id === playerId){
        await updateResources();
    }
})*/

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
        console.log("Ending Turn");
        const response = await fetch(`${server}/end-turn/${playerId}`);
        document.getElementById('dice-result').textContent = response['dice'];
        await updateResources();


    }catch(error){
        console.error("Failed to end turn");
    }
}

async function update(){
    try{
        await updateResources();
        const response = await fetch(`${server}/update/${playerId}`);
        document.getElementById('dice-result').textContent = response['game']['Roll'];
    }catch(error){
        console.error(error);
    }
}

async function updateResources(){
    try{
        console.log('updating resources');
        const response = await fetch(`${server}/update`);
        document.getElementById("brick_amount")=response.data["Brick"];
        document.getElementById("lumber_amount")=response.data["Wood"];
        document.getElementById("ore_amount")=response.data["Ore"];
        document.getElementById("grain_amount")=response.data["Wheat"];
        document.getElementById("wool_amount")=response.data["Sheep"];
        document.getElementById("wool_amount").textContent=5;
    }catch(error){
        console.error('Failed to update resources');
    }
}

