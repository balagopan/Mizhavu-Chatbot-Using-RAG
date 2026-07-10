

"use client"

import React, { useState, useEffect } from 'react'
import Header from '@/components/Header';
import InputBar from '@/components/InputBar';
import MessageArea from '@/components/MessageArea';
import { Message } from '@/types';

interface SearchInfo {
  stages: string[];
  query: string;
  urls: string[];
}

const Home = () => {
  // const [messages, setMessages] = useState<Message[]>([
  //   {
  //     id: 1,
  //     imageUrl: '/Chatbot_DP.jpg',
  //     isUser: false,
  //     type: 'message'
  //   },
  //   {
  //     id: 2,
  //     content: "Hello there! Welcome to the World of the Mizhavu.",
  //     isUser: false,
  //     type: 'message'
  //   },
  //   {
  //     id: 3,
  //     content: "My name is Mizhavu Ashan, and I will be your guide throug this exicting journey, where you will learn all about mizhavu instrument",
  //     isUser: false,
  //     type: 'message'
  //   },
  //   {
  //     id: 4,
  //     content: "Tell me how can I help you?",
  //     isUser: false,
  //     type: 'message'
  //   }
  // ]);

  const [messages, setMessages] = useState<Message[]>([
  { id: 1, imageUrl: '/Chatbot_DP.jpg', isUser: false, type: 'message' }
]);


  useEffect(() => {
    let isMounted = true;

    // These are your exact messages, just stored here so we can loop through them
    const initialMessages: Message[] = [
      { id: 2, content: "Hello there! Welcome to the World of the Mizhavu.", isUser: false, type: 'message' },
      { id: 3, content: "My name is Mizhavu Ashan, and I will be your guide throug this exicting journey, where you will learn all about mizhavu instrument", isUser: false, type: 'message' },
      { id: 4, content: "Tell me how can I help you?", isUser: false, type: 'message' }
    ];

    const loadInitialMessages = async () => {
      for (let i = 0; i < initialMessages.length; i++) {
        if (!isMounted) break;

        const msg = initialMessages[i];

        // 1. Show the loading animation
        setMessages(prev => [...prev, { ...msg, content: "", imageUrl: undefined, isLoading: true }]);

        // 2. Wait 1.2 seconds
        await new Promise(resolve => setTimeout(resolve, 600));

        if (!isMounted) break;

        // 3. Reveal the actual message
        setMessages(prev => prev.map(m => m.id === msg.id ? { ...msg, isLoading: false } : m));

        // 4. Tiny pause before the next message
        await new Promise(resolve => setTimeout(resolve, 400));
      }
    };

    loadInitialMessages();

    return () => { isMounted = false; };
  }, []);





  const [currentMessage, setCurrentMessage] = useState("");
  const [checkpointId, setCheckpointId] = useState(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (currentMessage.trim()) {
      // First add the user message to the chat
      const newMessageId = messages.length > 0 ? Math.max(...messages.map(msg => msg.id)) + 1 : 1;

      setMessages(prev => [
        ...prev,
        {
          id: newMessageId,
          content: currentMessage,
          isUser: true,
          type: 'message'
        }
      ]);

      const userInput = currentMessage;
      setCurrentMessage(""); // Clear input field immediately

      try {
        // Create AI response placeholder
        const aiResponseId = newMessageId + 1;
        setMessages(prev => [
          ...prev,
          {
            id: aiResponseId,
            content: "",
            isUser: false,
            type: 'message',
            isLoading: true,
            searchInfo: {
              stages: [],
              query: "",
              urls: []
            }
          }
        ]);

        // Create URL with checkpoint ID if it exists
        // let url = `https://agentic-ai-search-bot.onrender.com/chat/${encodeURIComponent(userInput)}`;
        let url = `/chat/${encodeURIComponent(userInput)}`;
        
        if (checkpointId) {
          url += `?checkpoint_id=${encodeURIComponent(checkpointId)}`;
        }

        // Connect to SSE endpoint using EventSource
        const eventSource = new EventSource(url);
        let streamedContent = "";
        let searchData: any = null;;
        let hasReceivedContent = false;

        // Process incoming messages
        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === 'checkpoint') {
              // Store the checkpoint ID for future requests
              setCheckpointId(data.checkpoint_id);
            }
            else if (data.type === 'content') {
              streamedContent += data.content;
              hasReceivedContent = true;

              // Update message with accumulated content
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === aiResponseId
                    ? { ...msg, content: streamedContent, isLoading: false }
                    : msg
                )
              );
            }
            else if (data.type === 'search_start') {
              // Create search info with 'searching' stage
              const newSearchInfo = {
                stages: ['searching'],
                query: data.query,
                urls: []
              };
              searchData = newSearchInfo;

              // Update the AI message with search info
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === aiResponseId
                    ? { ...msg, content: streamedContent, searchInfo: newSearchInfo, isLoading: false }
                    : msg
                )
              );
            }
            else if (data.type === 'search_results') {
              try {
                // Parse URLs from search results
                const urls = typeof data.urls === 'string' ? JSON.parse(data.urls) : data.urls;

                // Update search info to add 'reading' stage (don't replace 'searching')
                const newSearchInfo = {
                  stages: searchData ? [...searchData.stages, 'reading'] : ['reading'],
                  query: searchData?.query || "",
                  urls: urls
                };
                searchData = newSearchInfo;

                // Update the AI message with search info
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === aiResponseId
                      ? { ...msg, content: streamedContent, searchInfo: newSearchInfo, isLoading: false }
                      : msg
                  )
                );
              } catch (err) {
                console.error("Error parsing search results:", err);
              }
            }
            else if (data.type === 'search_error') {
              // Handle search error
              const newSearchInfo = {
                stages: searchData ? [...searchData.stages, 'error'] : ['error'],
                query: searchData?.query || "",
                error: data.error,
                urls: []
              };
              searchData = newSearchInfo;

              setMessages(prev =>
                prev.map(msg =>
                  msg.id === aiResponseId
                    ? { ...msg, content: streamedContent, searchInfo: newSearchInfo, isLoading: false }
                    : msg
                )
              );
            }
            else if (data.type === 'end') {
              // When stream ends, add 'writing' stage if we had search info
              if (searchData) {
                const finalSearchInfo = {
                  ...searchData,
                  stages: [...searchData.stages, 'writing']
                };

                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === aiResponseId
                      ? { ...msg, searchInfo: finalSearchInfo, isLoading: false }
                      : msg
                  )
                );
              }

              eventSource.close();
            }
          } catch (error) {
            console.error("Error parsing event data:", error, event.data);
          }
        };

        // Handle errors
        eventSource.onerror = (error) => {
          console.error("EventSource error:", error);
          eventSource.close();

          // Only update with error if we don't have content yet
          if (!streamedContent) {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === aiResponseId
                  ? { ...msg, content: "Sorry, there was an error processing your request.", isLoading: false }
                  : msg
              )
            );
          }
        };

        // Listen for end event
        eventSource.addEventListener('end', () => {
          eventSource.close();
        });
      } catch (error) {
        console.error("Error setting up EventSource:", error);
        setMessages(prev => [
          ...prev,
          {
            id: newMessageId + 1,
            content: "Sorry, there was an error connecting to the server.",
            isUser: false,
            type: 'message',
            isLoading: false
          }
        ]);
      }
    }
  };

  return (
    <div className="flex justify-center min-h-screen py-8 px-4 bg-[url('/Chatbot_Bg_2.jpg')] bg-cover bg-center bg-no-repeat bg-fixed relative">
      
      <div className="absolute top-2 left-4 md:top-2 md:left-6 z-10">
        <img 
          src="/logo.png"
          alt="Mizhavu Chatbot" 
          className="h-16 md:h-24 w-auto object-contain drop-shadow-md" 
        />
      </div>

      {/* Main container with refined shadow and border */}
      <div className="w-full max-w-xl flex flex-col h-[90vh] bg-transparent">
        <MessageArea messages={messages} />
        <InputBar currentMessage={currentMessage} setCurrentMessage={setCurrentMessage} onSubmit={handleSubmit} />
      </div>
    </div>
  );
};

export default Home;