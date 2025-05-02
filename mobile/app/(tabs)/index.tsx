import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, View, Text, Button, ScrollView, Alert, ActivityIndicator, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import Constants from 'expo-constants';

// IMPORTANT: Replace with your backend server address
// Android Emulator: 'http://10.0.2.2:8000'
// iOS Simulator: 'http://localhost:8000'
// Physical device: 'http://<YOUR_MACHINE_LOCAL_IP>:8000'
// const serverUrl = 'http://127.0.0.1:8000'; // <-- CHANGE THIS IF NEEDED
const rawHost =
  Constants.expoConfig?.hostUri?.split(':')[0] ??
  Constants.manifest?.debuggerHost?.split(':')[0] ??
  'localhost';

// export const serverUrl = `http://${rawHost}:8000`;
export const serverUrl = 'http://172.17.35.114:8000';

interface Player {
    id: number;
    victoryPoints: number;
    hand: Resources;
    cards: DevCards;
}

interface Resources {
    lumber: number;
    wool: number;
    grain: number;
    brick: number;
    ore: number;
}

interface DevCards {
    '0': number; // Knight
    '1': number; // Point
    '2': number; // Road Building
    '3': number; // Year of Plenty
    '4': number; // Monopoly
}

const initialResources: Resources = { lumber: 0, wool: 0, grain: 0, brick: 0, ore: 0 };
const initialDevCards: DevCards = { '0': 0, '1': 0, '2': 0, '3': 0, '4': 0 };

const resourceIndexToName: { [key: number]: keyof Resources } = {
    0: 'lumber', // Assuming 0 is lumber/wood based on game.js
    1: 'wool',   // Assuming 1 is wool/sheep
    2: 'grain',  // Assuming 2 is grain/wheat
    3: 'brick',
    4: 'ore'
};

const resourceNameToIndex = (name: string): number | undefined => {
    const map: { [key: string]: number } = {
        "wood": 0, "lumber": 0,
        "sheep": 1, "wool": 1,
        "wheat": 2, "grain": 2,
        "brick": 3,
        "ore": 4
    };
    return map[name?.toLowerCase()];
};


export default function GameScreen() {
    const [playerId, setPlayerId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [diceRoll, setDiceRoll] = useState<string>('--');
    const [players, setPlayers] = useState<Player[]>([]);
    const [myResources, setMyResources] = useState<Resources>(initialResources);
    const [myDevCards, setMyDevCards] = useState<DevCards>(initialDevCards);
    const [isMyTurn, setIsMyTurn] = useState<boolean>(false); // Basic turn tracking

    const loadPlayerId = useCallback(async () => {
        try {
            const storedId = await AsyncStorage.getItem('playerId');
            if (storedId) {
                setPlayerId(storedId);
                fetchGameInfo(storedId); // Fetch initial game info if ID exists
            } else {
                setIsLoading(false); // No ID, stop loading, show join button
            }
        } catch (e) {
            setError("Failed to load player ID from storage.");
            setIsLoading(false);
        }
    }, []); // Add fetchGameInfo when defined

    useEffect(() => {
        loadPlayerId();
    }, [loadPlayerId]);


    const handleApiResponse = async (response: Response, actionDesc: string) => {
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to ${actionDesc}: ${response.status} ${errorText}`);
        }
        return response.json();
    };

    const fetchGameInfo = useCallback(async (currentId: string | null = playerId) => {
         if (!currentId) return;
         console.log("Fetching game info...");
         // setIsLoading(true); // Indicate loading for refresh
         setError(null);
         try {
             const response = await fetch(`${serverUrl}/game-info`);
             const data = await handleApiResponse(response, "fetch game info");

             setDiceRoll(data.roll ?? '--');
             setPlayers(data.players ?? []);
             setIsMyTurn(data.players?.find((p: Player) => p.id.toString() === currentId)?.id === data.currentPlayerId); // Example: Check if backend sends current player ID

             // Find current player's data
             const me = data.players?.find((p: Player) => p.id.toString() === currentId);
             if (me) {
                 setMyResources(me.hand ?? initialResources);
                 setMyDevCards(me.cards ?? initialDevCards);
             } else {
                 // This might happen if player just joined and game hasn't fully updated
                 console.warn("Current player data not found in game info.");
                 setMyResources(initialResources);
                 setMyDevCards(initialDevCards);
                 // Optionally clear player ID if consistently not found?
                 // await AsyncStorage.removeItem('playerId');
                 // setPlayerId(null);
                 // setError("Couldn't find your player data. Please try joining again.");
             }
         } catch (err: any) {
             setError(`Error fetching game data: ${err.message}`);
             console.error("Fetch game info error:", err);
         } finally {
            // If we set loading true at start, set it false here
            // setIsLoading(false);
         }
     }, [playerId]); // Dependency on playerId

    const joinGame = async () => {
        console.log("Attempting to join game...");
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`${serverUrl}/join-game`);
            const data = await handleApiResponse(response, "join game");

            if (data.id !== undefined) {
                const newPlayerId = data.id.toString();
                await AsyncStorage.setItem('playerId', newPlayerId);
                setPlayerId(newPlayerId);
                await fetchGameInfo(newPlayerId); // Fetch info immediately after join
            } else {
                throw new Error("No player ID received from server.");
            }
        } catch (err: any) {
            setError(`Failed to join game: ${err.message}`);
            Alert.alert("Error", `Failed to join game: ${err.message}`);
            console.error("Join game error:", err);
        } finally {
            setIsLoading(false);
        }
    };

    // --- Action Handlers ---
    const makeApiCall = useCallback(async (endpoint: string, actionDesc: string) => {
        if (!playerId) {
            Alert.alert("Error", "Player ID not found.");
            return;
        }
        setError(null);
        try {
            const response = await fetch(`${serverUrl}/${endpoint}/${playerId}`);
            const result = await handleApiResponse(response, actionDesc);
            console.log(`${actionDesc} result:`, result);
            Alert.alert("Success", `${actionDesc} successful.`);
            await fetchGameInfo(); // Refresh game state
        } catch (err: any) {
            setError(`Error during ${actionDesc}: ${err.message}`);
            Alert.alert("Error", `Failed to ${actionDesc}: ${err.message}`);
            console.error(`${actionDesc} error:`, err);
        }
    }, [playerId, fetchGameInfo]); // Dependencies

    const handleBuildRoad = () => makeApiCall('build-road', 'Build Road');
    const handleBuildSettlement = () => makeApiCall('build-house', 'Build Settlement'); // Assuming 'build-house' endpoint
    const handleBuildCity = () => makeApiCall('build-city', 'Build City');
    const handleBuyDevCard = () => makeApiCall('buy-dev-card', 'Buy Development Card');
    const handleEndTurn = () => makeApiCall('end-turn', 'End Turn');

    const handleUseDevCard = async (card: number) => {
        if (!playerId) return;

        let args: number[] = [];
        let url = `${serverUrl}/use-dev-card/${card}/${playerId}`;

        try {
            if (card === 3) { // Year of Plenty
                const r1Name = await new Promise<string | undefined>((resolve) => Alert.prompt("Year of Plenty", "Choose first resource (brick, lumber, ore, grain, wool):", text => resolve(text)));
                const r2Name = await new Promise<string | undefined>((resolve) => Alert.prompt("Year of Plenty", "Choose second resource:", text => resolve(text)));
                const r1Index = resourceNameToIndex(r1Name || '');
                const r2Index = resourceNameToIndex(r2Name || '');
                if (r1Index === undefined || r2Index === undefined) {
                    Alert.alert("Error", "Invalid resource name(s) entered.");
                    return;
                }
                args = [r1Index, r2Index];
            } else if (card === 4) { // Monopoly
                const resName = await new Promise<string | undefined>((resolve) => Alert.prompt("Monopoly", "Choose resource to monopolize:", text => resolve(text)));
                const resIndex = resourceNameToIndex(resName || '');
                if (resIndex === undefined) {
                    Alert.alert("Error", "Invalid resource name entered.");
                    return;
                }
                args = [resIndex];
            }

            if (args.length > 0) {
                url += `?args=${args.join(",")}`;
            }

            const response = await fetch(url); // Assuming GET request based on game.js
            const result = await handleApiResponse(response, `Use Dev Card ${card}`);
            console.log("Use dev card result:", result);
            Alert.alert("Success", `Development card used.`);
            await fetchGameInfo(); // Refresh state

        } catch (err: any) {
             setError(`Error using dev card: ${err.message}`);
             Alert.alert("Error", `Failed to use dev card: ${err.message}`);
             console.error("Use dev card error:", err);
        }
    };


    // --- Render Logic ---
    if (isLoading && !playerId) { // Show loading only on initial ID check
      return <View style={styles.centered}><ActivityIndicator size="large" /></View>;
    }

    if (!playerId) {
      return (
        <View style={styles.centered}>
          <ThemedText type="title">Welcome!</ThemedText>
          {error && <Text style={styles.errorText}>{error}</Text>}
          <Button title="Join Game" onPress={joinGame} disabled={isLoading} />
          {isLoading && <ActivityIndicator />}
        </View>
      );
    }

    // Main Game View
    return (
        <ScrollView style={styles.container}>
            {error && <Text style={styles.errorText}>{error}</Text>}

            <ThemedView style={[styles.section, { marginTop: 70 }]}>
                <ThemedText style={styles.topHeader}>Player Info</ThemedText>
                <Text>You are Player {playerId}</Text>
                <Text>Status: {isMyTurn ? 'Your Turn' : 'Waiting...'}</Text>
                 <Button title="Refresh Game Info" onPress={() => fetchGameInfo()} />
            </ThemedView>

            <ThemedView style={styles.section}>
                <ThemedText style={styles.header}>Dice Roll</ThemedText>
                <Text style={styles.diceResult}>{diceRoll}</Text>
            </ThemedView>

            <ThemedView style={styles.section}>
                <ThemedText style={styles.header}>Players</ThemedText>
                {players.map(p => (
                    <Text key={p.id}>Player {p.id} - VP: {p.victoryPoints}</Text>
                ))}
            </ThemedView>

            <ThemedView style={styles.section}>
                <ThemedText style={styles.header}>Your Resources</ThemedText>
                <View style={styles.resourcesGrid}>
                    {(Object.keys(myResources) as Array<keyof Resources>).map(key => (
                        <View key={key} style={styles.resourceBox}>
                           <Text style={styles.resourceText}>{key.charAt(0).toUpperCase() + key.slice(1)}: {myResources[key]}</Text>
                        </View>
                    ))}
                </View>
                 {/* <Button title="Trade 4:1 (Not Implemented)" onPress={() => Alert.alert("Info", "Trade not implemented")} /> */}
            </ThemedView>

            <ThemedView style={styles.section}>
                <ThemedText style={styles.header}>Actions</ThemedText>
                <View style={styles.buttonGrid}>
                    <Button title="Build Road" onPress={handleBuildRoad} />
                    <Button title="Build Settlement" onPress={handleBuildSettlement} />
                    <Button title="Build City" onPress={handleBuildCity} />
                    <Button title="Buy Dev Card" onPress={handleBuyDevCard} />
                    <Button title="End Turn" onPress={handleEndTurn} /*disabled={!isMyTurn}*/ />
                 </View>
            </ThemedView>

             <ThemedView style={styles.section}>
                 <ThemedText style={styles.header}>Development Cards</ThemedText>
                 <View style={styles.buttonGrid}>
                     <Button
                         title={`Knight (${myDevCards['0']})`}
                         disabled={myDevCards['0'] === 0}
                         onPress={() => handleUseDevCard(0)}
                     />
                      <Button
                         title={`Point (${myDevCards['1']})`}
                         disabled={true} // Always disabled
                     />
                      <Button
                         title={`Road Building (${myDevCards['2']})`}
                         disabled={myDevCards['2'] === 0}
                         onPress={() => handleUseDevCard(2)}
                     />
                      <Button
                         title={`Year of Plenty (${myDevCards['3']})`}
                         disabled={myDevCards['3'] === 0}
                         onPress={() => handleUseDevCard(3)}
                     />
                      <Button
                         title={`Monopoly (${myDevCards['4']})`}
                         disabled={myDevCards['4'] === 0}
                         onPress={() => handleUseDevCard(4)}
                     />
                 </View>
             </ThemedView>

        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 10,
    },
    centered: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    section: {
        marginBottom: 20,
        padding: 10,
        borderWidth: 1,
        borderColor: '#ccc',
        borderRadius: 5,
        // Use ThemedView's background or define one here
        // backgroundColor: '#f9f9f9',
    },
    topHeader: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    header: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    errorText: {
        color: 'red',
        marginBottom: 10,
        textAlign: 'center',
    },
    diceResult: {
        fontSize: 24,
        fontWeight: 'bold',
        textAlign: 'center',
    },
    resourcesGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-around', // Or 'flex-start'
        marginBottom: 10,
    },
     resourceBox: {
        backgroundColor: '#e0e0e0', // Light grey background
        paddingVertical: 8,
        paddingHorizontal: 12,
        borderRadius: 4,
        margin: 4, // Add some margin around each box
        minWidth: 80, // Ensure minimum width
        alignItems: 'center', // Center text inside
    },
    resourceText: {
      fontSize: 14,
    },
    buttonGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'center', // Center buttons horizontally
        gap: 10, // Add gap between buttons
    },
    // Add any other styles needed, potentially reusing styles from the original ParallaxScrollView example if desired
});
