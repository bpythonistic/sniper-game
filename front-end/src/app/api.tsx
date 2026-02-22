import React, { useEffect, useState } from 'react';

const apiUrl = 'http://127.0.0.1:8000';
const defaultHeaders = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': 'http://127.0.0.1:5173',
};
export const websocketUrl = 'ws://127.0.0.1:8000/ws/scope';

export const fetchMessage = async (): Promise<{
  message: string;
  user: { name: string };
}> => {
  try {
    const response = await fetch(apiUrl, {
      headers: defaultHeaders,
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching message:', error);
    return { message: 'Error fetching message', user: { name: 'Guest' } };
  }
};

export const createUser = async (
  name: string,
): Promise<{ success: boolean; user: { id: string; name: string } | null }> => {
  try {
    const response = await fetch(apiUrl + '/create_user', {
      method: 'POST',
      headers: {
        ...defaultHeaders,
      },
      body: JSON.stringify({ name }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return { success: true, user: data.user };
  } catch (error) {
    console.error('Error creating user:', error);
    return { success: false, user: null };
  }
};

export const fetchUser = async (
  name: string,
): Promise<{ success: boolean; user: { id: string; name: string } | null }> => {
  try {
    const response = await fetch(apiUrl + `/users/`, {
      headers: defaultHeaders,
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const user = data.find((u: any) => u.name === name);
    return { success: true, user: user || null };
  } catch (error) {
    console.error('Error fetching user:', error);
    return { success: false, user: null };
  }
};

export const createScope = async (
  user: { id: string; name: string },
  frequency: number,
  amplitude: number,
  phase: number = 0.0,
): Promise<{ success: boolean; scope: any }> => {
  try {
    const response = await fetch(apiUrl + '/create_scope', {
      method: 'POST',
      headers: {
        ...defaultHeaders,
      },
      body: JSON.stringify({
        user: user,
        frequency: frequency,
        amplitude: amplitude,
        phase: phase,
      }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return { success: true, scope: data };
  } catch (error) {
    console.error('Error creating scope:', error);
    return { success: false, scope: null };
  }
};

export const fetchScope = async (userId: string): Promise<{ success: boolean; scope: any }> => {
  try {
    const response = await fetch(apiUrl + `/scopes/`, {
      headers: defaultHeaders,
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const scope = data.find((s: any) => s.user.id === userId);
    return { success: true, scope: scope || null };
  } catch (error) {
    console.error('Error fetching scope:', error);
    return { success: false, scope: null };
  }
};

export const renderScopeWebSocket = (
  scopeId: string,
  onData: (data: any) => void,
  onError: (error: any) => void,
) => {
  const ws = new WebSocket(websocketUrl + `/${scopeId}`, 'json');
  ws.onopen = () => {
    console.log('WebSocket connection opened');
  };
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onData(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      onError(error);
    }
  };
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    onError(error);
  };
  ws.onclose = () => {
    console.log('WebSocket connection closed');
  };
  return ws;
};
