"use client";

import { C1Chat, ThemeProvider } from "@thesysai/genui-sdk";
import { themePresets } from "@crayonai/react-ui";

const udcDarkTheme = {
  ...themePresets.carbon.darkTheme,
  backgroundFills: "#0a0f1a",
  containerFills: "#111827",
  sunkFills: "#0d1117",
  sunkBgFills: "#080c14",
  elevatedFills: "#1a2332",
  overlayFills: "rgba(0, 0, 0, 0.7)",
  strokeDefault: "#1f2937",
  strokeInteractiveEl: "#2d3748",
  strokeInteractiveElSelected: "#c9a961",
  strokeEmphasis: "#374151",
  strokeAccent: "#c9a961",
  strokeAccentEmphasis: "#d4af37",
  primaryText: "#f5f5f7",
  secondaryText: "#9ca3af",
  disabledText: "#4b5563",
  linkText: "#c9a961",
  brandText: "#c9a961",
  brandSecondaryText: "#a88b4a",
  accentPrimaryText: "#c9a961",
  successPrimaryText: "#10b981",
  alertPrimaryText: "#f59e0b",
  dangerPrimaryText: "#ef4444",
  dangerFills: "rgba(239, 68, 68, 0.12)",
  successFills: "rgba(16, 185, 129, 0.12)",
  alertFills: "rgba(245, 158, 11, 0.12)",
  infoFills: "rgba(59, 130, 246, 0.12)",
  interactiveDefault: "#1f2937",
  interactiveHover: "#2d3748",
  interactivePressed: "#374151",
  interactiveAccent: "#c9a961",
  interactiveAccentHover: "#d4af37",
  brandElFills: "#c9a961",
  brandElHoverFills: "#d4af37",
  chatContainerBg: "#0a0f1a",
  chatAssistantResponseBg: "#111827",
  chatUserResponseBg: "#1a2332",
  chatAssistantResponseText: "#f5f5f7",
  chatUserResponseText: "#f5f5f7",
  highlightSubtle: "rgba(201, 169, 97, 0.08)",
  highlightStrong: "rgba(201, 169, 97, 0.16)",
  roundedS: "8px",
  roundedM: "10px",
  roundedL: "12px",
  roundedClickable: "10px",
  fontHeadingLarge: "700 28px/1.2 'Inter', sans-serif",
  fontHeadingLargeLetterSpacing: "-0.02em",
  fontHeadingMedium: "600 20px/1.3 'Inter', sans-serif",
  fontHeadingMediumLetterSpacing: "-0.015em",
  fontHeadingSmall: "600 16px/1.4 'Inter', sans-serif",
  fontHeadingSmallLetterSpacing: "-0.01em",
  fontBody: "400 15px/1.6 'Inter', sans-serif",
  fontBodySmall: "400 13px/1.5 'Inter', sans-serif",
  fontBodyHeavy: "600 15px/1.6 'Inter', sans-serif",
  fontLabel: "500 13px/1.4 'Inter', sans-serif",
  fontLabelSmall: "500 11px/1.3 'Inter', sans-serif",
  fontLabelHeavy: "600 13px/1.4 'Inter', sans-serif",
};

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

function getFormattedDate(): string {
  return new Date().toLocaleDateString("en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export default function Dashboard() {
  return (
    <ThemeProvider
      theme={themePresets.carbon.theme}
      darkTheme={udcDarkTheme}
      mode="dark"
    >
      <C1Chat
        apiUrl="/api/chat"
        formFactor="full-page"
        agentName="UDC Executive Dashboard"
        disableThemeProvider
        welcomeMessage={{
          title: `${getGreeting()}.`,
          description: `${getFormattedDate()} — United Development Company`,
        }}
        conversationStarters={{
          variant: "long",
          options: [
            {
              displayText: "Morning briefing",
              prompt: "Good morning — how are we doing?",
            },
            {
              displayText: "What needs my attention",
              prompt: "What needs my attention today?",
            },
            {
              displayText: "Commercial leasing",
              prompt: "Show me our commercial leasing performance",
            },
            {
              displayText: "Financial position",
              prompt: "How is our cash position and who owes us money?",
            },
            {
              displayText: "Operations & satisfaction",
              prompt: "Are tenants happy? How is maintenance performing?",
            },
            {
              displayText: "Struggling assets",
              prompt: "Which assets are struggling the most?",
            },
          ],
        }}
        customizeC1={{
          enableArtifactEdit: true,
        }}
      />
    </ThemeProvider>
  );
}
