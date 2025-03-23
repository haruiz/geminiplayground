// contexts/WebSocketContext.js
"use client";

import React, {createContext, useContext} from "react";
import useWebSocket, {ReadyState} from "react-use-websocket";

const WS_URL = `ws://${process.env.NEXT_PUBLIC_API_BASE_URL}/ws`;
const WebSocketContext = createContext(null);

export const WebSocketProvider = ({children}) => {
    const {
        sendJsonMessage,
        lastJsonMessage,
        readyState,
    } = useWebSocket(WS_URL, {
        share: true, // important: share connection across components
        shouldReconnect: () => true,
    });

    return (
        <WebSocketContext.Provider value={{sendJsonMessage, lastJsonMessage, readyState}}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocketContext = () => useContext(WebSocketContext);
