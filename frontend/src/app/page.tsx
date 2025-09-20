"use client";

import AudioChat from "@/features/audio/components/AudioChat";
import { useAudio } from "@/features/audio/hooks/useAudio";
import { ChatHistory } from "@/features/chat/components/ChatDialog";
import { FunctionsPanel } from "@/features/chat/components/FunctionsPanel";
import { useWebsocket } from "@/features/chat/hooks/useWebsocket";
import { Composer, Header, LanguageSelector } from "@/features/ui";
import { useState } from "react";

import "./styles.css";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [isProcessingAudio, setIsProcessingAudio] = useState(false);
  const [isFunctionsPanelOpen, setIsFunctionsPanelOpen] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState("en");

  const {
    isReady: audioIsReady,
    playAudio,
    startRecording,
    stopRecording,
    stopPlaying,
    frequencies,
    playbackFrequencies,
    microphoneError,
    retryMicrophoneAccess,
  } = useAudio();
  const {
    isReady: websocketReady,
    sendAudioMessage,
    sendTextMessage,
    history: messages,
    resetHistory,
    isLoading,
    agentName,
  } = useWebsocket({
    onNewAudio: playAudio,
  });

  function handleSubmit() {
    setPrompt("");
    sendTextMessage(prompt);
  }

  async function handleStopPlaying() {
    await stopPlaying();
  }

  function handleAudioMessage(audio: Int16Array<ArrayBuffer>) {
    setIsProcessingAudio(true);
    sendAudioMessage(audio);
    // Reset processing state after a delay
    setTimeout(() => setIsProcessingAudio(false), 10000);
  }

  return (
    <div className="w-full h-dvh flex flex-col items-center relative">
      {/* Functions Panel */}
      <FunctionsPanel 
        isOpen={isFunctionsPanelOpen} 
        onToggle={() => setIsFunctionsPanelOpen(!isFunctionsPanelOpen)} 
      />
      
      {/* Language Selector */}
      <div className="absolute top-4 right-4 z-50">
        <LanguageSelector 
          currentLanguage={currentLanguage}
          onLanguageChange={setCurrentLanguage}
        />
      </div>
      
      <Header
        agentName={agentName ?? ""}
        playbackFrequencies={playbackFrequencies}
        stopPlaying={handleStopPlaying}
        resetConversation={resetHistory}
      />
      <ChatHistory messages={messages} isLoading={isLoading} isProcessingAudio={isProcessingAudio} />
      <Composer
        prompt={prompt}
        setPrompt={setPrompt}
        onSubmit={handleSubmit}
        isLoading={isLoading}
        audioChat={
          <AudioChat
            frequencies={frequencies}
            isReady={websocketReady && audioIsReady}
            startRecording={startRecording}
            stopRecording={stopRecording}
            sendAudioMessage={handleAudioMessage}
            microphoneError={microphoneError}
            retryMicrophoneAccess={retryMicrophoneAccess}
          />
        }
      />
    </div>
  );
}
