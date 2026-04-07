"use client";

import type { ThinkComponent } from "@thesysai/genui-sdk";

export const ExecutiveThinking: ThinkComponent = ({ thinkItems }) => {
  const latestItem = thinkItems[thinkItems.length - 1];

  return (
    <div className="udc-thinking">
      <div className="udc-thinking-bar" />
      <div className="udc-thinking-content">
        <div className="udc-thinking-title">
          {latestItem?.title || "Processing"}
        </div>
        {latestItem?.content && (
          <div className="udc-thinking-description">
            {latestItem.content}
          </div>
        )}
      </div>
    </div>
  );
};
