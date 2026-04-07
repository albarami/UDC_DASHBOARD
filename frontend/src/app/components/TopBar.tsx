"use client";

import { useEffect, useState } from "react";

export function TopBar() {
  const [dateStr, setDateStr] = useState<string>("");

  useEffect(() => {
    const now = new Date();
    const formatted = now.toLocaleDateString("en-GB", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    setDateStr(formatted);
  }, []);

  return (
    <div className="udc-topbar">
      <div className="udc-topbar-left">
        <span className="udc-brand">UDC</span>
        <span className="udc-divider">|</span>
        <span className="udc-subtitle">Executive Dashboard</span>
      </div>
      <div className="udc-topbar-right">
        <span className="udc-date">{dateStr}</span>
      </div>
    </div>
  );
}
