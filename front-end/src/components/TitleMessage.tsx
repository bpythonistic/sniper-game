import React, {JSX, useEffect, useState} from "react";
import { fetchMessage } from "../app/api";

const TitleMessage = (): JSX.Element => {
    const [message, setMessage] = useState("");
    const [username, setUsername] = useState("");

    useEffect(() => {
        // Fetch the message from the backend API
        fetchMessage()
            .then(data => {
                setMessage(data.message);
                setUsername(data.user.name);
            })
            .catch(error => console.error("Error fetching message:", error));
    }, []);
    return (
        <div className="text-center mt-8">
            <h1 className="text-4xl font-bold mb-4">{message}</h1>
            <p className="text-lg text-gray-600">Welcome, {username}!</p>
        </div>
    );
};

export default TitleMessage;
