"use client";
import ChatMessagesBox from "@/components/Chat/ChatMessagesBox";
import ChatInputBox from "@/components/Chat/ChatInputBox";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {axiosInstance} from "@/app/axios";
import moment from "moment";
import ChatSettings from "@/components/ChatSettings";
import {useRef} from "react";

function removeBrackets(str) {
    return str.replace(/[\[\](){}<>]/g, '');
}


export default function Chat() {

    const queryClient = useQueryClient();
    const settingFormRef = useRef(null);

    const apiEndpoint = "/tags";
    const {data: tagsData, isLoading, refetch} = useQuery({
        queryKey: [apiEndpoint],
        queryFn: async () => {
            const res = await axiosInstance.get(apiEndpoint);
            return res.data;
        }
    });

    const {data: messages} = useQuery({
        queryKey: ["messages"],
        queryFn: async () => {
            return queryClient.getQueryData(["messages"]) || [];
        }
    });


    const sendMessage = useMutation({
        mutationFn: async (messageRequest) => {
            const res = await axiosInstance.post("/generate", messageRequest);
            return res.data;
        }
    });

    const addMessage = useMutation({
        mutationFn: async (message) => {
            queryClient.setQueryData(["messages"], (prevMessages) => {
                return [...prevMessages, message];
            });
        }
    });

    const updateMessage = useMutation({
        mutationFn: async (message) => {
            queryClient.setQueryData(["messages"], (prevMessages) => {
                return prevMessages.map((msg) => {
                    if (msg.timestamp === message.timestamp) {
                        return message;
                    }
                    return msg;
                });
            });
        }
    });

    const updateLastMessage = useMutation({
        mutationFn: async (message) => {
            queryClient.setQueryData(["messages"], (prevMessages) => {
                const updatedLastMessage = { ...prevMessages[prevMessages.length - 1],
                    ...message };
                return [...prevMessages.slice(0, -1), updatedLastMessage];
            });
        }
    });

    function addMessageToChat(role, content, isLoading, rawMessage, error = null) {
        const timestamp = new Date().toISOString();
        const momentFormatted = moment().format('MMMM Do YYYY, h:mm:ss a');
        const message = {
            role,
            content,
            timestamp,
            rawMessage,
            loading: isLoading,
            moment: momentFormatted
        };
        if (error) {
            message.error = error;
        }
        addMessage.mutate(message);
    }

    // Function to handle the generation of the response and update the UI accordingly
    async function handleResponseGeneration(message) {
        if (!message) {
            return;
        }
         try {

            const  settingsForm = settingFormRef.current;
            const settingsValid = await settingsForm.validateSettings();
            if (!settingsValid) {
                return;
            }
            const model = queryClient.getQueryData(["selectedModel"]);
            let modelSettings = settingFormRef.current.getSettings();
            modelSettings = {
                temperature: parseFloat(modelSettings.temperature),
                candidateCount: parseInt(modelSettings.candidateCount),
                topK: parseInt(modelSettings.topK),
                topP: parseFloat(modelSettings.topP),
            }

            const messageRequest = {
                model,
                message,
                settings: modelSettings
            };

             // Add user message to chat
             addMessageToChat("user", removeBrackets(message), false, message);

             // Add initial model message to chat
             addMessageToChat("model", "Generating response...", true, message);



             const generationResponse = await sendMessage.mutateAsync(messageRequest);
            console.log("generation response", generationResponse);
            const candidateContent = generationResponse?.candidates[0]?.content;
            const updatedContent = candidateContent
                ? candidateContent.parts[0].text
                : "Sorry, I couldn't understand that. Can you please rephrase?";

            updateLastMessage.mutate({
                content: updatedContent,
                loading: false
            });
        } catch (e) {
            console.log("error in generating response", e);
            updateLastMessage.mutate({
                content: "Ups! Something went wrong. I cannot generate a response at the moment",
                loading: false,
                error: e
            });
        }
    }

    const onMessageSend = async (message, evt) => {
        // add user message to chat
        await handleResponseGeneration(message);
    }

    const clearChatQueueHandler = async () => {
        queryClient.setQueryData(["messages"], []);
    }
    return (
        <div className="flex flex-col lg:flex-row gap-3">
            <div className="w-full">
                <div
                    className="flex flex-col  rounded-xl bg-muted/50 p-1 border-2 h-screen lg:h-[calc(100vh-90px)] w-full m-0">
                    <div className="w-full h-dvh overflow-auto">
                        <ChatMessagesBox messages={messages} onClearChatQueue={clearChatQueueHandler}/>
                    </div>
                    <div className="w-full">
                        <ChatInputBox inputTags={tagsData} onMessageSend={onMessageSend} tagValueAccessor="name"/>
                    </div>
                </div>
            </div>
            <div>
                <ChatSettings ref={settingFormRef}/>
            </div>
        </div>
    )
}