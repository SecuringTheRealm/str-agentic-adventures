import { useState, useEffect, useRef, useCallback } from 'react';

export interface WebSocketMessage {
	type: string;
	[key: string]: any;
}

export interface UseWebSocketOptions {
	onMessage?: (message: WebSocketMessage) => void;
	onConnect?: () => void;
	onDisconnect?: () => void;
	onError?: (error: Event) => void;
	reconnectInterval?: number;
	maxReconnectAttempts?: number;
}

export const useWebSocket = (url: string, options: UseWebSocketOptions = {}) => {
	const [socket, setSocket] = useState<WebSocket | null>(null);
	const [isConnected, setIsConnected] = useState(false);
	const [isConnecting, setIsConnecting] = useState(false);
	const [error, setError] = useState<string | null>(null);
	
	const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
	const reconnectAttemptsRef = useRef(0);
	const shouldReconnectRef = useRef(true);
	
	const {
		onMessage,
		onConnect,
		onDisconnect,
		onError,
		reconnectInterval = 3000,
		maxReconnectAttempts = 5
	} = options;

	const connect = useCallback(() => {
		if (socket?.readyState === WebSocket.OPEN || isConnecting) {
			return;
		}

		setIsConnecting(true);
		setError(null);

		try {
			const ws = new WebSocket(url);

			ws.onopen = () => {
				setIsConnected(true);
				setIsConnecting(false);
				setError(null);
				reconnectAttemptsRef.current = 0;
				
				if (onConnect) {
					onConnect();
				}
			};

			ws.onmessage = (event) => {
				try {
					const message = JSON.parse(event.data);
					if (onMessage) {
						onMessage(message);
					}
				} catch (err) {
					console.error('Failed to parse WebSocket message:', err);
				}
			};

			ws.onclose = (event) => {
				setIsConnected(false);
				setIsConnecting(false);
				
				if (onDisconnect) {
					onDisconnect();
				}

				// Attempt to reconnect if not manually closed
				if (shouldReconnectRef.current && 
					reconnectAttemptsRef.current < maxReconnectAttempts) {
					
					reconnectAttemptsRef.current++;
					reconnectTimeoutRef.current = setTimeout(() => {
						connect();
					}, reconnectInterval);
				}
			};

			ws.onerror = (event) => {
				setError('WebSocket connection error');
				setIsConnecting(false);
				
				if (onError) {
					onError(event);
				}
			};

			setSocket(ws);
		} catch (err) {
			setError('Failed to create WebSocket connection');
			setIsConnecting(false);
		}
	}, [url, onConnect, onMessage, onDisconnect, onError, reconnectInterval, maxReconnectAttempts]);

	const disconnect = useCallback(() => {
		shouldReconnectRef.current = false;
		
		if (reconnectTimeoutRef.current) {
			clearTimeout(reconnectTimeoutRef.current);
		}
		
		if (socket) {
			socket.close();
			setSocket(null);
		}
		
		setIsConnected(false);
		setIsConnecting(false);
	}, [socket]);

	const sendMessage = useCallback((message: WebSocketMessage) => {
		if (socket?.readyState === WebSocket.OPEN) {
			socket.send(JSON.stringify(message));
			return true;
		}
		return false;
	}, [socket]);

	// Connect on mount
	useEffect(() => {
		connect();
		
		return () => {
			shouldReconnectRef.current = false;
			if (reconnectTimeoutRef.current) {
				clearTimeout(reconnectTimeoutRef.current);
			}
			if (socket) {
				socket.close();
			}
		};
	}, [connect]);

	// Cleanup on unmount
	useEffect(() => {
		return () => {
			disconnect();
		};
	}, [disconnect]);

	return {
		socket,
		isConnected,
		isConnecting,
		error,
		connect,
		disconnect,
		sendMessage,
		reconnectAttempts: reconnectAttemptsRef.current
	};
};