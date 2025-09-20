import { ResponseFunctionWebSearch } from "openai/resources/responses/responses.mjs";
import React from "react";

import { FunctionCallMessage } from "./messages/FunctionCallMessage";
import { TextMessage } from "./messages/TextMessage";
import { WebSearchMessage } from "./messages/WebSearchMessage";
import { Message } from "@/types/legacy";

type MessageBubbleProps = {
  message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  switch (message.type) {
    case "function_call":
      return <FunctionCallMessage message={message} />;
    case "function_call_output":
      // already rendered in FunctionCall
      return null;
    case "file_search_call":
      return (
        <div className="flex flex-row gap-2 font-mono text-sm text-gray-500">
          file_search_call: {message.queries.join(", ")}
        </div>
      );
    case "message":
      if (Array.isArray(message.content)) {
        const content = message.content[0];
        if (content.type === "output_text") {
          const isUser = message.role === "user";
          return <TextMessage text={content.text} isUser={isUser} />;
        } else if (content.type === "refusal") {
          return null;
        }
      } else if (typeof message.content === "string") {
        const isUser = message.role === "user";
        const isAudio = (message as any).audio_data === "audio_received";
        return (
          <div>
            <TextMessage text={message.content} isUser={isUser} isAudio={isAudio} />
            {/* Display function calls if they exist */}
            {(message as any).function_calls && (message as any).function_calls.length > 0 && (
              <div className="mt-2">
                {(message as any).function_calls.map((funcCall: any, index: number) => (
                  <FunctionCallMessage 
                    key={index} 
                    message={{
                      ...funcCall,
                      type: "function_call",
                      name: funcCall.name,
                      arguments: funcCall.arguments
                    }} 
                  />
                ))}
              </div>
            )}
          </div>
        );
      }
      return null;
    case "web_search_call":
      return (
        <WebSearchMessage message={message as ResponseFunctionWebSearch} />
      );
    default:
      console.log("Unknown message type", message);
      return null;
  }
}
