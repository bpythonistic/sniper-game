import React, { useEffect, useState } from "react";

const apiUrl = "http://127.0.0.1:8000";
const defaultHeaders = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "http://127.0.0.1:5173",
};

export const fetchMessage = async (): Promise<{
    message: string;
    user: { name: string };
}> => {
    try {
        const response = await fetch(
            apiUrl,
            {
                headers: defaultHeaders,
            },
        );
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching message:", error);
        return { message: "Error fetching message", user: { name: "Guest" } };
    }
};

export const createUser = async (
    name: string,
): Promise<{ success: boolean; user: { id: number; name: string } | null }> => {
    try {
        const response = await fetch(
            apiUrl + "/create_user",
            {
                method: "POST",
                headers: {
                    ...defaultHeaders,
                },
                body: JSON.stringify({ name }),
            },
        );
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return { success: true, user: data.user };
    } catch (error) {
        console.error("Error creating user:", error);
        return { success: false, user: null };
    }
};
