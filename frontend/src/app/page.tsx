"use client";

import { C1Chat } from "@thesysai/genui-sdk";
import { themePresets } from "@crayonai/react-ui";
import { ExecutiveThinking } from "./components/ExecutiveThinking";

export default function Home() {
  return (
    <C1Chat
      apiUrl="/api/chat"
      formFactor="full-page"
      agentName="UDC Executive Dashboard"
      theme={{ ...themePresets.carbon, mode: "dark" }}
      customizeC1={{
        enableArtifactEdit: true,
        thinkComponent: ExecutiveThinking,
      }}
    />
  );
}
